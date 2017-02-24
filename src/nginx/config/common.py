"""
Defines a variety of common nginx config boilerplate. Includes a lot of uwsgi defaults and settings.
"""
from . import helpers
from .api import EmptyBlock, Block


def _uwsgi_params():
    """ These are the parameters provided by nginx in "uwsgi_params"

    http://uwsgi-docs.readthedocs.io/en/latest/Nginx.html

    """
    return helpers.duplicate_options(
        'uwsgi_param',
        [
            ['QUERY_STRING', '$query_string'],
            ['REQUEST_METHOD', '$request_method'],
            ['CONTENT_TYPE', '$content_type'],
            ['CONTENT_LENGTH', '$content_length'],
            ['REQUEST_URI', '$request_uri'],
            ['PATH_INFO', '$document_uri'],
            ['DOCUMENT_ROOT', '$document_root'],
            ['SERVER_PROTOCOL', '$server_protocol'],
            ['REMOTE_ADDR', '$remote_addr'],
            ['REMOTE_PORT', '$remote_port'],
            ['SERVER_ADDR', '$server_addr'],
            ['SERVER_PORT', '$server_port'],
            ['SERVER_NAME', '$server_name'],
        ]
    )


def _gzip_options():
    """ These are some decent default settings for gzip compression """
    return EmptyBlock(
        **dict(
            gzip='on',
            gzip_types='application/json',
            gzip_comp_level=2,
            gzip_min_length=1024,
        )
    )


def _uwsgi_cache():
    """ A set of useful defaults for using nginx's response cache with uWSGI

    This block of options belongs in your HTTP section.

    NB! you must set "set $nocache 0;" in the Location block of your uwsgi backend.

    see: http://nginx.org/en/docs/http/ngx_http_uwsgi_module.html
    """
    return EmptyBlock(
        **dict(
            uwsgi_cache_path=[
                'var/nginx_cache',
                'keys_zone=one:10m',
                'loader_threshold=300',
                'loader_files=200',
                'max_size=200m'
            ],
            uwsgi_cache_key='$request_uri',
            uwsgi_cache_min_uses=1,
        )
    )


def _uwsgi_cache_location():
    """ These are some decent defaults for caching uwsgi responses """
    cache_options = EmptyBlock()
    # This is a bit of a hack to deal with the Cache-Control header
    # normally, the uwsgi nginx module doesn't honor the Cache-Control
    # header at all. For the cases where a user sends `max-age=0` or
    # `no-cache`, this will do the right thing and bypass the uwsgi
    # module's cache. This hack does not handle cases where max-age
    # is set to something else - it will just use the cache in that
    # case regardless of age
    cache_options.sections.add(
        EmptyBlock(set=['$nocache', '0']),
        Block(
            'if ($http_cache_control = "max-age=0")',
            set=['$nocache', '1']
        ),
        Block(
            'if ($http_cache_control = "no-cache")',
            set=['$nocache', '1']
        ),
        EmptyBlock(uwsgi_cache_valid=['404', '5s']),
        EmptyBlock(uwsgi_cache_valid=['200', '301', '302', '1d']),
    )

    return cache_options


def _large_buffers():
    """ These are some larger than default buffer settings.

    Use at your own risk!

    """
    return EmptyBlock(
        **dict(
            client_body_buffer_size='128k',
            client_max_body_size='10m',
            client_header_buffer_size='1k',
            large_client_header_buffers=[4, '4k'],
            output_buffers=[1, '32k'],
            postpone_output=1460,
        )
    )


def _statsd_options_location():
    """ These are some good defaults to supply to Nginx when using the statsd plugin.

    https://github.com/zebrafishlabs/nginx-statsd

    NB! it requires you to include a "statsd_server" directive in your http section.
    This set of common directives should go in any Location block.

    """
    statsd = EmptyBlock()
    statsd.sections.add(
        EmptyBlock(statsd_count=['"nginx.requests"', '1']),
        EmptyBlock(statsd_count=['"nginx.responses.$status"', '1', '"$status"']),
        EmptyBlock(statsd_timing=['"nginx.request_time"', '"$request_time"']),
        EmptyBlock(statsd_timing=['"nginx.upstream_response_time"', '"$upstream_response_time"']),
        EmptyBlock(statsd_count=['"nginx.response_length"', '"$request_length"']),
        EmptyBlock(statsd_count=['"nginx.bytes_sent"', '"$bytes_sent"']),
    )
    return statsd


# aliases
uwsgi_params = _uwsgi_params()
uwsgi_cache = _uwsgi_cache()
gzip_options = _gzip_options()
buffer_options = _large_buffers()
uwsgi_cache_location = _uwsgi_cache_location()
statsd_options_location = _statsd_options_location()


def ratelimit_options(qps):
    """ create rate limit shared memory zone, used for tracking different connections """
    return EmptyBlock(
        limit_req_zone=[
            '$binary_remote_addr',
            'zone=ratelimit_zone:10m',
            'rate={qps}r/s'.format(qps=qps),
        ]
    )


def ratelimit_options_location(burst_qps):
    """ this needs to be added to a location block in order for that location to get rate limiting"""
    return EmptyBlock(
        limit_req_zone=[
            'zone=ratelimit_zone',
            'burst={burst_qps}'.format(burst_qps=burst_qps),
        ]
    )
