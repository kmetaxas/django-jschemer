from django.forms.fields import Field as DjangoField
from .fields import BaseDjangoJSONSchemaField
import inspect


class JSONSchemaFieldRegistry(object):
    """
    A Class that acts as a Registry for available
    JSON Schema Fields.
    User can register new fields and associate a Class that it serves
    """

    def __init__(self):
        self._registry = {}

    def register(self, form_field_cls, jsonschema_field_cls):
        """
        Register a JSONSchema field class with an associated Django Forms field
        class.
        You must supply Class objects and not instances (just like Django admin
        register() )
        form_field_cls -- Django Forms Field class
        jsonschema_field_cls -- json schema Field class
        """

        if not inspect.isclass(form_field_cls):
            raise ValueError("form_field_cls is not a Class object")
        if not inspect.isclass(jsonschema_field_cls):
            raise ValueError("jsonschema_field_cls is not a Class object")
        if not issubclass(form_field_cls, DjangoField):
            raise ValueError("You must supply a subclass of djanfo.forms.fields.Field")
        if not issubclass(jsonschema_field_cls, BaseDjangoJSONSchemaField):
            raise ValueError("You must supply a subclass of BaseDjangoJSONSchemaField")

        if form_field_cls in self._registry:
            raise ValueError("Already registered")

        self._registry[form_field_cls] = jsonschema_field_cls

    def unregister(self, form_field_cls):
        """
        Unregister the given Django Field class
        """

        if not issubclass(form_field_cls, DjangoField):
            raise ValueError("You must supply a subclass of djanfo.forms.fields.Field")
        if form_field_cls not in self._registry:
            raise ValueError("class {} is Not registered".format(form_field_cls))
        del self._registry[form_field_cls]

    def get_schemafield(self, form_field):
        """
        Searches registry for the given Django Form field and returns the
        associated Schema Field if found.
        Returns None otherwise
        """
        return self._registry.get(form_field, None)


registry = JSONSchemaFieldRegistry()
