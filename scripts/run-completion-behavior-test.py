#!/usr/bin/env python3
import importlib.util
from pathlib import Path

source=Path(__file__).with_name('test-completion-behavior.py')
spec=importlib.util.spec_from_file_location('completion_behavior',source)
mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
original=mod.fixture
def fixture(base):
    Path(base).mkdir(parents=True,exist_ok=True)
    return original(Path(base))
mod.fixture=fixture
mod.main()
