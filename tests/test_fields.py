from datetime import datetime, date
from barq import (
    Field,
    IntField,
    StrField,
    BoolField,
    FloatField,
    MethodField,
    DateField,
    DateTimeField,
)


class TestFields:
    def test_to_value_noop(self):
        assert Field().to_value(5) == 5
        assert Field().to_value("a") == "a"
        assert Field().to_value(None) is None

    def test_as_getter_none(self):
        assert Field().as_getter(None, None) is None

    def test_is_to_value_overridden(self):
        class TransField(Field):
            def to_value(self, value):
                return value

        field = Field()
        assert field._is_to_value_overridden() is False
        field = TransField()
        assert field._is_to_value_overridden() is True
        field = IntField()
        assert field._is_to_value_overridden() is True

    def test_str_field(self):
        field = StrField()
        assert field.to_value("a") == "a"
        assert field.to_value(5) == "5"

    def test_bool_field(self):
        field = BoolField()
        assert field.to_value(True) is True
        assert field.to_value(False) is False
        assert field.to_value(1) is True
        assert field.to_value(0) is False

    def test_int_field(self):
        field = IntField()
        assert field.to_value(5) == 5
        assert field.to_value(5.4) == 5
        assert field.to_value("5") == 5

    def test_float_field(self):
        field = FloatField()
        assert field.to_value(5.2) == 5.2
        assert field.to_value("5.5") == 5.5

    def test_date_field(self):
        field = DateField(date_format="%Y-%m-%d")
        assert field.to_value(date(2024, 3, 7).isoformat()) == "2024-03-07"
        field = DateField(date_format="%d/%m/%Y")
        assert field.to_value("07/03/2024") == "2024-03-07"

    def test_datetime_field(self):
        field = DateTimeField(date_format="%Y-%m-%dT%H:%M:%S")
        assert (
            field.to_value(datetime(2024, 3, 7, 18, 00).isoformat())
            == "2024-03-07T18:00:00"
        )
        field = DateTimeField(date_format="%d/%m/%Y à %H:%M:%S")
        assert field.to_value("07/03/2024 à 18:00:00") == "2024-03-07T18:00:00"

    def test_method_field(self):
        class FakeSerializer:
            def get_a(self, obj):
                return obj["a"]

            def z_sub_1(self, obj):
                return obj["z"] - 1

        serializer = FakeSerializer()

        fn = MethodField().as_getter("a", serializer)
        assert fn({"a": 3}) == 3

        fn = MethodField("z_sub_1").as_getter("a", serializer)
        assert fn({"z": 3}) == 2

        assert MethodField.getter_takes_serializer is True

    def test_field_label(self):
        field1 = StrField(label="@id")
        assert field1.label == "@id"
