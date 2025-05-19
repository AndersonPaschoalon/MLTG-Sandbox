from commons.pylang.repr_mixin import ReprMixin


class MemoryStore(ReprMixin):
    """
    Lightweight runtime container for storing arbitrary objects
    with dot-notation access. Does not persist between runs.

    Usage:
    -------
    container = MemoryStore()
    container.df = pandas.DataFrame(...)
    container.model = MyModel(...)
    print(container.df)
    """

    def __init__(self):
        super().__setattr__("_vars", {})

    def __getattr__(self, name):
        try:
            return self._vars[name]
        except KeyError:
            raise AttributeError(f"'MemoryStore' has no attribute '{name}'") from None

    def __setattr__(self, name, value):
        self._vars[name] = value

    def __delattr__(self, name):
        try:
            del self._vars[name]
        except KeyError:
            raise AttributeError(f"'MemoryStore' has no attribute '{name}'") from None

    def list_vars(self):
        """Return a list of registered variable names."""
        return list(self._vars.keys())

    def dump(self):
        """Return a shallow copy of the internal object dictionary."""
        return dict(self._vars)

    def clear(self):
        """Clear all stored objects."""
        self._vars.clear()


if __name__ == "__main__":
    import pandas as pd

    class ComplexClass:
        def __init__(self, name):
            self.name = name

        @classmethod
        def complex_factory(cls, val):
            return cls(f"Hello {val}")

        def __repr__(self):
            return f"<ComplexClass name={self.name}>"

    container = MemoryStore()

    container.df = pd.DataFrame({"x": [1, 2], "y": [3, 4]})
    container.complex_class_obj = ComplexClass.complex_factory("World")
    container.simple_int = 1

    print(container.df)
    print(container.complex_class_obj)
    print(container.simple_int)
