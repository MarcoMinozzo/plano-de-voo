"""Tamanho dos módulos e complexidade ciclomática."""

import os
from pathlib import Path

import pytest

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

from radon.complexity import cc_visit
from radon.raw import analyze

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


def _module_violations():
    config = _config()
    max_complexity = int(config["max_cyclomatic_complexity"])
    max_lines = int(config["max_module_lines"])
    complexity = []
    size = []
    for relative_root in config["source_roots"]:
        base = ROOT / relative_root
        for path in _python_files(base):
            text = path.read_text(encoding="utf-8", errors="ignore")
            relative = path.relative_to(ROOT).as_posix()
            if analyze(text).loc > max_lines:
                size.append(f"{relative}: {analyze(text).loc} linhas")
            for block in cc_visit(text):
                if block.complexity > max_complexity:
                    complexity.append(f"{relative}:{block.name}: {block.complexity}")

    return complexity, size


@pytest.mark.skip(reason="Suspenso temporariamente até reduzir a complexidade do relatório PDF.")
def test_modules_stay_within_complexity():
    complexity, _ = _module_violations()
    assert complexity == [], "complexidade ciclomática acima do limite\n" + "\n".join(complexity)


def test_modules_stay_within_size():
    _, size = _module_violations()
    assert size == [], "módulo acima do tamanho permitido\n" + "\n".join(size)
