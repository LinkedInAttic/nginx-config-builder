from .base import Base


class KeyOption(Base):
    """ A KeyOption represents a directive with no value.

    For example: http://nginx.org/en/docs/http/ngx_http_core_module.html#internal

    """
    def __init__(self, name):
        self.name = self.value = name

    def __repr__(self):
        return self._render(
            '{name};'.format(
                name=self.name,
            )
        )


class KeyValueOption(Base):
    """ A key/value directive. This covers most directives available for Nginx """
    def __init__(self, name, value=''):
        self.name = name
        if isinstance(value, bool):
            self.value = 'off' if value is False else 'on'
        elif isinstance(value, int):
            self.value = str(value)
        elif isinstance(value, list):
            self.value = [str(e) for e in value]
        else:
            self.value = value

    def __repr__(self):
        return self._render(
            '{name} {value};'.format(
                name=self.name,
                value=self.value
            )
        )


class KeyMultiValueOption(KeyValueOption):
    """ A key with multiple space delimited options.

    For example: http://nginx.org/en/docs/http/ngx_http_log_module.html#access_log

    Example::

        >>> from nginx.config.api.options import KeyMultiValueOption
        >>> a_log = KeyMultiValueOption('access_log', ['/path/to/log.gz', 'combined', 'gzip', 'flush=5m'])
        >>> print(a_log)

        access_log /path/to/log.gz combined gzip flush=5m;

    """
    def __repr__(self):
        return self._render(
            '{name} {value};'.format(
                name=self.name,
                value=' '.join(self.value)
            )
        )


class Comment(Base):
    """ A simple comment object. """

    _offset = ''
    _comment = ''

    def __init__(self, offset='', comment='', **kwargs):
        self._offset = offset
        self._comment = comment
        super(Comment, self).__init__(**kwargs)

    def __repr__(self):
        return self._render(
            '{offset}# {comment}'.format(
                offset=self._offset,
                comment=self._comment,
            )
        )


class AttrDict(dict):
    """ A dictionary that exposes it's values as attributes. """
    def __init__(self, owner):
        self.__dict__ = self
        self._owner = owner

    def __setitem__(self, key, val):
        if hasattr(val, '_parent'):
            val._parent = self._owner
        return super(AttrDict, self).__setitem__(key, val)

    def __repr__(self):
        owner = self.pop('_owner')
        ret = super(AttrDict, self).__repr__()
        self._owner = owner
        return ret


class AttrList(AttrDict):
    """ A dictionary/list hybrid that exposes values as attributes. """
    def __iter__(self):
        return iter(self.values())

    def append(self, item):
        if hasattr(item, '_parent'):
            item._parent = self._owner
        if hasattr(item, 'name'):
            self[item.name] = item
        else:
            self[hash(item)] = item

    def add(self, *items):
        for item in items:
            self.append(item)
