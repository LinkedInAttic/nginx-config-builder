from .baseplugins import Plugin
from ..api import KeyValueOption, EmptyBlock

from abc import ABCMeta, abstractproperty
from enum import Enum, unique
import six


class _ValEnum(Enum):
    """Enum that yields its value on stringification"""
    def __str__(self):
        return str(self.value)


@unique
class CacheUseStale(_ValEnum):
    """
    enum for possible options to be passed to *_use_stale. enum for safety
    (preventing invalid options) as well as documentation and reuse
    """

    error = 'error'
    timeout = 'timeout'
    invalid_header = 'invalid_header'
    updating = 'updating'
    http_500 = 'http_500'
    http_503 = 'http_503'
    http_403 = 'http_403'
    http_404 = 'http_404'
    off = 'off'


@six.add_metaclass(ABCMeta)
class CacheRoutePlugin(Plugin):
    """
    Route caching superclass

    All caching plugins can inherit off of this, by setting a `cache_prefix` property
    that gets prepended to each nginx directive that gets set. This automatically sets
    the top-level cache directives that need to be set, and when called off of a route,
    it turns caching on for that route for the duration specified in the arguments
    """

    invalid = ()
    valid_cfg_parents = ('location',)

    @abstractproperty
    def cache_prefix(self):
        pass

    def _set_cache_option(self, opt, val):
        cp = "{cache_prefix}_".format(cache_prefix=self.cache_prefix)
        if opt not in self.invalid and val:
            self.config_builder.top.options[cp + opt] = val

    def cache_route(self, cache_key='$request_uri', ignore_headers=None,
                    cache_min_uses=1, cache_bypass='$nocache',
                    cache_use_stale=CacheUseStale.off, cache_valid=None,
                    cache_convert_head=None):
        cp = "{cache_prefix}_".format(cache_prefix=self.cache_prefix)

        # set the options directly on the route now
        self.add_child(EmptyBlock(
            *tuple(KeyValueOption(cp + 'cache_valid', value='{k} {v}'.format(k=k, v=v))
                   for (k, v) in cache_valid.items())
        ))

        # XXX: check if these are set the first time
        # add options to top
        self._set_cache_option('cache_key', cache_key)
        self._set_cache_option('cache_min_uses', cache_min_uses)
        self._set_cache_option('cache_bypass', cache_bypass)
        self._set_cache_option('cache_use_stale', cache_use_stale)
        self._set_cache_option('cache_convert_head', cache_convert_head)

        if 'add_header' not in self.config_builder.top.options:
            self.config_builder.top.options['add_header'] = []
        self.config_builder.top.options['add_header'].extend(['X-Cache-Status', '$upstream_cache_status'])

        return self


class UWSGICacheRoutePlugin(CacheRoutePlugin):
    name = 'cache uwsgi route'
    cache_prefix = 'uwsgi'
    invalid = ('cache_convert_head',)

    @property
    def exported_methods(self):
        return {'cache_uwsgi_route': self.cache_route}


class ProxyCacheRoutePlugin(CacheRoutePlugin):
    name = 'cache proxy route'
    cache_prefix = 'proxy'

    @property
    def exported_methods(self):
        return {'cache_proxy_route': self.cache_route}
