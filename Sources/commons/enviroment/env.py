import json
from pathlib import Path
from typing import Any


class Env:
    """
    Simple run-time environment / variable bag with dot-notation access
    and JSON persistence for primitive Python types.

    Supported value types
    ---------------------
    • int, float, str
    • list / tuple / dict that recursively contain any supported type
    """

    # ---------- internal helpers ---------- #
    @staticmethod
    def _encode(obj: Any):
        """Recursively convert Python objects → JSON-serialisable form."""
        if isinstance(obj, tuple):
            return {"__tuple__": [Env._encode(x) for x in obj]}
        if isinstance(obj, list):
            return [Env._encode(x) for x in obj]
        if isinstance(obj, dict):
            return {str(k): Env._encode(v) for k, v in obj.items()}
        return obj  # int, float, str are already JSON‑safe

    @staticmethod
    def _decode(obj: Any):
        """Recursively convert JSON-decoded objects back → Python objects."""
        if isinstance(obj, dict):
            if "__tuple__" in obj:
                return tuple(Env._decode(x) for x in obj["__tuple__"])
            return {k: Env._decode(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [Env._decode(x) for x in obj]
        return obj

    # ---------- core API ---------- #
    def __init__(self):
        super().__setattr__("_vars", {})  # avoid recursion in __setattr__

    def __getattr__(self, name):
        try:
            return self._vars[name]
        except KeyError:
            raise AttributeError(f"'Env' has no attribute '{name}'") from None

    def __setattr__(self, name, value):
        self._vars[name] = value

    def __delattr__(self, name):
        try:
            del self._vars[name]
        except KeyError:
            raise AttributeError(f"'Env' has no attribute '{name}'") from None

    # ---------- convenience ---------- #
    def list_vars(self):
        """Return a list of registered variable names."""
        return list(self._vars.keys())

    def dump(self):
        """Return a shallow copy of the internal dictionary."""
        return dict(self._vars)

    def clear(self):
        """Remove all stored variables."""
        self._vars.clear()

    # ---------- persistence ---------- #
    def save(self, path: str | Path):
        """
        Save the current environment to *path* (JSON).

        Example
        -------
        env.save("session.json")
        """
        path = Path(path)
        blob = Env._encode(self._vars)
        path.write_text(json.dumps(blob, indent=2))
        print(f"✔ Environment saved to {path}")

    def load(self, path: str | Path):
        """
        Load environment state from *path* (JSON).

        Example
        -------
        env.load("session.json")
        """
        path = Path(path)
        blob = json.loads(path.read_text())
        self._vars = Env._decode(blob)
        print(f"✔ Environment loaded from {path}")


if __name__ == "__main__":
    env = Env()

    # register values
    env.iteration = 3
    env.alpha = 0.01
    env.description = "test run"
    env.sizes = [64, 128, 256]
    env.settings = {"method": "iperf", "retry": (1, 2, 3)}

    # persist to disk
    env.save("my_env.json")

    # start fresh and restore
    new_env = Env()
    new_env.load("my_env.json")
    print(new_env.description)  # → "test run"
    print(new_env.settings["retry"])  # → (1, 2, 3)  ← tuple preserved!
