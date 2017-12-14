import inspect
from django_jschemer.registry import field_registry


class DjangoFormToJSONSchema(object):
    """
    Converts a Form to a JSON schema
    """

    def __init__(self, form, schema_template=None):
        self.form = form
        self.alpaca_options = {}
        self._cached = False
        if schema_template:
            self.json_schema = schema_template
        else:
            self.json_schema = {
                # 'title':dockit_schema._meta
                # 'description'
                'type': 'object',
                'properties': {},  # TODO SortedDict
            }

    def convert_to_schema(self):
        """
        Converts Form to JSON SChema
        """
        self._convert()
        return self.json_schema

    def _convert(self):
        """
        Converts the Form to a JSON Schema object and Alpaca options
        and caches the results to instance variables.
        """

        form = self.form
        json_schema = self.json_schema
        fields = form.base_fields
        # If a Form instance is given, use the 'fields' attribute if it exists
        # since instances are allowed to modify them.
        if not inspect.isclass(form) and hasattr(form, 'fields'):
            fields = form.fields

        required_fields = []
        for name, field in list(fields.items()):
            json_schema['properties'][name] = self.convert_formfield(field, name)
            if field.required:
                required_fields.append(name)
        # if we have required fields, add them to the Schema
        if required_fields:
            json_schema['required'] = required_fields

        self.json_schema = json_schema
        self._cached = True
        return json_schema

    input_type_map = {
        'text': 'string',
    }

    def convert_formfield(self, field, name):

        # We do not check for exceptions here.
        # should we let them propagate or should we have a sensible default?
        print("Field={}/name={}".format(field, name))
        schemafield_cls = field_registry.get_schemafield(field)
        schemafield = schemafield_cls(field, name)

        part = schemafield.get_schema_part()
        return part


class DjangoModelToJSONSchema(DjangoFormToJSONSchema):
    def convert_model(self, model, json_schema=None):
        model_form = None   # TODO convert to model form
        # TODO handle many2many and inlines
        return self.convert_form(model_form, json_schema)
