"""
Convienence utilities for building nginx configs
"""
from multiprocessing import cpu_count

from .api import Config, Location, Section
from .api.blocks import EmptyBlock


def dumps(config_list):
    """ Dumps a string representation of a config. Accepts a list of config objects.

    :param list config_list: A list of config objects from this module
    :rtype: str
    """
    return ''.join([str(element) for element in config_list])


def duplicate_options(key, values):
    """ There are many cases when building configs that you may have duplicate keys

    This function will produce an EmptyBlock object with duplicate keys but unique values

    Example::

        from nginx.config.helpers import duplicate_options
        from nginx.config.api import Location
        loc = Location(
            '/',
            duplicate_options('uwsgi_cache_valid', (['404', '5s'], ['200', '60s'])),
        )

    Which would produce::

        location / {
            uwsgi_cache_valid 200 60s;
            uwsgi_cache_valid 404 5s;
        }

    """
    duplicates = EmptyBlock()

    for value in values:
        duplicates.sections.add(EmptyBlock(**{key: value}))

    return duplicates


def simple_configuration(port=8080):
    """ Returns a simple nginx config.

    Also serves as an example of how to build configs using this module.

    :param int port: A port to populate the 'listen' paramter of the server block
    :rtype str:
    """

    http = Section(
        'http',
        access_log=['logs/access.log', 'combined'],
    )

    http.sections.server = Section(
        'server',
        Location('/'),
        listen=port,
    )

    events = Section(
        'events',
        worker_connections=4096
    )

    top = EmptyBlock(
        worker_processes=cpu_count(),
        error_log='logs/error.log'
    )

    config = Config(
        top,
        events,
        http,
    )

    return config
