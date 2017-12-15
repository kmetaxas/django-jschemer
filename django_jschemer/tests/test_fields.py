import jsonschema
import unittest
from django.forms import Form
from django.forms import fields
from django.utils.translation import ugettext_lazy as _

from django_jschemer import fields as jsonfields

class TestForm(Form):

    CHOICES = (
        ("a","OPTION A"),
        ("b","OPTION B"),
        ("c","OPTION C"),
    )

    a_charfield = fields.CharField(max_length=20, min_length=4,
                                   initial="INITIAL_VALUE",
                                   help_text="HelpText")
    a_charfield_lazy = fields.CharField(max_length=20, min_length=4,
                                        label = _("Test Label"),
                                        help_text=_("HelpText"))
    a_url = fields.URLField(min_length=15)
    a_date = fields.DateField(label=_("Δοκιμή")) # Greek text
    a_datetime = fields.DateTimeField()
    a_time = fields.TimeField(label=_("TimeFieldTest"))
    an_integer = fields.IntegerField(
        label="IntegerTest",
        max_value=1000, min_value=10,
    )
    an_ipaddress = fields.GenericIPAddressField()
    a_boolean = fields.BooleanField()
    a_regex = fields.RegexField(label=_("A Regex"),
                                regex = r"\d+"
                                )
    a_choicefield = fields.ChoiceField(
        label="A Choice field",
        choices=CHOICES)


class FormFieldsTestCase(unittest.TestCase):

    def setUp(self):
        self.form = TestForm()

    def _create_schema_for_part(self,part,name):
        schema = {
            'type':'object',
            'required':[name],
            'properties':{}
        }
        schema['properties'][name] = part
        return schema


    def test_charfield(self):
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
        # test if initial value generates default
        self.assertEquals(part['default'],"INITIAL_VALUE")
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
        # Check if schema validates
        schema = self._create_schema_for_part(part,name)
        jsonschema.Draft4Validator.check_schema(schema)


        # Invalidate schema and check that it does *NOT* validate
        with self.assertRaises(jsonschema.exceptions.SchemaError):
            part['type'] = "TYPE_DOES_NOT_EXIST"
            schema = self._create_schema_for_part(part,name)
            jsonschema.Draft4Validator.check_schema(schema)

    def test_booleanfield(self):
        name = 'a_boolean'
        unbound_field = TestForm.base_fields[name]
        jsonfield = jsonfields.BooleanField(unbound_field,name)
        part = jsonfield.get_schema_part()
        print("json_part={}".format(part))
        self.assertEquals(part['title'],"A boolean")
        self.assertEquals(part['type'],'boolean')
        self.assertEquals(part['description'],'')
        # Check if schema validates
        schema = self._create_schema_for_part(part,name)
        jsonschema.Draft4Validator.check_schema(schema)


    def test_timefield(self):
        name = 'a_time'
        unbound_field = TestForm.base_fields[name]
        jsonfield = jsonfields.TimeField(unbound_field,name)
        part = jsonfield.get_schema_part()
        print("json_part={}".format(part))
        self.assertEquals(part['type'],'string')
        self.assertEquals(part['format'],'time')
        self.assertEquals(part['title'],'TimeFieldTest')
        # Check if schema validates
        schema = self._create_schema_for_part(part,name)
        jsonschema.Draft4Validator.check_schema(schema)

    def test_datefield(self):
        name = "a_date"
        unbound_field = TestForm.base_fields[name]
        jsonfield = jsonfields.DateField(unbound_field,name)
        part = jsonfield.get_schema_part()
        print("json_part={}".format(part))
        self.assertEquals(part['type'],'string')
        self.assertEquals(part['format'],'date')
        self.assertEquals(part['title'],'Δοκιμή')
        # Check if schema validates
        schema = self._create_schema_for_part(part,name)
        jsonschema.Draft4Validator.check_schema(schema)

    def test_datetimefield(self):
        name = "a_datetime"
        unbound_field = TestForm.base_fields[name]
        jsonfield = jsonfields.DateTimeField(unbound_field,name)
        part = jsonfield.get_schema_part()
        print("json_part={}".format(part))
        self.assertEquals(part['type'],'string')
        self.assertEquals(part['format'],'datetime')
        self.assertEquals(part['title'],'A datetime')
        # Check if schema validates
        schema = self._create_schema_for_part(part,name)
        jsonschema.Draft4Validator.check_schema(schema)

    def test_integerfield(self):
        name = "an_integer"
        unbound_field = TestForm.base_fields[name]
        jsonfield = jsonfields.IntegerField(unbound_field,name)
        part = jsonfield.get_schema_part()
        print("json_part={}".format(part))
        self.assertEquals(part['type'],'integer')
        self.assertEquals(part['title'],'IntegerTest')
        with self.assertRaises(KeyError):
            part['format']
        self.assertEquals(part['maximum'],1000)
        self.assertEquals(part['minimum'],10)
        #self.assertEquals(part['multipleOf'],1)
        # Check if schema validates
        schema = self._create_schema_for_part(part,name)
        jsonschema.Draft4Validator.check_schema(schema)

    def test_urlfield(self):
        name = "a_url"
        unbound_field = TestForm.base_fields[name]
        jsonfield = jsonfields.URLField(unbound_field,name)
        part = jsonfield.get_schema_part()
        print("json_part={}".format(part))
        self.assertEquals(part['type'],'string')
        self.assertEquals(part['format'],"uri")
        self.assertEquals(part['description'],"")
        self.assertEquals(part['title'],"A url")
        self.assertEquals(part['minLength'],15)
        with self.assertRaises(KeyError):
            part['maxLength']

        schema = self._create_schema_for_part(part,name)
        jsonschema.Draft4Validator.check_schema(schema)

    def test_genericipaddressfield(self):
        "GenericIpAddressField"
        name = "an_ipaddress"
        unbound_field = TestForm.base_fields[name]
        jsonfield = jsonfields.GenericIPAddressField(unbound_field,name)
        part = jsonfield.get_schema_part()
        print("json_part={}".format(part))
        self.assertEquals(part['type'],'string')
        self.assertEquals(part['format'],'ipv4')
        self.assertEquals(part['title'],'An ipaddress')
        self.assertEquals(part['description'],'')

        schema = self._create_schema_for_part(part,name)
        jsonschema.Draft4Validator.check_schema(schema)

    def test_regexfield(self):
        name = "a_regex"
        unbound_field = TestForm.base_fields[name]
        jsonfield = jsonfields.RegexField(unbound_field,name)
        part = jsonfield.get_schema_part()
        print("json_part={}".format(part))
        self.assertEquals(part['type'],'string')
        self.assertEquals(part['title'],'A Regex')

        schema = self._create_schema_for_part(part,name)
        jsonschema.Draft4Validator.check_schema(schema)
        # Apparently RegexField compiles regular expressions.
        # We should compare against uncompiled version (raw string)
        # self.assertEquals(part['regex'],r"\d+") 

    def test_choicefield(self):
        name = "a_choicefield"
        unbound_field = TestForm.base_fields[name]
        jsonfield = jsonfields.ChoiceField(unbound_field,name)
        print("jsonfield={}".format(jsonfield))
        part = jsonfield.get_schema_part()
        alpaca_options = jsonfield.get_alpaca_options({"custom1":"custom option"})
        print("alpaca_options={}".format(alpaca_options))
        # enum should be the zeroth index of the tuple
        enum = [choice[0] for choice in unbound_field.choices]
        choice_labels = [choice[1] for choice in unbound_field.choices]
        self.assertEquals(part['enum'],enum)
        self.assertEquals(alpaca_options['optionLabels'],choice_labels)
