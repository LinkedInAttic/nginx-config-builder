[![PyPI](https://img.shields.io/pypi/v/nginx-config-builder.svg)](https://pypi.python.org/pypi/nginx-config-builder)
[![Build Status](https://travis-ci.org/linkedin/nginx-config-builder.svg?branch=master)](https://travis-ci.org/linkedin/nginx-config-builder)
[![Documentation Status](https://readthedocs.org/projects/nginx-config-builder/badge/?version=latest)](http://nginx-config-builder.readthedocs.io/en/latest/?badge=latest)
[![License](https://img.shields.io/badge/License-BSD%202--Clause-orange.svg)](https://opensource.org/licenses/BSD-2-Clause)

nginx-config-builder
====================

A python library for constructing nginx configuration files.

Installation
============
```
pip install nginx-config-builder
```

Usage
=====

This library ships two interfaces to build configuration with, a high level builder API as well as the low level block-based API that the builder makes use of. Consumers can choose whichever makes sense for their use case:

#### The Builder API

The builder API is expressive and pluggable.

```
>>> from nginx.config.builder import NginxConfigBuilder
>>> nginx = NginxConfigBuilder(daemon='on')
>>> with nginx.add_server() as server:
...     server.add_route('/foo', proxy_pass='upstream').end()
...
>>> print(nginx)

error_log logs/nginx.error.log;
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
 
```

#### The Block API

The block api provides more granularity and explicitness at the cost of being  substantially more verbose than the builder api.

```
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
```

Development
===========

Checkout the repo:

```
git clone git@github.com:linkedin/nginx-config-builder.git
```

Set up your virtual environment:

```
cd nginx-config-builder
python setup.py venv
source activate
```

Install the project and start hacking!

```
python setup.py develop
```

Don't forget to write/run tests!

```
pip install tox
tox
```

Authors
=======

* [Loren Carvalho](https://www.github.com/sixninetynine)
* [William Orr](https://www.github.com/worr)
