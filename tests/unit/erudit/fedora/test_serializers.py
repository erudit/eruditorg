import os

from eulxml.xmlmap import XmlObject
from erudit.fedora import serializers

FIXTURE_ROOT = os.path.join(os.path.dirname(__file__), 'fixtures')


def test_can_return_default_serializers_for_unmanaged_ds():
    default_serializers = serializers.get_datastream_cache_serializer('TEST')
    assert default_serializers == (
        serializers._default_serializer,
        serializers._default_deserializer
    )


def test_can_return_serializer_for_managed_ds():
    xsd300_serializers = serializers.get_datastream_cache_serializer('erudit_xsd300')
    assert xsd300_serializers == (serializers._xsd300_serializer, serializers._xsd300_deserializer)


def test_can_serialize_xsd300_ds():
    from eulxml.xmlmap import load_xmlobject_from_file

    with open(os.path.join(FIXTURE_ROOT, '1023796ar.xml')) as f:
        xmlobject = load_xmlobject_from_file(f)
        serialized_object = serializers._xsd300_serializer(xmlobject)
        assert type(serialized_object) == bytes


def test_can_deserialize_xsd300_ds():

    with open(os.path.join(FIXTURE_ROOT, '1023796ar.xml'), 'rb') as f:
        content = f.read()
        deserialized_object = serializers._xsd300_deserializer(content)
        assert type(deserialized_object) == XmlObject
