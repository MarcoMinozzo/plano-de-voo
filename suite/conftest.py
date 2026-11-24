"""Durante a mutação, importa a cópia em mutants e não o original."""

import sys
from pathlib import Path

_SKIP = {"tests", "suite", "__pycache__", ".pytest_cache", "mutants"}


def _prefer_mutants() -> None:
    here = Path(__file__).resolve()
    for parent in here.parents:
        if parent.name != "mutants":
            continue
        for child in parent.iterdir():
            if not child.is_dir() or child.name in _SKIP:
                continue
            if child.name in {"src", "scripts", "ferramentas"} or not (child / "__init__.py").exists():
                sys.path.insert(0, str(child))
            else:
                sys.path.insert(0, str(parent))
        original = parent.parent.resolve()
        blocked = {original, original / "src", original / "scripts", original / "ferramentas"}
        sys.path[:] = [item for item in sys.path if Path(item).resolve() not in blocked]
        return


_prefer_mutants()
