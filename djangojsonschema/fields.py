# Supported fields by django-jsonschema.
# Each class supports a single field and is responsible for generating the
# approriate JSON schema.

# If we need to specify options specific to the fields here, it might be a good
# idea to make an inner class (like class JSONSchema) and specifiy options
# there.
from .decorators import register
from django.forms import fields


class BaseDjangoJSONSchemaField(object):
    def __init__(self, field, name):
        """
        Initialize a JSON Schema representation object based on a Field
        field -- the form field object.
        name -- the name of the field object in the form.
        """
        self.field = field
        self.name = name
        self.label_suffix = field.label_suffix
        self.initial = field.initial
        self.widget = field.widget
        self.help_text = field.help_text
        self.error_messages = field.error_messages
        self.validators = field.validators
        self.localize = field.localize
        self.disabled = field.disabled

    def get_type(self):
        """
        Return the 'type' of field
        """
        raise NotImplementedError("Must override per field")

    def get_format(self):
        """
        Get the format for the field
        """
        return None

    def _pretty_name(self, name):
        """
        Converts 'first_name' to 'First name'
        """
        if not name:
            return ''
        return name.replace('_', ' ').capitalize()

    def get_label(self, label=None):
        if label:
            return label
        else:
            return self.field.label or self._pretty_name(self.name)

    def update_part(self, part):
        """
        Allow subclasses to update to json part according to their specific
        needs.
        It is called at the end of get_schema_part().
        part -- JSON part as built.
        Return value is the new part.
        """
        return None

    def get_schema_part(self):
        """
        Returns the schema definition for this field
        """
        part = {
            'title': str(self.get_label()),
            'description': str(self.help_text),
            'type': self.get_type(),
        }
        # if 'format' is specified, add it.
        t_format = self.get_format()
        if t_format:
            part['format'] = t_format
        return self.update_part(part) or part

    def get_alpaca_options(self):
        """
        Get an options object to be used with AlpacaJS.
        """
        # TODO this should be decoupled. Possibly using a different module
        # that subclasses the same fields using a Mix-In
        pass


@register(fields.BooleanField)
class BooleanField(BaseDjangoJSONSchemaField):

    def get_type(self):
        return "boolean"


@register(fields.NullBooleanField)
class NullBooleanField(BooleanField):
    # XXX How is Null value handled? needs testing
    pass


@register(fields.CharField)
class CharField(BaseDjangoJSONSchemaField):

    def get_type(self):
        return "string"

    def update_part(self, part):
        if self.field.max_length:
            part['maxLength'] = self.field.max_length
        if self.field.min_length:
            part['minLength'] = self.field.min_length
        return part


@register(fields.RegexField)
class RegexField(CharField):

    def update_part(self, part):
        part = super().update_part(part)
        part['regex'] = self.field.regex.pattern


@register(fields.URLField)
class URLField(CharField):

    def get_format(self):
        # is URL supported. For now URI
        return "uri"


@register(fields.UUIDField)
class UUIDField(BaseDjangoJSONSchemaField):

    def get_type(self):
        return "string"


@register(fields.DateField)
class DateField(BaseDjangoJSONSchemaField):

    def get_type(self):
        return "string"

    def get_format(self):
        return "date"


@register(fields.DateTimeField)
class DateTimeField(DateField):

    def get_format(self):
        return "datetime"


@register(fields.TimeField)
class TimeField(DateField):

    def get_format(self):
        return "time"


@register(fields.IntegerField)
class IntegerField(BaseDjangoJSONSchemaField):
    def get_type(self):
        return "integer"

    def update_part(self, part):
        if self.field.max_value:
            part['maximum'] = self.field.max_value
        if self.field.min_value:
            part['minimum'] = self.field.min_value

        # making sure it is an Integer is  a hack found here:
        # https://spacetelescope.github.io/understanding-json-schema/reference/numeric.html
        part['multipleOf'] = 1
        return part


@register(fields.DecimalField)
class DecimalField(IntegerField):
    def get_type(self):
        return "number"


@register(fields.EmailField)
class EmailField(CharField):
    def get_type(self):
        return "string"

    def get_format(self):
        return "email"


@register(fields.FileField)
class FileField(BaseDjangoJSONSchemaField):
    def get_type(self):
        return "string"
    # TODO this obviously would not work as is.


@register(fields.GenericIPAddressField)
class GenericIPAddressField(BaseDjangoJSONSchemaField):
    def get_type(self):
        return "string"

    def get_format(self):
        # XXX should we support IPV6? and how?
        return "ipv4"
