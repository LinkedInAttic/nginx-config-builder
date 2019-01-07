class Base(object):
    """ This is the base class for all blocks and options. """
    _indent_level = 0
    _indent_char = ' '
    _indent = 4
    _parent = None

    def _get_indent(self):
        return self._indent_char * self._indent * self._indent_level

    def _render(self, name):
        return '\n{indent}{name}'.format(
            name=name,
            indent=self._get_indent()
        )

    def __str__(self):
        return str(self.__repr__())

    @property
    def parent(self):
        return self._parent
