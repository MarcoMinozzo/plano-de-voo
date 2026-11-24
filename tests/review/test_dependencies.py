"""A estrutura de dependências não tem ciclo."""

import ast
import os
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

ROOT = Path(__file__).resolve().parents[2]
EXCLUDE = {".venv", "venv", "node_modules", "site-packages", "mutants", ".git", "__pycache__", ".specify", ".pytest_cache"}


def _config() -> dict:
    return tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["tool"]["suite"]["review"]


def _python_files(base: Path):
    for current, dirs, files in os.walk(base):
        dirs[:] = [name for name in dirs if name not in EXCLUDE]
        for name in files:
            if name.endswith(".py"):
                yield Path(current) / name


def _modules(config: dict) -> dict[str, Path]:
    found = {}
    module_root = ROOT / config["module_root"]
    for relative_root in config["source_roots"]:
        base = ROOT / relative_root
        for path in _python_files(base):
            relative = path.relative_to(module_root).with_suffix("")
            parts = list(relative.parts)
            if parts[-1] == "__init__":
                parts = parts[:-1]
            if not parts:
                continue
            found[".".join(parts)] = path
    return found


def _imports(path: Path, module: str, known: set[str]) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8", errors="ignore"))
    targets = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.level:
                parent = module.split(".")
                if path.name != "__init__.py":
                    parent = parent[:-1]
                parent = parent[: len(parent) - node.level + 1]
                name = ".".join(part for part in parent + ([node.module] if node.module else []) if part)
            else:
                name = node.module or ""
            if name in known or any(item.startswith(name + ".") for item in known):
                targets.add(name)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name in known or any(item.startswith(alias.name + ".") for item in known):
                    targets.add(alias.name)
    return targets


def _cycles(graph: dict[str, set[str]]) -> list[tuple[str, ...]]:
    found = []
    visiting = set()
    visited = set()
    stack = []

    def walk(module: str) -> None:
        if module in visited:
            return
        if module in visiting:
            found.append(tuple(stack[stack.index(module):] + [module]))
            return
        visiting.add(module)
        stack.append(module)
        for target in sorted(graph.get(module, ())):
            if target in graph:
                walk(target)
        stack.pop()
        visiting.remove(module)
        visited.add(module)

    for module in sorted(graph):
        walk(module)
    return found


def _signature(cycle: tuple[str, ...]) -> tuple[str, ...]:
    body = list(cycle)
    if body and body[0] == body[-1]:
        body = body[:-1]
    turns = [tuple(body[i:] + body[:i]) for i in range(len(body))]
    return min(turns)


def test_imports_have_no_new_cycles():
    config = _config()
    modules = _modules(config)
    graph = {name: _imports(path, name, set(modules)) for name, path in modules.items()}
    found = {_signature(cycle) for cycle in _cycles(graph)}
    allowed = {_signature(tuple(item)) for item in config.get("known_cycles", [])}
    extra = sorted(found - allowed)
    assert extra == [], "ciclo de importação novo\n" + "\n".join(" -> ".join(cycle) for cycle in extra)
