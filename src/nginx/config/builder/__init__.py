"""
The Builder API defines a pluggable builder framework for manipulating nginx configs from within python.

Building a config
=================

Every config built using the builder pattern starts off with creating a :class:NginxConfigBuilder::

    from nginx.config.builder import NginxConfigBuilder

    nginx = NginxConfigBuilder()

By default, this comes loaded with a bunch of helpful tools to easily create routes and servers
in nginx::

    with nginx.add_server() as server:
        server.add_route('/foo').end()
        with server.add_route('/bar') as bar:
             bar.add_route('/baz')

This generates a simple config that looks like this::

    error_log logs/nginx.error.log;
    worker_processes auto;
    daemon on;
    http {
        include ../conf/mime.types;
        server {
            server_name _;
            location /foo {
            }
            location /bar {
                location /baz {
                }
            }
        }
    }
    events {
        worker_connections 1024;
    }

Plugins
=======

A plugin is a class that inherits from :class:`nginx.config.builder.baseplugins.Plugin` that provides
additional methods which can be chained off of the :class:`NginxConfigBuilder` object. These plugins provide
convenience methods that manipulate the underlying nginx configuration that gets built by the
:class:`NginxConfigBuilder`.

A simple plugin only needs to define what methods it's going to export::

    class NoopPlugin(Plugin):
        name = 'noop'

        @property
        def exported_methods(self):
             return {'noop': self.noop}

        def noop(self):
             pass

This NoopPlugin provides a simple function that can be called off of a :class:`NginxConfigBuilder` that
does nothing successfully. More complex plugins can be found in :mod:`nginx.config.builder.plugins`

To use this NoopPlugin, we need to create a config builder and then register the plugin with it::

    nginx = NginxConfigBuilder()
    nginx.noop()  # AttributeError :(
    nginx.register_plugin(NoopPlugin())
    nginx.noop()  # it works!

A more complex plugin would actually do something, like a plugin that adds an expiry directive to
a route::

    class ExpiryPlugin(Plugin):
        name = 'expiry'
        @property

"""

from ..api import EmptyBlock, Block, Config
from .exceptions import ConfigBuilderConflictException, ConfigBuilderException, ConfigBuilderNoSuchMethodException
from .baseplugins import RoutePlugin, ServerPlugin, Plugin


DEFAULT_PLUGINS = (RoutePlugin, ServerPlugin)
INVALID_PLUGIN_NAMES = ('top,')


class NginxConfigBuilder(object):
    """ Helper that builds a working nginx configuration

    Exposes a plugin-based architecture for generating nginx configurations.

    """

    def __init__(self, worker_processes='auto', worker_connections=512, error_log='logs/error.log', daemon='off'):
        """
        :param worker_processes str|int: number of worker processes to start with (default: auto)
        :param worker_connections int: number of nginx worker connections (default: 512)
        :param error_log str: path to nginx error log (default: logs/error.log)
        :param daemon str: whether or not to daemonize nginx (default: on)
        """

        self.plugins = []
        self._top = EmptyBlock(
            worker_processes=worker_processes,
            error_log=error_log,
            daemon=daemon,
        )

        self._http = Block(
            'http',
            include='../conf/mime.types'
        )

        self._cwo = self._http
        self._events = Block(
            'events',
            worker_connections=worker_connections
        )

        self._methods = {}

        for plugin in DEFAULT_PLUGINS:
            self.register_plugin(plugin(parent=self._http))

    def _validate_plugin(self, plugin):
        if not isinstance(plugin, Plugin):
            raise ConfigBuilderException(
                "Must be a subclass of {cls}".format(cls=Plugin.__name__),
                plugin=plugin
            )

        if plugin.name in INVALID_PLUGIN_NAMES:
            raise ConfigBuilderException(
                "{name} is a protected name and cannot be used as the name of"
                " a plugin".format(name=plugin.name),
                plugin=plugin
            )

        if plugin.name in (loaded.name for loaded in self.plugins):
            raise ConfigBuilderConflictException(plugin=plugin, loaded_plugin=plugin, method_name='name')

        methods = plugin.exported_methods.items()

        # check for conflicts
        for loaded_plugin in self.plugins:
            for (name, method) in methods:
                if name in loaded_plugin.exported_methods:
                    raise ConfigBuilderConflictException(
                        plugin=plugin,
                        loaded_plugin=loaded_plugin,
                        method_name=name
                    )

                # Also protect register_plugin, etc.
                if hasattr(self, name):
                    raise ConfigBuilderConflictException(
                        plugin=plugin,
                        loaded_plugin='top',
                        method_name=name
                    )

        # we can only be owned once
        if plugin._config_builder:
            raise ConfigBuilderException("Already owned by another NginxConfigBuilder", plugin=plugin)
        plugin._config_builder = self

    def register_plugin(self, plugin):
        """ Registers a new nginx builder plugin.

        Plugins must inherit from nginx.builder.baseplugins.Plugin and not expose methods that conflict
        with already loaded plugins

        :param plugin nginx.builder.baseplugins.Plugin: nginx plugin to add to builder
        """

        self._validate_plugin(plugin)

        # insert ourselves as the config builder for plugins
        plugin._config_builder = self
        self.plugins.append(plugin)

        self._methods.update(plugin.exported_methods)

    @property
    def top(self):
        """ Returns the logical top of the config hierarchy.

        This is a convenience method for any plugins that need to quickly access the top of the config tree.

        :returns :class:`nginx.config.Block`: Top of the config block
        """
        return self._http

    def __getattr__(self, attr):
        # Since we want this to be easy to use, we will do method lookup
        # on the methods that we've gotten from our different config plugins
        # whenever someone tries to call a method off of the builder.
        #
        # This means that plugins can just return a reference to the builder
        # so that users can just chain methods off of the builder.
        try:
            return self._methods[attr]
        except KeyError:
            raise ConfigBuilderNoSuchMethodException(attr, builder=self)

    def __repr__(self):
        return repr(Config(self._top, self._events, self._http))
