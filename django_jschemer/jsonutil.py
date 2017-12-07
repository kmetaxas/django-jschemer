from django.utils.functional import Promise
from django.utils.encoding import force_text
from django.core.serializers.json import DjangoJSONEncoder

# Encoder copies from:
# https://docs.djangoproject.com/en/1.11/topics/serialization/#serialization-formats-json


class LazyEncoder(DjangoJSONEncoder):
    """
    Custom encoder to force out the lazyness from ugettext strings
    """
    def default(self, obj):
        if isinstance(obj, Promise):
            return force_text(obj)
        return super(LazyEncoder,
                     self).default(obj)
