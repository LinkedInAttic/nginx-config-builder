from nginx.config.builder import NginxConfigBuilder
from nginx.config.builder.baseplugins import Plugin
from nginx.config.builder.plugins import UWSGICacheRoutePlugin
from nginx.config.builder.exceptions import (
    ConfigBuilderException,
    ConfigBuilderConflictException,
    ConfigBuilderNoSuchMethodException
)
import pytest


def test_bad_plugin():
    class BadPlugin(BaseException):
        name = 'bad'
        valid_cfg_parents = tuple()

        @property
        def exported_methods(self):
            return {}

    nginx = NginxConfigBuilder()
    with pytest.raises(ConfigBuilderException):
        nginx.register_plugin(BadPlugin())


def test_custom_plugin():
    class CustomPlugin(Plugin):
        name = 'custom'
        valid_cfg_parents = tuple()

        def foo(self):
            pass

        @property
        def exported_methods(self):
            return {'foo': self.foo}

    nginx = NginxConfigBuilder()
    nginx.register_plugin(CustomPlugin())


def test_conflict_plugins():
    class CustomOne(Plugin):
        name = 'one'
        valid_cfg_parents = tuple()

        def foo(self):
            pass

        @property
        def exported_methods(self):
            return {'foo': self.foo}

    class CustomTwo(Plugin):
        name = 'two'
        valid_cfg_parents = tuple()

        def foo(self):
            pass

        @property
        def exported_methods(self):
            return {'foo': self.foo}

    nginx = NginxConfigBuilder()
    nginx.register_plugin(CustomOne())

    with pytest.raises(ConfigBuilderConflictException):
        nginx.register_plugin(CustomTwo())


def test_same_name():
    class CustomOne(Plugin):
        name = 'one'
        valid_cfg_parents = tuple()

        def foo(self):
            pass

        @property
        def exported_methods(self):
            return {'foo': self.foo}

    class CustomTwo(Plugin):
        name = 'one'
        valid_cfg_parents = tuple()

        def foo(self):
            pass

        @property
        def exported_methods(self):
            return {'bar': self.foo}

    nginx = NginxConfigBuilder()
    nginx.register_plugin(CustomOne())

    with pytest.raises(ConfigBuilderConflictException):
        nginx.register_plugin(CustomTwo())


def test_builtin_conflict():
    class CustomPlugin(Plugin):
        name = 'one'
        valid_cfg_parents = tuple()

        def register_plugin(self):
            pass

        @property
        def exported_methods(self):
            return {'register_plugin': self.register_plugin}

    nginx = NginxConfigBuilder()

    with pytest.raises(ConfigBuilderConflictException):
        nginx.register_plugin(CustomPlugin())


def test_calling_plugin_meth():
    class Custom(Plugin):
        name = 'custom'
        valid_cfg_parents = tuple()

        def foo(self):
            return 'foo'

        @property
        def exported_methods(self):
            return {'foo': self.foo}

    nginx = NginxConfigBuilder()
    nginx.register_plugin(Custom())
    assert nginx.foo() == 'foo'

    class CustomArgs(Plugin):
        name = 'custom args'
        valid_cfg_parents = tuple()

        def bar(self, other, kwarg=None):
            return (other, kwarg)

        @property
        def exported_methods(self):
            return {'bar': self.bar}

    nginx.register_plugin(CustomArgs())
    assert nginx.bar('bar', kwarg='baz') == ('bar', 'baz')

    with pytest.raises(ConfigBuilderNoSuchMethodException):
        nginx.blah()


def test_basic_route():
    expected = '''
daemon off;
error_log logs/error.log;
worker_processes auto;
events {
    worker_connections 512;
}
http {
    include ../conf/mime.types;
    server {
        server_name _;
        location /foo {
        }
    }
}'''

    nginx = NginxConfigBuilder()
    nginx.add_server().add_route('/foo').end().end()
    assert sorted(expected.splitlines()) == sorted(repr(nginx).splitlines())


def test_nested_route():
    expected = '''
daemon off;
error_log logs/error.log;
worker_processes auto;
events {
    worker_connections 512;
}
http {
    include ../conf/mime.types;
    server {
        server_name _;
        location /foo {
            location /bar {
            }
        }
    }
}'''

    nginx = NginxConfigBuilder()
    nginx.add_server().add_route('/foo').add_route('/bar').end().end().end()

    assert sorted(expected.splitlines()) == sorted(repr(nginx).splitlines())


def test_invalid_parent():
    nginx = NginxConfigBuilder()
    with pytest.raises(ConfigBuilderException):
        nginx.add_route('/blah')


def test_context_man():
    expected = '''
daemon off;
error_log logs/error.log;
worker_processes auto;
events {
    worker_connections 512;
}
http {
    include ../conf/mime.types;
    uwsgi_cache_key $request_uri;
    uwsgi_cache_min_uses 1;
    uwsgi_cache_bypass $nocache;
    uwsgi_cache_use_stale off;
    add_header X-Cache-Status $upstream_cache_status;
    server {
        server_name _;
        location /foo {
            uwsgi_cache_valid 404 5s;
        }
        location /bar {
        }
    }
}'''

    nginx = NginxConfigBuilder()
    nginx.register_plugin(UWSGICacheRoutePlugin())

    with nginx.add_server() as server:
        with server.add_route('/foo') as foo:
            foo.cache_uwsgi_route(cache_valid={'404': '5s'})
        server.add_route('/bar').end()

    assert sorted(expected.splitlines()) == sorted(repr(nginx).splitlines())
