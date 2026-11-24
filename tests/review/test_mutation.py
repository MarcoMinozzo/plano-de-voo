"""A mutação do módulo puro precisa ser morta pelos testes."""

import json
import subprocess
import sys
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

ROOT = Path(__file__).resolve().parents[2]


def test_mutation_score():
    config = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["tool"]["suite"]["review"]
    minimum = float(config["min_mutation_score"])
    completed = subprocess.run([sys.executable, "-m", "mutmut", "run"], cwd=ROOT, check=False)
    assert completed.returncode == 0, "a mutação não terminou"
    exported = subprocess.run(
        [sys.executable, "-m", "mutmut", "export-cicd-stats"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert exported.returncode == 0, exported.stderr
    stats = json.loads((ROOT / "mutants" / "mutmut-cicd-stats.json").read_text(encoding="utf-8"))
    tested = int(stats["total"]) - int(stats["skipped"])
    killed = int(stats["killed"]) + int(stats["timeout"])
    score = 0.0 if tested <= 0 else 100.0 * killed / tested
    assert int(stats["no_tests"]) == 0, stats
    assert score >= minimum, f"escore de mutação {score:.1f}% abaixo de {minimum:.0f}%\n{stats}"
