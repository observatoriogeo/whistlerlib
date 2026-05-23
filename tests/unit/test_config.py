"""Unit tests for `whistlerlib.config.config`.

The module reads two env vars at import. Tests use `monkeypatch` + module
reload to exercise both the "set" and "unset" paths cleanly.
"""

import importlib

from whistlerlib.config import config as config_module


def _reload_config(monkeypatch, **env):
    """Set/clear env vars, then reload the config module so it re-reads them."""
    for key in ('WHISTLERLIB_R_SCRIPTS_PATH', 'WHISTLERLIB_R_PATH'):
        if key in env:
            if env[key] is None:
                monkeypatch.delenv(key, raising=False)
            else:
                monkeypatch.setenv(key, env[key])
    return importlib.reload(config_module)


def test_both_env_vars_set(monkeypatch):
    mod = _reload_config(monkeypatch,
                         WHISTLERLIB_R_SCRIPTS_PATH='/srv/r-scripts',
                         WHISTLERLIB_R_PATH='/usr/bin')
    assert mod.R_SCRIPTS_PATH == '/srv/r-scripts'
    assert mod.R_PATH == '/usr/bin'


def test_both_env_vars_unset(monkeypatch):
    mod = _reload_config(monkeypatch,
                         WHISTLERLIB_R_SCRIPTS_PATH=None,
                         WHISTLERLIB_R_PATH=None)
    assert mod.R_SCRIPTS_PATH is None
    assert mod.R_PATH is None


def test_partial_set_one_var(monkeypatch):
    """Only WHISTLERLIB_R_PATH set; SCRIPTS_PATH unset → None."""
    mod = _reload_config(monkeypatch,
                         WHISTLERLIB_R_SCRIPTS_PATH=None,
                         WHISTLERLIB_R_PATH='/usr/bin')
    assert mod.R_SCRIPTS_PATH is None
    assert mod.R_PATH == '/usr/bin'


def test_import_does_not_raise_when_unset(monkeypatch):
    """Regression: pre-0.2 the module would `assert` and crash `import whistlerlib`
    when env vars weren't set. After Phase 1 it must just expose None."""
    monkeypatch.delenv('WHISTLERLIB_R_SCRIPTS_PATH', raising=False)
    monkeypatch.delenv('WHISTLERLIB_R_PATH', raising=False)
    # Reload must succeed even when neither var is set.
    importlib.reload(config_module)
