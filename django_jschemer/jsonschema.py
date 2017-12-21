import inspect
from collections import OrderedDict
from django_jschemer.registry import field_registry
from deepmerge import Merger


class DjangoFormToJSONSchema(object):
    """
    Converts a Form to a JSON schema.

    schema_template -- optionally specify a template for JSON SCHEMA
    form_key -- optionally specify a unique identifier for the schema.

    The reasoning for form_key is to allow multiple JSONSchemaFields in the
    same form:
        1. Enable Django view code to identify a JSONSchemaField and possibly
        associate it with a model or a specific Form class.
        2. Use it to namespace or otherwise separate a set of fields that
        belong to the same 'form' (using JS etc).
    Currently it is used in Schema's 'id' attribute.
    """

    def __init__(self, schema_template=None, form_key=None):
        self.alpaca_options = {
            "fields": {},
            "helper": "",
        }

        if schema_template:
            self.json_schema = schema_template
        else:
            self.json_schema = {
                # 'title':dockit_schema._meta
                # 'description'
                'type': 'object',
                'properties': OrderedDict(),
            }
        if form_key:
            self.json_schema['id'] = str(form_key)

    def convert_to_schema(self, form):
        """
        Converts the Form to a JSON Schema object and Alpaca options
        """

        fields = form.base_fields
        # If a Form instance is given, use the 'fields' attribute if it exists
        # since instances are allowed to modify them.
        if not inspect.isclass(form) and hasattr(form, 'fields'):
            fields = form.fields

        required_fields = []
        for name, field in list(fields.items()):
            part, options = self.convert_formfield(field, name)
            self.json_schema['properties'][name] = part
            self.alpaca_options['fields'][name] = options
            if field.required:
                required_fields.append(name)
        # if we have required fields, add them to the Schema
        if required_fields:
            self.json_schema['required'] = required_fields

        # Check the form for inner 'AlpacaOptions' class and update
        # dictionaries with any supplied options/schema.
        meta_options = getattr(form,"SchemerOptions",None)
        if meta_options:
            # We need merger because nested dicts don't update() automatically
            # and need to recurse. deepmerge module handles that for us.
            merger = Merger([ (dict,["merge"])], ["override"],["override"])
            self.alpaca_options = merger.merge(self.alpaca_options,
                                               getattr(meta_options,"options",{}))
            self.json_schema= merger.merge(self.json_schema,
                                           getattr(meta_options,"schema",{}))
        return self.json_schema, self.alpaca_options

    input_type_map = {
        'text': 'string',
    }

    def convert_formfield(self, field, name, extra_options=None):
        """
        Converts a form field to a (part,options) tuple where
        part is the JSON Schema part and options is the Alpaca Options
        dictionary part.
        extra_options -- extra Alpaca options to be applied to this field.
        """

        # We do not check for exceptions here.
        # should we let them propagate or should we have a sensible default?
        schemafield_cls = field_registry.get_schemafield(field)
        schemafield = schemafield_cls(field, name)

        part = schemafield.get_schema_part()
        options = schemafield.get_alpaca_options()
        if extra_options:
            options.update(extra_options)
        return part, options


class DjangoModelToJSONSchema(DjangoFormToJSONSchema):
    def convert_model(self, model, json_schema=None):
        model_form = None   # TODO convert to model form
        # TODO handle many2many and inlines
        return self.convert_form(model_form, json_schema)
