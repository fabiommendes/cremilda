from cremilda import parse
from cremilda.ir import internal_representation

HELLO_MODULE = """
def _module():
    from cremilda_runtime import log
    msg = log('hello world!')
    return {}
globals().update(_module())
"""


class TestToPythonStmt:
    def mod(self, src):
        return internal_representation(parse(src))

    def test_can_emit_correct_hello_word_module(self):
        mod = self.mod('msg = log("hello world!");')
        pyast = mod.to_python()
        assert pyast.source() == HELLO_MODULE.strip()
