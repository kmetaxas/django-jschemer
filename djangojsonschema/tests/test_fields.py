#from jsonschema import Draft4Validator
import unittest
from django.forms import Form
from django.forms import fields
from django.utils.translation import ugettext_lazy as _
from .. import fields as jsonfields

class TestForm(Form):
    a_charfield = fields.CharField(max_length=20, min_length=4,
                                   help_text="HelpText")
    a_charfield_lazy = fields.CharField(max_length=20, min_length=4,
                                        label = _("Test Label"),
                                        help_text=_("HelpText"))
    a_url = fields.URLField()
    a_date = fields.DateField()
    a_datetime = fields.DateTimeField()
    a_time = fields.TimeField()
    an_integer = fields.IntegerField(
        label="IntegerTest",
        max_value=1000, min_value=10,
    )
    an_ipaddress = fields.GenericIPAddressField()
    a_boolean = fields.BooleanField()


class FormFieldsTestCase(unittest.TestCase):

    def setUp(self):
        self.form = TestForm()

    def test_convert_charfield(self):
        name = 'a_charfield'
        unbound_field = TestForm.base_fields[name]
        jsonfield = jsonfields.CharField(unbound_field,name)
        part = jsonfield.get_schema_part()
        print("json_part={}".format(part))
        self.assertEquals(part['maxLength'],20)
        self.assertEquals(part['minLength'],4)
        self.assertEquals(part['description'],"HelpText")
        self.assertEquals(part['type'],"string")
        self.assertEquals(part['title'],"A charfield")
        # There should be no 'formar' for CharField
        with self.assertRaises(KeyError):
            part['format']

        # Test a lazy charfield with label
        name = 'a_charfield_lazy'
        unbound_field = TestForm.base_fields[name]
        jsonfield = jsonfields.CharField(unbound_field,name)
        part = jsonfield.get_schema_part()
        self.assertEquals(part['description'],"HelpText")
        self.assertEquals(part['title'],"Test Label")

    def test_convert_booleanfield(self):
        name = 'a_boolean'
        unbound_field = TestForm.base_fields[name]
        jsonfield = jsonfields.BooleanField(unbound_field,name)
        part = jsonfield.get_schema_part()
        print("json_part={}".format(part))
        self.assertEquals(part['title'],"A boolean")
        self.assertEquals(part['type'],'boolean')
        self.assertEquals(part['description'],'')
