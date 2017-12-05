from django.forms import widgets, fields
import inspect
from .registry import registry


def pretty_name(name):
    """
    Converts 'first_name' to 'First name'
    """
    if not name:
        return ''
        return name.replace('_', ' ').capitalize()


class DjangoFormToJSONSchema(object):

    def convert_form(self, form, json_schema=None):
        if json_schema is None:
            json_schema = {
                #'title':dockit_schema._meta
                #'description'
                'type': 'object',
                'properties': {}, #TODO SortedDict
            }

        fields = form.base_fields
        # If a Form instance is given, use the 'fields' attribute if it exists
        # since instances are allowed to modify them.
        if not inspect.isclass(form) and hasattr(form, 'fields'):
            fields = form.fields

        required_fields = []
        for name, field in list(fields.items()):
            json_schema['properties'][name] = self.convert_formfield(field,name)
            if field.required:
                required_fields.append(name)
        # if we have required fields, add them to the Schema
        if required_fields:
            json_schema['required'] = required_fields

        return json_schema

    input_type_map = {
        'text': 'string',
    }

    def convert_formfield(self,field,name):

        # We do not check for excptions here. 
        # should we let them propagate or should we have a sensible default?
        print("Field={}/name={}".format(field,name))
        schemafield_cls = registry.get_schemafield(field)
        schemafield = schemafield_cls(field,name)

        part = schemafield.get_schema_part()
        return part


    def convert_formfield_old(self, name, field):
        #TODO detect bound field
        widget = field.widget
        target_def = {
            'title': str(field.label) or pretty_name(name),
            'description': str(field.help_text),
        }
        # if field.required:                  #removed since it is not correct
        #     target_def['required'] = [name] #TODO this likely is not correct
        #TODO JSONSchemaField; include subschema and ref the type
        if isinstance(field, fields.URLField):
            target_def['type'] = 'string'
            target_def['format'] = 'url'
        elif isinstance(field, fields.FileField):
            target_def['type'] = 'string'
            target_def['format'] = 'uri'
        elif isinstance(field, fields.DateField):
            target_def['type'] = 'string'
            target_def['format'] = 'date'
        elif isinstance(field, fields.DateTimeField):
            target_def['type'] = 'string'
            target_def['format'] = 'datetime'
        elif isinstance(field, (fields.DecimalField, fields.FloatField)):
            target_def['type'] = 'number'
        elif isinstance(field, fields.IntegerField):
            target_def['type'] = 'integer'
        elif isinstance(field, fields.EmailField):
            target_def['type'] = 'string'
            target_def['format'] = 'email'
        elif isinstance(field, fields.NullBooleanField):
            target_def['type'] = 'boolean'
        elif isinstance(widget, widgets.CheckboxInput):
            target_def['type'] = 'boolean'
        elif isinstance(widget, widgets.Select):
            if widget.allow_multiple_selected:
                target_def['type'] = 'array'
            else:
                target_def['type'] = 'string'
            target_def['enum'] = [choice[0] for choice in field.choices]
        elif isinstance(widget, widgets.Input):
            translated_type = self.input_type_map.get(widget.input_type, 'string')
            target_def['type'] = translated_type
        else:
            target_def['type'] = 'string'
        return target_def

class DjangoModelToJSONSchema(DjangoFormToJSONSchema):
    def convert_model(self, model, json_schema=None):
        model_form = None #TODO convert to model form
        #TODO handle many2many and inlines
        return self.convert_form(model_form, json_schema)
