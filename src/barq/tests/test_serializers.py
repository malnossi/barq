import pytest
import barq

class TestSerializers:
    def test_simple(self):
        class ASerializer(barq.Serializer):
            a = barq.Field()

        a = dict(a=5)
        assert ASerializer(a).data["a"] == 5

    def test_data_cached(self):
        class ASerializer(barq.Serializer):
            a = barq.Field()

        a = dict(a=5)
        serializer = ASerializer(a)
        data1 = serializer.data
        data2 = serializer.data
        assert data1 is data2  # Cached data is the same instance

    def test_inheritance(self):
        class ASerializer(barq.Serializer):
            a = barq.Field()

        class CSerializer(barq.Serializer):
            c = barq.Field()

        class ABSerializer(ASerializer):
            b = barq.Field()

        class ABCSerializer(ABSerializer, CSerializer):
            pass

        a = dict(a=5, b="hello", c=100)
        assert ASerializer(a).data["a"] == 5
        data = ABSerializer(a).data
        assert data["a"] == 5
        assert data["b"] == "hello"
        data = ABCSerializer(a).data
        assert data["a"] == 5
        assert data["b"] == "hello"
        assert data["c"] == 100

    def test_many(self):
        class ASerializer(barq.Serializer):
            a = barq.Field()

        objs = [dict(a=i) for i in range(5)]
        data = ASerializer(objs, many=True).data
        assert len(data) == 5
        for i in range(5):
            assert data[i]["a"] == i

    def test_serializer_as_field(self):
        class ASerializer(barq.Serializer):
            a = barq.Field()

        class BSerializer(barq.Serializer):
            b = ASerializer()

        b = dict(b=dict(a=3))
        assert BSerializer(b).data["b"]["a"] == 3

    def test_serializer_as_field_many(self):
        class ASerializer(barq.Serializer):
            a = barq.Field()

        class BSerializer(barq.Serializer):
            b = ASerializer(many=True)

        b = dict(b=[dict(a=i) for i in range(3)])
        b_data = BSerializer(b).data["b"]
        for i in range(3):
            assert b_data[i]["a"] == i

    def test_serializer_as_field_call(self):
        class ASerializer(barq.Serializer):
            a = barq.Field()

        class BSerializer(barq.Serializer):
            b = ASerializer(call=True)

        b = dict(b=lambda: dict(a=3))
        assert BSerializer(b).data["b"]["a"] == 3

    def test_serializer_method_field(self):
        class ASerializer(barq.Serializer):
            a = barq.MethodField()
            b = barq.MethodField("add_9")

            def get_a(self, obj):
                return obj["a"] + 5

            def add_9(self, obj):
                return obj["a"] + 9

        a = dict(a=2)
        data = ASerializer(a).data
        assert data["a"] == 7
        assert data["b"] == 11

    def test_custom_field(self):
        class Add5Field(barq.Field):
            def to_value(self, value):
                return value + 5

        class ASerializer(barq.Serializer):
            a = Add5Field()

        o = dict(a=10)
        data = ASerializer(o).data
        assert data["a"] == 15

    def test_optional_intfield(self):
        class ASerializer(barq.Serializer):
            a = barq.IntField(required=False)

        o = dict(a=None)
        data = ASerializer(o).data
        assert data["a"] is None

        o = dict(a="5")
        data = ASerializer(o).data
        assert data["a"] == 5

        class ASerializer(barq.Serializer):
            a = barq.IntField()

        o = dict(a=None)
        with pytest.raises(TypeError):
            ASerializer(o).data

    def test_optional_field(self):
        class ASerializer(barq.Serializer):
            a = barq.Field(required=False)

        o = dict(a=None)
        data = ASerializer(o).data
        assert data["a"] is None

        o = dict()
        data = ASerializer(o).data
        assert data["a"] is None

        class ASerializer(barq.Serializer):
            a = barq.Field()

        o = dict(a=None)
        data = ASerializer(o).data
        assert data["a"] is None

        o = dict()
        with pytest.raises(KeyError):
            ASerializer(o).data

    def test_default_field(self):
        class ASerializer(barq.Serializer):
            a = barq.Field(default="test")

        o = dict()
        data = ASerializer(o).data
        assert data["a"] == "test"

    def test_self_field(self):
        class ASerializer(barq.Serializer):
            _test = "coucou"
            test = barq.SelfField(attr="_test")

        data = ASerializer().data
        assert data["test"] == "coucou"

    def test_optional_methodfield(self):
        class ASerializer(barq.Serializer):
            a = barq.MethodField(required=False)

            def get_a(self, obj):
                return obj["a"]

        o = dict(a=None)
        data = ASerializer(o).data
        assert data["a"] is None

        o = dict(a="5")
        data = ASerializer(o).data
        assert data["a"] == "5"

        class ASerializer(barq.Serializer):
            a = barq.MethodField()

            def get_a(self, obj):
                return obj["a"]

        o = dict(a=None)
        data = ASerializer(o).data
        assert data["a"] is None

    def test_serializer_with_custom_output_label(self):
        class ASerializer(barq.Serializer):
            context = barq.StrField(label="@context")
            content = barq.MethodField(label="@content")

            def get_content(self, obj):
                return obj["content"]

        o = dict(context="http://foo/bar/baz/", content="http://baz/bar/foo/")
        data = ASerializer(o).data
        assert "@context" in data
        assert data["@context"] == "http://foo/bar/baz/"
        assert "@content" in data
        assert data["@content"] == "http://baz/bar/foo/"
