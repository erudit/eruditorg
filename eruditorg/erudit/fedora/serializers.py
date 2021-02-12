""" This module defines serializers for Fedora datastreams """
from eulxml.xmlmap import load_xmlobject_from_string


def _xsd300_serializer(content):
    """ serialize the xsd300 XmlObject to a string """
    return content.serialize()


def _xsd300_deserializer(content):
    """ create a XmlObject from a string """
    if content:
        return load_xmlobject_from_string(content)


def _default_serializer(datastream):
    """ the default serializer does not do anything """
    return datastream


def _default_deserializer(datastream):
    """ the default deserializer does not do anything """
    return datastream


datastream_cache_serializers = {
    'erudit_xsd300': (_xsd300_serializer, _xsd300_deserializer,),
    'summary': (_xsd300_serializer, _xsd300_deserializer,)
}
""" define the serializer mapping """


def get_datastream_cache_serializer(datastream_name):
    """ returns the serializer for the given datastream

    if the datastream is not declared in the datastream mapping,
    the default serializer is returned.
    """
    return datastream_cache_serializers.get(
        datastream_name, (_default_serializer, _default_deserializer)
    )
