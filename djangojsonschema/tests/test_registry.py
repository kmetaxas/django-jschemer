import unittest
from django.forms import fields
from .. import fields as jsonfields

from ..registry import registry


class TestSchemaField1(jsonfields.BaseDjangoJSONSchemaField ):
    def get_type(self):
        return "string"


class NotReallyDjangoField(object):
    """ Does not subclass django.forms.fields.Field """
    pass


class RegistryTestCase(unittest.TestCase):


    def test_register(self):

        # This should raise ValueError because it is an included field and
        # should have been added using a decorator
        with self.assertRaisesRegexp(ValueError,"^Already registered$"):
            registry.register(fields.CharField , jsonfields.CharField)

        self.assertEquals(jsonfields.CharField,
                          registry.get_schemafield(fields.CharField)
                          )
        self.assertEquals(registry.get_schemafield( TestSchemaField1 ), None)

        with self.assertRaises(ValueError):
            # Schema field does not inherit from BaseDjangoJSONSchemaField
            registry.register(fields.CharField, TestSchemaField1 )

        with self.assertRaises(ValueError):
            # django field does not inherit from django.forms.field.Field
            registry.register(NotReallyDjangoField, TestSchemaField1 )

        with self.assertRaisesRegexp(ValueError,"^Already registered$"):
            # already registered
            registry.register(fields.CharField, jsonfields.CharField)
            pass

        # Test passing an instance instead of Class object
        with self.assertRaises(ValueError):
            registry.register(fields.CharField,
                              jsonfields.CharField(fields.CharField(),"testname"))
        with self.assertRaises(ValueError):
            registry.register(fields.CharField(),
                              jsonfields.CharField)

    def test_unregister(self):
        # first make sure it **is** registered
        self.assertEquals(registry.get_schemafield(fields.CharField),
                          jsonfields.CharField)

        registry.unregister(fields.CharField)
        self.assertEquals( registry.get_schemafield(fields.CharField), None)

        with self.assertRaises(ValueError):
            # parameter does not inherit from django's Field
            registry.unregister(NotReallyDjangoField)

        with self.assertRaises(ValueError):
            # not registered
            registry.unregister(TestSchemaField1)
            pass
