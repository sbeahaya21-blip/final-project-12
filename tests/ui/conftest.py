"""
When running pytest tests/ui:
- All UI test results (PASSED/FAILED) are shown in the terminal.
- The "running" line (test name as it starts) is shown only for test_user_journey_unittest.py.
"""
import pytest

USER_JOURNEY_MARKER = "test_user_journey_unittest"


class _FilteringTerminalReporter:
    """Shows all test results; shows the running/verbose line only for user journey tests."""

    def __init__(self, real_reporter, show_only_nodeid_part):
        self._real = real_reporter
        self._show_only = show_only_nodeid_part

    def _should_show_running(self, nodeid):
        return nodeid is not None and self._show_only in nodeid

    def __getattr__(self, name):
        return getattr(self._real, name)

    def pytest_runtest_logstart(self, nodeid, location):
        # Only show "test is starting" line for user journey; others run without that line
        if self._should_show_running(nodeid):
            self._real.pytest_runtest_logstart(nodeid, location)

    def pytest_runtest_logfinish(self, nodeid, **kwargs):
        pass

    def pytest_runtest_logreport(self, report):
        # Always show result (PASSED/FAILED) for every test so all UI tests appear in the terminal
        self._real.pytest_runtest_logreport(report)


def pytest_configure(config):
    # Only apply when running under tests/ui (invocation args contain 'ui')
    try:
        args = config.invocation_params.args or []
    except Exception:
        args = []
    if not any("ui" in str(a) for a in args):
        return
    # Store so we can wrap in sessionstart when reporter exists
    config._ui_show_only_user_journey = True


def pytest_sessionstart(session):
    if not getattr(session.config, "_ui_show_only_user_journey", False):
        return
    reporter = session.config.pluginmanager.get_plugin("terminalreporter")
    if reporter is None:
        return
    wrapper = _FilteringTerminalReporter(reporter, USER_JOURNEY_MARKER)
    session.config.pluginmanager.unregister(reporter)
    session.config.pluginmanager.register(wrapper, "terminalreporter")
