import unittest
from .test_fields import TestForm, TestFormWithNoOptions
from django_jschemer.jsonschema import DjangoFormToJSONSchema
import jsonschema
from jsonschema.exceptions import ValidationError as SchemaValidationError

class DjangoFormToJSONSchemaTestCase(unittest.TestCase):

    def setUp(self):
        self.form = TestForm()
        self.converter = DjangoFormToJSONSchema()
        self.validating_data = {
            'a_charfield':"Test text",
            'a_charfield_lazy':"text",
            'a_url':'http://www.example.com',
            'a_date':'2017-01-02',
            'a_time':'14:30',
            'a_datetime':'10/25/2006 14:30:59',
            'an_integer':11,
            'an_ipaddress':'127.0.0.1',
            'a_boolean':True,
            'a_regex':r"\d+",
            'a_choicefield':'a',
        }

    def test_convert_to_schema(self):
        schema,options  = self.converter.convert_to_schema(self.form)
        print("converted schema={}".format(schema))
        # We have no assertion because if successfull it does *NOT* raise an
        # exception.
        jsonschema.Draft4Validator.check_schema(schema)
        jsonschema.validate(self.validating_data,schema)

        # lets invalidate our data
        with self.assertRaisesRegexp(SchemaValidationError,
                                     "'NOT AN INTEGER' is not of type 'integer'"):
            invalid_data = self.validating_data.copy()
            invalid_data['an_integer'] = "NOT AN INTEGER"
            jsonschema.validate(invalid_data,schema)

        with self.assertRaisesRegexp(SchemaValidationError,
                                     "1 is not of type 'boolean'"):
            invalid_data = self.validating_data.copy()
            invalid_data['a_boolean'] = 1
            jsonschema.validate(invalid_data,schema)

        # Test TestFormWithNoOptions
        schema, options = self.converter.convert_to_schema(TestFormWithNoOptions)
        jsonschema.Draft4Validator.check_schema(schema)
        jsonschema.validate(self.validating_data,schema)


    def test_alpacaoptions_class(self):
        schema,options  = self.converter.convert_to_schema(self.form)
        # Assert that AlpacaOptions are merged
        self.assertEquals(schema['dependencies'],{'a_url':['a_charfield']})
        self.assertEquals(
            options['fields']['a_charfield']['placeholder'],
            'PLACETEST')
        self.assertEquals(
            options['fields']['a_url']['allowIntranet'],
            True)
        # Test with a form that has *NO* inner class
        schema, options = self.converter.convert_to_schema(TestFormWithNoOptions)
        with self.assertRaises(KeyError):
            options['fields']['a_url']['allowIntranet'],


    def test_convert_formfield(self):
        pass
