"""Importing libraries should not create files or require plotting extras."""

import os
from pathlib import Path
import subprocess
import sys


def test_imports_are_read_only_without_plotting(tmp_path):
    script = """
import importlib.abc
from pathlib import Path
import sys

class NoPlotting(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname == 'matplotlib' or fullname.startswith('matplotlib.'):
            raise ModuleNotFoundError('Plotting is not installed')

sys.meta_path.insert(0, NoPlotting())
original_path = list(sys.path)
import family_screen
import run_demo
from mechanome import emit, schema, structural_screen
assert structural_screen.verify_energy_scale_consistency()['consistent']
assert structural_screen.verify_frozen_ranking()['passed']
assert sys.path == original_path
assert not list(Path.cwd().iterdir())
"""
    env = {**os.environ, "PYTHONPATH": str(Path(__file__).resolve().parents[1])}
    subprocess.run([sys.executable, "-c", script], cwd=tmp_path, env=env, check=True)
