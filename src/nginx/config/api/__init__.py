"""
The Block API provides objects to programatically generate nginx configurations.

Example::

    >>> from nginx.config.api import Config, Section, Location
    >>> events = Section('events', worker_connections='1024')
    >>> http = Section('http', include='../conf/mime.types')
    >>> http.sections.add(
    ...     Section(
    ...         'server',
    ...         Location(
    ...             '/foo',
    ...             proxy_pass='upstream',
    ...         ),
    ...         server_name='_',
    ...     )
    ... )
    >>> nginx = Config(
    ...     events,
    ...     http,
    ...     worker_processes='auto',
    ...     daemon='on',
    ...     error_log='var/error.log',
    ... )
    >>> print(nginx)

    error_log var/error.log;
    worker_processes auto;
    daemon on;
    http {
        include ../conf/mime.types;
        server {
            server_name _;
            location /foo {
                proxy_pass upstream;
            }
        }
    }
    events {
        worker_connections 1024;
    }

.. The objects in this submodule are largely inspired by code found in https://github.com/FeroxTL/pynginxconfig-new.

"""
from .blocks import EmptyBlock, Block, Location
from .options import Comment, KeyOption, KeyValueOption, KeyMultiValueOption

__all__ = [
    'EmptyBlock',
    'Block',
    'Location',
    'KeyOption',
    'KeyValueOption',
    'KeyValueMultilines',
    'KeyMultiValueOption',
    'Comment',
    'Config',
    'Section'
]

# aliases
Config = EmptyBlock
Section = Block
