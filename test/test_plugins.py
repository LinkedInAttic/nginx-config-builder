from nginx.config.builder import NginxConfigBuilder
from nginx.config.builder.plugins import UWSGICacheRoutePlugin, ProxyCacheRoutePlugin
from nginx.config.builder.exceptions import ConfigBuilderException

import pytest


@pytest.fixture
def uwsgi_cache_cfg():
    cfg = NginxConfigBuilder()
    cfg.register_plugin(UWSGICacheRoutePlugin())
    return cfg


@pytest.fixture
def proxy_cache_cfg():
    cfg = NginxConfigBuilder()
    cfg.register_plugin(ProxyCacheRoutePlugin())
    return cfg


def test_cache(uwsgi_cache_cfg, proxy_cache_cfg):
    uwsgi_expected = '''
daemon off;
error_log logs/error.log;
worker_processes auto;
http {
    add_header X-Cache-Status $upstream_cache_status;
    include ../conf/mime.types;
    uwsgi_cache_bypass $nocache;
    uwsgi_cache_key $request_uri;
    uwsgi_cache_min_uses 1;
    uwsgi_cache_use_stale off;
    server {
        server_name _;
        location /foo {
            uwsgi_cache_valid 500 40s;
        }
    }
}
events {
    worker_connections 512;
}'''

    proxy_expected = '''
daemon off;
error_log logs/error.log;
worker_processes auto;
http {
    add_header X-Cache-Status $upstream_cache_status;
    include ../conf/mime.types;
    proxy_cache_bypass $nocache;
    proxy_cache_convert_head on;
    proxy_cache_key $request_uri;
    proxy_cache_min_uses 1;
    proxy_cache_use_stale off;
    server {
        server_name _;
        location /foo {
            proxy_cache_valid 500 40s;
        }
    }
}
events {
    worker_connections 512;
}'''
    # cache_convert_head is added here to check to unsure that declared invalid options are discarded
    uwsgi_cache_cfg = uwsgi_cache_cfg.add_server().add_route('/foo')
    uwsgi_cache_cfg = uwsgi_cache_cfg.cache_uwsgi_route(cache_valid={'500': '40s'}, cache_convert_head=True).end().end()

    expected_byline = sorted(uwsgi_expected.splitlines())
    repr_byline = sorted(repr(uwsgi_cache_cfg).splitlines())

    assert expected_byline == repr_byline

    proxy_cache_cfg = proxy_cache_cfg.add_server().add_route('/foo')
    proxy_cache_cfg = proxy_cache_cfg.cache_proxy_route(cache_valid={'500': '40s'}, cache_convert_head=True).end().end()

    expected_byline = sorted(proxy_expected.splitlines())
    repr_byline = sorted(repr(proxy_cache_cfg).splitlines())

    assert expected_byline == repr_byline


def test_cache_wrong_parent(uwsgi_cache_cfg):
    with pytest.raises(ConfigBuilderException):
        uwsgi_cache_cfg.cache_uwsgi_route(cache_valid={'500': '40s'})
