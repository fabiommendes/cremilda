from cremilda.runtime.base import adt


class TestTypeFactories:
    def test_creation_of_adt_type(self):
        Maybe = adt('Maybe', Nothing=(), Just=object)  # noqa: N806
        assert str(Maybe.Just(42)) == 'Just(42)'
        assert str(Maybe.Nothing) == 'Nothing'
