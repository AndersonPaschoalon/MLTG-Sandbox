class ReprMixin:
    """
    Mixin class that provides a human-friendly __repr__ with all instance attributes.

    Usage:
        Just inherit from ReprMixin in any class where you want a nice __repr__.
        It will automatically include all instance-level attributes in a clean format.
    """

    def __repr__(self):
        cls_name = self.__class__.__name__
        attrs = vars(self)
        if not attrs:
            return f"<{cls_name}()>"

        # Format each key=value pair
        formatted = ", ".join(f"{k}={v!r}" for k, v in attrs.items())
        return f"<{cls_name}({formatted})>"
