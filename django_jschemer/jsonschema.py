import inspect
from django_jschemer.registry import field_registry


class DjangoFormToJSONSchema(object):
    """
    Converts a Form to a JSON schema
    """

    def __init__(self, schema_template=None):
        self.alpaca_options = {
            "fields": {},
            "helper": "",
        }

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

    def convert_to_schema(self,form):
        """
        Converts the Form to a JSON Schema object and Alpaca options
        and caches the results to instance variables.
        """

        fields = form.base_fields
        # If a Form instance is given, use the 'fields' attribute if it exists
        # since instances are allowed to modify them.
        if not inspect.isclass(form) and hasattr(form, 'fields'):
            fields = form.fields

        required_fields = []
        for name, field in list(fields.items()):
            # TODO we should check the form for inner class of extra options
            # and pass them as extra_options param
            part,options = self.convert_formfield(field,name)
            self.json_schema['properties'][name] = part
            self.alpaca_options['fields'][name] = options
            if field.required:
                required_fields.append(name)
        # if we have required fields, add them to the Schema
        if required_fields:
            self.json_schema['required'] = required_fields

        self._cached = True
        return self.json_schema, self.alpaca_options

    input_type_map = {
        'text': 'string',
    }

    def convert_formfield(self, field, name,extra_options=None):
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
        return part , options


class DjangoModelToJSONSchema(DjangoFormToJSONSchema):
    def convert_model(self, model, json_schema=None):
        model_form = None   # TODO convert to model form
        # TODO handle many2many and inlines
        return self.convert_form(model_form, json_schema)
