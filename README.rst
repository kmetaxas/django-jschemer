

============
Introduction
============

django-jschemer converts Django Forms into JSON Schema compatibile representations.

Originally a fork of https://github.com/zbyte64/django-jsonschema but it turned into a major rewrite.


------------
Requirements
------------

* Python 3 or later (not tested with 2.x)
* Django 1.8 or later, althought it should probably work in earlier versions


=====
Usage
=====


To convert a form to a JSON Schema::

    from django_jschemer.jsonschema import DjangoFormToJSONSchema
    
    schema_repr , alpaca_options = DjangoFormToJSONSchema().convert_form(MyForm)


If you have written your own custom Fields (django.forms.field.Field subclasses) then it is easy to add them
to django-jschemer using a method just like Django's admin registry:

You need to subclass django_schemer.fields.BaseDjangoJSONSchemaField and provide relevant method overrides.

overriding `def_type()` is required but everything else is optional. `get_type` should return a string with the JSON Schema 'type' field.

Example::

    class CustomSchemaField(BaseDjangoJSONSchemaField):
        
        def get_type(self):
            return "string"

        # optionally define a get_format() method
        def get_format(self):
            return "email"


There are now 2 ways to add this to the registry.

Method 1::

    from django_jschemer.registry import registry
    registry.register(YourCustomField,CustomSchemaField)

Method 2 (decorator)::

    from django_jschemer.decorators import register as schema_register

    @schema_register(CustomSchemaField)
    class MyCustomField(Field):
        # you field code here
        pass

    
To embed a JSON Schema as a form field::

    from django_jschemer.forms import JSONSchemaField
    
    #where schema is a python dictionay like schema_repr in the first exmaple
    
    class MyForm(forms.Form):
        subfield = JSONSchemaField(schema=schema)
    
    form = MyForm(data={'subfield':'<json encoded value>'})
    form.validate() #will validate the subfield entry against schema
    form['subfield'].as_widget() #will render a textarea widget with a data-schemajson attribute
