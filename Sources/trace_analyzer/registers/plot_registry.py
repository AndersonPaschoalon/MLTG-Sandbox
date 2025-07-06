from typing import Any, Callable, Optional


# Refactored PlotRegistry with support for kwargs in call method
class PlotRegistry:
    _registry = {}

    @classmethod
    def register(cls, name: str, display_name: str, plot_fn: Callable, *args, **kwargs):
        cls._registry[name] = {
            "display_name": display_name,
            "plot_fn": plot_fn,
            "args": args,
            "kwargs": kwargs,
        }

    @classmethod
    def get_all(cls):
        return cls._registry

    @classmethod
    def call(cls, name: str, **call_kwargs) -> Optional[Any]:
        entry = cls._registry.get(name)
        if not entry:
            print(f"[ERROR] Plot '{name}' is not registered.")
            return None

        fn = entry["plot_fn"]
        args = entry.get("args", [])
        kwargs = entry.get("kwargs", {}).copy()
        kwargs.update(call_kwargs)
        return fn(*args, **kwargs)
