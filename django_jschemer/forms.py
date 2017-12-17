import json

from jsonschema import validate, FormatChecker,  ValidationError as JSONSchemaValidationError

from django import forms
from django.core.exceptions import ValidationError
from django_jschemer.jsonutil import LazyEncoder


class SchemaValidator(object):
    def __init__(self, schema):
        self.schema = schema

    def __call__(self, value):
        try:
            decoded_value = json.loads(value)
        except ValueError as error:
            raise ValidationError(str(error))
        try:
            validate(decoded_value,
                     self.schema,
                     format_checker=FormatChecker())
        except JSONSchemaValidationError as error:
            raise ValidationError('%s: %s' % ('.'.join(error.path), error.message))
        return value


class JSONSchemaFormWidget(forms.widgets.Textarea):
    """
    Custom widget that is hidden by default
    and has javascript to get the Alpaca form data on submit
    """
    print("JSONSchemaFormWidget init")

    class Media:
        # TODO load alpaca js/css here or leave it to the user?
        js = ('django_jschemer/jschemer_widget.js',)


class JSONSchemaField(forms.CharField):
    '''
    A django form field that takes in a schema definition and serializes the result in JSON.
    Renders to a textarea with a data-schemajson attribute containing the initial json .
    Javascript is loaded to convert the field into an Alpacajs powered form: http://www.alpacajs.org/

    Upon return validate the submission using python-jsonschema
    '''
    widget = JSONSchemaFormWidget

    def __init__(self, schema, options=None, **kwargs):
        self.schema = schema
        self.options = options
        super(JSONSchemaField, self).__init__(**kwargs)
        self.validators.append(SchemaValidator(schema=schema))

    def widget_attrs(self, widget):
        attrs = super(JSONSchemaField, self).widget_attrs(widget)
        attrs.update(self.get_data_attributes())
        return attrs

    def get_data_attributes(self):

        data_attr = {'data-schemajson': json.dumps(self.schema, cls=LazyEncoder)}
        if self.options:
            data_attr.update({'data-alpacaoptions': json.dumps(self.options)})
        return data_attr


# CONSIDER: a JSONSchemaForm that has a schema attribute and constructs the appropriate base_fields with JSONSchemaFields for the complex subfields.
#class MyForm(JSONSchemaForm): schema=schema; afield=forms.CharField()
#model forms infer that we should save these values and should be custom, likely utilizing a single JSONSchemaField
