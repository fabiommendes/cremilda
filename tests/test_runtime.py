from cremilda_runtime.base_types import adt


class TestTypeFactories:
    def test_creation_of_adt_type(self):
        Maybe = adt('Maybe', Nothing=(), Just=object)
        assert str(Maybe.Just(42)) == 'Just(42)'
        assert str(Maybe.Nothing) == 'Nothing'
