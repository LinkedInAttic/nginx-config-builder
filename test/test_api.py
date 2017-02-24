from nginx.config.api.blocks import Block, EmptyBlock
from nginx.config.api.options import KeyOption, KeyValueOption, KeyMultiValueOption
from nginx.config.helpers import duplicate_options


def test_block_options():
    block = Block('test')

    assert block.options == {'_owner': block}
    assert block.sections == {'_owner': block}

    block.options.opt = 'val1'

    assert repr(block) == '\ntest {\n    opt val1;\n}'

    block.options.opt = 'val2 val3'

    assert repr(block) == '\ntest {\n    opt val2 val3;\n}'

    block.options.opt = ''

    assert repr(block) == '\ntest {\n    opt;\n}'


def test_emptyblock_options():
    block = EmptyBlock()

    assert block.options == {'_owner': block}
    assert block.sections == {'_owner': block}

    block.options.opt = 'val'

    assert repr(block) == '\nopt val;'


def test_options():
    opt1 = KeyOption('opt')
    assert repr(opt1) == '\nopt;'

    opt2 = KeyValueOption('opt', value='value')
    assert repr(opt2) == '\nopt value;'

    opt3 = KeyMultiValueOption('opt', value=['v', 'a', 'l'])
    assert repr(opt3) == '\nopt v a l;'


def test_sections():
    block = Block('test')
    block.sections.add(EmptyBlock(test=1))

    assert repr(block) == '\ntest {\n    test 1;\n}'


def test_duplicates():
    dupes = duplicate_options('test', [1, 2, 3])
    assert sorted(repr(dupes).splitlines()) == sorted('\ntest 1;\ntest 2;\ntest 3;'.splitlines())
