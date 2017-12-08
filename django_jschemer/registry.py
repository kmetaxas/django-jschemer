from django.forms import fields
#from django_jschemer.fields import BaseDjangoJSONSchemaField
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
        if not issubclass(form_field_cls, fields.Field):
            raise ValueError("You must supply a subclass of djanfo.forms.fields.Field")
#        if not issubclass(jsonschema_field_cls, BaseDjangoJSONSchemaField):
#            raise ValueError("You must supply a subclass of BaseDjangoJSONSchemaField")

        if form_field_cls in self._registry:
            raise ValueError("Already registered")

        self._registry[form_field_cls] = jsonschema_field_cls

    def unregister(self, form_field_cls):
        """
        Unregister the given Django Field class
        """

        if not issubclass(form_field_cls, fields.Field):
            raise ValueError("You must supply a subclass of djanfo.forms.fields.Field")
        if form_field_cls not in self._registry:
            raise ValueError("class {} is Not registered".format(form_field_cls))
        del self._registry[form_field_cls]

    def get_schemafield(self, form_field):
        """
        Searches registry for the given Django Form field and returns the
        associated Schema Field if found.
        Returns None otherwise

        It will search by class object which is the natural key but if passed,
        an instance object it will iterate over the registry keys trying to
        match them.
        """
        if inspect.isclass(form_field):
            return self._registry.get(form_field, None)
        if isinstance(form_field, fields.Field):
            instance_name = form_field.__class__.__name__
            for key,value in self._registry.items():
                # This feels like a hack. I don't think there is a better way.
                # isinstance() will not work because all key are subclasses of
                # Field.
                key_name = key.__name__
                if key_name == instance_name:
                    return value
        raise KeyError("Unsupported field: {}".format(instance_name))

field_registry = JSONSchemaFieldRegistry()

# Import fields to trigger loading of default fields into registry
from django_jschemer import fields as schemafields
