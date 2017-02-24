import re
import six

from abc import ABCMeta, abstractproperty

from ..api import Block, Location
from .exceptions import ConfigBuilderException


@six.add_metaclass(ABCMeta)
class Navigable(object):
    """ Indicates that a class is navigable.

    This means that it references some type of nginx config machinery,
    and that this is traversable.

    """
    _config_builder = None

    def __init__(self, *args, **kwargs):
        """ Creates a new Navigable class

        :param nginx.builder.ConfigBuilder config_builder: internal ConfigBuilder used to create nginx config objs
        """
        # This can sometimes be added by direct access,
        # in the case of plugins
        self._config_builder = kwargs.get('config_builder', None)
        self._parent = kwargs.get('parent', None)

    def chobj(self, obj):
        """ Changes the current working object to the one provided.

        :param nginx.config.Block obj: object that we're scoping to
        """
        self.config_builder._cwo = obj

    @property
    def current_obj(self):
        """ Returns the current working object.

        :returns nginx.config.Block: object that we're currently scoped to
        """
        return self.config_builder._cwo

    @property
    def config_builder(self):
        """ Internal config builder.

        :returns nginx.builder.ConfigBuilder: the internal ConfigBuilder for manipulating the nginx config
        """
        return self._config_builder

    def up(self):
        """ Traverse up the config hierarchy """
        self.chobj(self.current_obj.parent)

    def add_child(self, child):
        """ Adds a child to the config object

        :param nginx.config.Builder child: child to insert into config tree
        """
        name = re.split(r'\s+', self.current_obj.name)[0]
        if self.valid_cfg_parents and name not in self.valid_cfg_parents:
            raise ConfigBuilderException(
                '{parent} is not a valid parent for this plugin. Call this off of one of these: {valid_parents}'.format(
                    parent=name if name else 'top',
                    valid_parents=self.valid_cfg_parents
                ), plugin=self._get_name()
            )

        self.current_obj.sections.add(child)

    def __getattr__(self, attr):
        return getattr(self.config_builder, attr)

    @abstractproperty
    def valid_cfg_parents(self):
        return None

    @property
    def parent(self):
        return self._parent

    def _get_name(self):
        return getattr(self, 'name', self.current_obj.name)


@six.add_metaclass(ABCMeta)
class Plugin(Navigable):
    """ Plugin base class. All plugins must inherit from this

    Defines a few properties that must be defined:

    name - name of the plugin. must be unique per config builder
    exported_methods - dict of method names -> callables. method names don't need to match
        callables. exported method names must be unique
    """

    @abstractproperty
    def name(self):
        return ''

    @abstractproperty
    def exported_methods(self):
        return {}

    @property
    def http(self):
        return self.config_builder._http

    def __str__(self):
        return self.name


@six.add_metaclass(ABCMeta)
class Endable(Navigable):
    """ Role that adds an `end` convenience method to close scoped blocks (location, server, et al) """

    def end(self):
        self.up()
        return self.config_builder


@six.add_metaclass(ABCMeta)
class Routable(Navigable):
    """ A thing that can have routes attached to it.

    In nginx, routes can either be attached to server blocks or other routes

    """

    def add_route(self, path, **kwargs):
        loc = Location(path, **kwargs)
        self.add_child(loc)
        self.chobj(loc)

        return RouteWrapper(self.current_obj, self.config_builder)


@six.add_metaclass(ABCMeta)
class Wrapper(object):
    def __getattr__(self, attr):
        return getattr(self.config_builder, attr)


class RouteWrapper(Routable, Wrapper, Endable):
    """ This needs to wrap routes emitted by this interface since we can nest routes in nginx configs.

    This also enables users to use the returned routes/servers as a context manager, so that we can
    sugar-coat syntax even more than we already do

    """
    valid_cfg_parents = ('server', 'location')

    def __init__(self, wrapped, config_builder):
        super(RouteWrapper, self).__init__(
            parent=wrapped,
            config_builder=config_builder
        )

    def __enter__(self):
        return self

    def __exit__(self, typ, val, tb):
        self.end()


class RoutePlugin(Plugin, Routable, Endable):
    """ A plugin that creates routes

    Routes can be nested infinitely.

    Must be called off of either a server or a location block
    """
    name = 'route'
    valid_cfg_parents = ('location', 'server')

    @property
    def exported_methods(self):
        return {
            'add_route': self.add_route,
        }


class ServerPlugin(Plugin, Routable, Endable):
    """ A plugin that creates server blocks

    Must only be called off of an http block
    """
    name = 'server'
    valid_cfg_parents = ('http',)

    # XXX: add more server options
    def add_server(self, hostname='_', **kwargs):
        server = Block('server', server_name=hostname, **kwargs)
        self.add_child(server)
        self.chobj(server)

        return RouteWrapper(self.current_obj, self.config_builder)

    @property
    def exported_methods(self):
        return {
            'add_server': self.add_server,
            'end': self.end
        }
