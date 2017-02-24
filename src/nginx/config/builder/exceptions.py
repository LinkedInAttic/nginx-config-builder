class ConfigBuilderException(BaseException):
    """
    Top-level exception for config builder exceptions.

    :param Plugin plugin: plugin that caused the problem
    :param NginxConfigBuilder builder: current config builder
    :param str msg: message describing the problem
    """
    def __init__(self, msg, **kwargs):
        self.plugin = kwargs.get('plugin', None)
        self.cfg = kwargs.get('builder', None)
        self.msg = msg
        super(ConfigBuilderException, self).__init__(msg)

    def __str__(self):
        return '{plugin}: {msg}'.format(plugin=str(self.plugin), msg=self.msg)


class ConfigBuilderConflictException(ConfigBuilderException):
    """
    Two plugins have conflicting plugins

    :param Plugin loaded_plugin: plugin that's already been added to config builder
    :param str method_name: name of the method that exists in both plugins
    """
    def __init__(self, **kwargs):
        self.loaded_plugin = kwargs.get('loaded_plugin', None)
        self.method_name = kwargs.get('method_name', None)
        super(ConfigBuilderConflictException, self).__init__('we override __str__', **kwargs)

    def __str__(self):
        repr_string = (
            "Method `{method_name}` from `{plugin}` conflicts with a "
            "method of the same name loaded from `{loaded_plugin}`"
        )

        kwargs = dict(
            plugin=str(self.plugin),
            loaded_plugin=str(self.loaded_plugin),
            method_name=self.method_name
        )

        return repr_string.format(**kwargs)


class ConfigBuilderNoSuchMethodException(ConfigBuilderException, AttributeError):
    """
    Exception raised when a user tries to call a non-existent method

    :param str attr: name of the attribute that the user attempted to call
    """
    def __init__(self, attr, **kwargs):
        self.attr = attr
        super(ConfigBuilderNoSuchMethodException, self).__init__('', **kwargs)

    def __str__(self):
        errstr = 'No plugins provide method {method}'.format(method=self.attr)

        if self.builder is not None:
            methods = '\n\t'.join(self.cfg._methods.keys)
            errstr = errstr + '\nExported methods:{methods}\n\t'.format(methods=methods)

        return errstr
