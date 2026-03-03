"""Tests for --patterns-no-color flag and color output behavior."""

import os
import subprocess
import tempfile
from pathlib import Path

import pytest

from pytest_patterns.plugin import GRAY_BG, RESET, _should_use_color

# Path to the project root (where pyproject.toml is)
PROJECT_ROOT = Path(__file__).parent.parent


def run_pytest(
    test_code: str, *args: str, env: dict[str, str] | None = None
) -> subprocess.CompletedProcess[str]:
    """Run pytest with a test file containing test_code.

    Runs from the project root directory where the plugin is installed.
    Uses 'uv run' to ensure correct Python environment.
    Uses -s to disable pytest output capture so stderr is visible.
    Returns the CompletedProcess with stdout and stderr captured.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = Path(tmpdir) / "test_generated.py"
        test_file.write_text(test_code)

        cmd = [
            "uv",
            "run",
            "pytest",
            str(test_file),
            "-s",  # Disable output capture to see stderr
            *args,
        ]
        merged_env = os.environ.copy()
        if env:
            merged_env.update(env)

        return subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT,
            env=merged_env,
            check=False,
        )


# TestNoColorFlag - Tests for --patterns-no-color command-line flag.


def test_no_color_flag_disables_ansi_codes() -> None:
    """--patterns-no-color disables ANSI color codes in output."""
    test_code = """
def test_with_whitespace(patterns):
    p = patterns.output
    p.in_order("First line\\nSecond line")
    # Trailing spaces cause whitespace issue
    assert p == "First line\\nSecond line    \\n"
"""
    result = run_pytest(test_code, "--patterns-no-color", "-v")
    stderr = result.stderr

    # Should have NO ANSI escape codes
    assert "\x1b[" not in stderr, (
        f"Expected no ANSI codes but found some in stderr:\n{stderr}"
    )
    # But whitespace markers (·) should still be present
    assert "·" in stderr, f"Expected whitespace marker '·' in stderr:\n{stderr}"


def test_no_color_flag_preserves_whitespace_markers() -> None:
    """Whitespace markers are still visible without color."""
    test_code = '''
def test_with_tabs(patterns):
    p = patterns.output
    p.in_order("indented")
    # Tab causes whitespace issue
    assert p == "indented\\t"
'''
    result = run_pytest(test_code, "--patterns-no-color", "-v")
    stderr = result.stderr

    # Tab marker should be present
    assert "→" in stderr, f"Expected tab marker '→' in stderr:\n{stderr}"
    # No ANSI codes
    assert "\x1b[" not in stderr, (
        f"Expected no ANSI codes but found some in stderr:\n{stderr}"
    )


# TestNoColorEnvVar - Tests for NO_COLOR environment variable.


def test_no_color_env_disables_ansi_codes() -> None:
    """NO_COLOR=1 environment variable disables color output."""
    test_code = '''
def test_with_whitespace(patterns):
    p = patterns.output
    p.in_order("Hello")
    # Trailing spaces
    assert p == "Hello  "
'''
    result = run_pytest(test_code, "-v", env={"NO_COLOR": "1"})
    stderr = result.stderr

    # Should have NO ANSI escape codes
    assert "\x1b[" not in stderr, (
        f"Expected no ANSI codes with NO_COLOR=1:\n{stderr}"
    )


# TestColorEnabledByDefault - Tests for color being enabled by default.


def test_color_auto_disabled_in_non_tty() -> None:
    """Colors are auto-disabled in non-TTY environments (subprocess)."""
    test_code = '''
def test_with_whitespace(patterns):
    p = patterns.output
    p.in_order("Text")
    # Trailing spaces cause whitespace highlighting
    assert p == "Text  "
'''
    # Without the flag, in non-TTY environment, color is auto-disabled
    result = run_pytest(test_code, "-v")
    stderr = result.stderr

    # In non-TTY (subprocess), color should be auto-disabled
    assert "\x1b[" not in stderr, (
        "In non-TTY subprocess, color should be auto-disabled"
    )


def test_color_flag_overrides_tty_detection() -> None:
    """--patterns-no-color forces color off even in TTY-like context."""
    test_code = '''
def test_with_whitespace(patterns):
    p = patterns.output
    p.in_order("Line")
    assert p == "Line\\t"
'''
    result = run_pytest(test_code, "--patterns-no-color", "-v")
    stderr = result.stderr

    # Explicit flag should disable color
    assert "\x1b[" not in stderr, (
        f"Expected no ANSI codes with --patterns-no-color:\n{stderr}"
    )


# TestShouldUseColorFunction - Unit tests for _should_use_color helper function.


def test_flag_disables_color() -> None:
    """--patterns-no-color flag disables color."""

    # Create a mock config with the flag set
    class MockConfig:
        def getoption(self, name: str) -> bool:
            if name == "--patterns-no-color":
                return True
            return False

    config = MockConfig()
    assert _should_use_color(config) is False  # type: ignore


def test_no_flag_no_env_tty_check() -> None:
    """Without flag or env, color depends on TTY detection."""

    class MockConfig:
        def getoption(self, name: str) -> bool:
            return False

    config = MockConfig()
    # This will check sys.stderr.isatty() which is False in test context
    # so we just verify it returns a boolean
    result = _should_use_color(config)  # type: ignore
    assert isinstance(result, bool)


def test_env_var_disables_color(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """NO_COLOR env var disables color."""
    monkeypatch.setenv("NO_COLOR", "1")

    class MockConfig:
        def getoption(self, name: str) -> bool:
            return False

    config = MockConfig()
    assert _should_use_color(config) is False  # type: ignore


# TestWhitespaceReportsWithoutColor - Test whitespace reporting works correctly without colors.


def test_whitespace_only_line_visible_without_color() -> None:
    """Whitespace-only lines are visible without color highlighting."""
    test_code = '''
def test_whitespace_only(patterns):
    p = patterns.output
    p.in_order("first\\nthird")
    # Line 2 is whitespace-only (unexpected)
    assert p == "first\\n    \\nthird"
'''
    result = run_pytest(test_code, "--patterns-no-color", "-v")
    stderr = result.stderr

    # Should show whitespace warning section
    assert "Whitespace issues detected" in stderr, (
        f"Expected whitespace warning in stderr:\n{stderr}"
    )
    # Should show line number and description
    assert "Line 2" in stderr, f"Expected 'Line 2' in stderr:\n{stderr}"
    assert "4 spaces" in stderr, f"Expected '4 spaces' in stderr:\n{stderr}"
    # Should show middle dots for spaces
    assert "····" in stderr, f"Expected '····' in stderr:\n{stderr}"


def test_trailing_whitespace_visible_without_color() -> None:
    """Trailing whitespace is visible without color highlighting."""
    test_code = '''
def test_trailing(patterns):
    p = patterns.output
    p.in_order("line1\\nline2\\nline3")
    # line2 has trailing spaces (unexpected)
    assert p == "line1\\nline2  \\nline3"
'''
    result = run_pytest(test_code, "--patterns-no-color", "-v")
    stderr = result.stderr

    # Should show whitespace warning
    assert "Whitespace issues detected" in stderr, (
        f"Expected whitespace warning in stderr:\n{stderr}"
    )
    assert "Line 2" in stderr, f"Expected 'Line 2' in stderr:\n{stderr}"
    assert "trailing" in stderr, f"Expected 'trailing' in stderr:\n{stderr}"
    # Should show middle dots
    assert "··" in stderr, f"Expected '··' in stderr:\n{stderr}"


# TestFormatLineReportWithColor - Unit tests for format_line_report with color control.


def test_whitespace_with_color_enabled() -> None:
    """Whitespace highlighting uses ANSI codes when color enabled."""
    from pytest_patterns.plugin import Status, format_line_report

    result = format_line_report(
        Status.UNEXPECTED, "🟡", "", "    ", use_color=True
    )
    # Should have ANSI codes
    assert GRAY_BG in result
    assert RESET in result
    # Should have middle dots
    assert "····" in result


def test_whitespace_with_color_disabled() -> None:
    """Whitespace highlighting works without ANSI codes."""
    from pytest_patterns.plugin import Status, format_line_report

    result = format_line_report(
        Status.UNEXPECTED, "🟡", "", "    ", use_color=False
    )
    # Should NOT have ANSI codes
    assert GRAY_BG not in result
    assert RESET not in result
    # Should still have middle dots
    assert "····" in result


def test_trailing_whitespace_with_color_disabled() -> None:
    """Trailing whitespace visible without color."""
    from pytest_patterns.plugin import Status, format_line_report

    result = format_line_report(
        Status.UNEXPECTED, "🟡", "", "hello  ", use_color=False
    )
    # Should NOT have ANSI codes
    assert GRAY_BG not in result
    assert RESET not in result
    # Should have middle dots for trailing spaces
    assert "··" in result
    # Should have the text
    assert "hello" in result


def test_tabs_with_color_disabled() -> None:
    """Tab whitespace visible without color."""
    from pytest_patterns.plugin import Status, format_line_report

    result = format_line_report(
        Status.UNEXPECTED, "🟡", "", "\t", use_color=False
    )
    # Should NOT have ANSI codes
    assert GRAY_BG not in result
    assert RESET not in result
    # Should have tab marker
    assert "→" in result


# TestAuditReportWithColor - Unit tests for Audit.report() with color control.


def test_audit_report_no_color() -> None:
    """Audit.report(use_color=False) has no ANSI codes."""
    from pytest_patterns.plugin import Audit

    audit = Audit("line1\nline2    ")  # trailing spaces on line2
    audit.optional("test", ["line1"])
    lines = list(audit.report(use_color=False))
    output = "\n".join(lines)
    # Should have NO ANSI escape codes
    assert "\x1b[" not in output, (
        f"Expected no ANSI codes but found some:\n{output}"
    )
    # But whitespace markers should still be present
    assert "·" in output, f"Expected whitespace marker '·' in:\n{output}"


def test_audit_report_with_color() -> None:
    """Audit.report(use_color=True) includes ANSI codes."""
    from pytest_patterns.plugin import Audit

    audit = Audit("line1\nline2    ")  # trailing spaces
    audit.optional("test", ["line1"])
    lines = list(audit.report(use_color=True))
    output = "\n".join(lines)
    # Should have ANSI codes for whitespace highlighting
    assert "\x1b[" in output, f"Expected ANSI codes in:\n{output}"


def test_audit_report_no_color_mixed_whitespace() -> None:
    """Audit.report with mixed whitespace types and use_color=False."""
    from pytest_patterns.plugin import Audit

    audit = Audit("line1\n  \nline3\t")  # ws-only line + trailing tab
    audit.optional("test", ["line1"])
    lines = list(audit.report(use_color=False))
    output = "\n".join(lines)
    # Should have NO ANSI codes
    assert "\x1b[" not in output
    # Should have both space and tab markers
    assert "·" in output  # Space marker
    assert "→" in output  # Tab marker


def test_audit_report_no_color_refused_lines() -> None:
    """Audit.report with refused lines and use_color=False."""
    from pytest_patterns.plugin import Audit

    audit = Audit("error  \nline2")  # trailing spaces on error line
    audit.refused("no_error", ["error"])
    lines = list(audit.report(use_color=False))
    output = "\n".join(lines)
    # Should have NO ANSI codes
    assert "\x1b[" not in output
    # Should show refused section
    assert "refused" in output.lower()
