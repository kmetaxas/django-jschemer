def register(field_cls,registry=None):
    """
    Decorator that registers the decorated class with the supplied `field_cls`
    in the registry.
    If the registry is not supplid, the default registry.registry is used.
    """
    if not registry:
        from .registry import registry

    def _django_field_wrapper(jsonfield_cls):
        registry.register(field_cls,jsonfield_cls)
        return jsonfield_cls
    return _django_field_wrapper

