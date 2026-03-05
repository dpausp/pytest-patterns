"""Tests for whitespace highlighting feature."""

from pytest_patterns.plugin import (
    Audit,
    Status,
    describe_whitespace,
    format_line_report,
)

# --- describe_whitespace helper tests ---


def test_describe_whitespace_no_issue_normal_line() -> None:
    """Normal line without whitespace issues returns None."""
    assert describe_whitespace("Hello World") is None


def test_describe_whitespace_no_issue_empty_line() -> None:
    """Empty line is not a whitespace issue."""
    assert describe_whitespace("") is None


def test_describe_whitespace_no_issue_no_trailing() -> None:
    """Line without trailing whitespace is fine."""
    assert describe_whitespace("  indented text") is None


def test_describe_whitespace_only_spaces() -> None:
    """Line with only spaces describes the count."""
    assert describe_whitespace("    ") == "4 spaces"


def test_describe_whitespace_only_tabs() -> None:
    """Line with only tabs describes the count."""
    assert describe_whitespace("\t\t") == "2 tabs"


def test_describe_whitespace_only_mixed() -> None:
    """Line with mixed whitespace describes composition."""
    result = describe_whitespace("  \t  ")
    assert result == "2 spaces + 1 tab + 2 spaces"


def test_describe_whitespace_trailing_spaces() -> None:
    """Trailing spaces are detected."""
    assert describe_whitespace("hello  ") == "trailing 2 spaces"


def test_describe_whitespace_trailing_tabs() -> None:
    """Trailing tabs are detected."""
    assert describe_whitespace("hello\t") == "trailing 1 tab"


def test_describe_whitespace_trailing_mixed() -> None:
    """Trailing mixed whitespace is detected."""
    assert describe_whitespace("hello  \t") == "trailing 2 spaces + 1 tab"


# --- format_line_report tests ---


def test_format_line_report_normal_line_unchanged() -> None:
    """Normal unexpected line uses control pictures."""
    result = format_line_report(Status.UNEXPECTED, "🟡", "", "hello")
    assert "hello" in result
    assert "[" not in result  # No annotation


def test_format_line_report_whitespace_only_annotated() -> None:
    """Whitespace-only line gets highlighted with markers."""
    result = format_line_report(Status.UNEXPECTED, "🟡", "", "    ")
    assert "····" in result  # 4 middle dots for 4 spaces


def test_format_line_report_trailing_whitespace_annotated() -> None:
    """Trailing whitespace gets highlighted with markers."""
    result = format_line_report(Status.UNEXPECTED, "🟡", "", "hello  ")
    assert "··" in result  # 2 middle dots for 2 trailing spaces


def test_format_line_report_expected_line_no_annotation() -> None:
    """Expected lines don't get whitespace highlighting."""
    result = format_line_report(Status.EXPECTED, "🟢", "pattern", "    ")
    assert "·" not in result
    assert "\x1b[100m" not in result


def test_format_line_report_gray_background_applied() -> None:
    """Whitespace-only lines get gray background ANSI code."""
    result = format_line_report(Status.UNEXPECTED, "🟡", "", "    ")
    # Gray background: \x1b[100m, Reset: \x1b[0m
    assert "\x1b[100m" in result
    assert "\x1b[0m" in result


# --- Audit whitespace warning tests ---


def test_audit_no_warning_when_no_whitespace_issues() -> None:
    """No warning section when no whitespace issues."""
    audit = Audit("hello\nworld\nfoo")
    audit.in_order("test", ["hello", "world", "foo"])
    report_lines = list(audit.report())
    assert not any("Whitespace issues" in line for line in report_lines)


def test_audit_warning_for_whitespace_only_unexpected() -> None:
    """Warning section appears for whitespace-only unexpected lines."""
    audit = Audit("hello\n    \nworld")
    audit.in_order("test", ["hello", "world"])
    report_text = "\n".join(audit.report())

    assert "Whitespace issues detected" in report_text
    assert "Line 2" in report_text
    assert "4 spaces" in report_text


def test_audit_warning_for_trailing_whitespace_unexpected() -> None:
    """Warning for trailing whitespace on unexpected lines."""
    audit = Audit("hello\nworld  \nfoo")
    audit.in_order("test", ["hello", "world", "foo"])
    report_text = "\n".join(audit.report())

    assert "Whitespace issues detected" in report_text


def test_audit_warning_for_unmatched_whitespace_pattern() -> None:
    """Warning when expected whitespace pattern doesn't match."""
    audit = Audit("hello\n\nworld")  # Empty line, not "    "
    audit.in_order("test", ["hello", "    ", "world"])
    report_text = "\n".join(audit.report())

    assert "    " in report_text or "4 spaces" in report_text


def test_audit_multiple_whitespace_issues_listed() -> None:
    """Multiple whitespace issues are all listed."""
    audit = Audit("hello\n    \nworld\n\t\t\nfoo")
    audit.in_order("test", ["hello", "world", "foo"])
    report_text = "\n".join(audit.report())

    assert "Line 2" in report_text
    assert "Line 4" in report_text


# --- Integration tests ---


def test_whitespace_only_line_mismatch() -> None:
    """Detect when whitespace-only line doesn't match expected."""
    from pytest_patterns.plugin import PatternsLib

    patterns = PatternsLib()
    p = patterns.test
    p.in_order(
        """
line1
line2
"""
    )

    content = "line1\n    \nline2"
    audit = p._audit(content)

    assert not audit.is_ok()
    report_text = "\n".join(audit.report())
    assert "Whitespace" in report_text or "    " in report_text


def test_trailing_whitespace_caught() -> None:
    """Trailing whitespace causes match failure."""
    from pytest_patterns.plugin import PatternsLib

    patterns = PatternsLib()
    p = patterns.test
    p.in_order("hello")

    audit = p._audit("hello  ")
    assert not audit.is_ok()

    report_text = "\n".join(audit.report())
    assert (
        "trailing" in report_text.lower() or "whitespace" in report_text.lower()
    )


# --- Additional whitespace description tests ---


def test_describe_whitespace_components_empty() -> None:
    """Empty whitespace string returns empty."""
    from pytest_patterns.plugin import _describe_whitespace_components

    assert _describe_whitespace_components("", "") == ""


def test_describe_whitespace_components_other_whitespace() -> None:
    """Other whitespace characters (shouldn't happen often)."""
    from pytest_patterns.plugin import _describe_whitespace_components

    # Vertical tab - gets repr'd
    result = _describe_whitespace_components("\x0b", "")
    assert "'\\x0b'" in result or "1" in result  # Shows as repr or count


# --- Additional format_whitespace tests ---


def test_format_whitespace_spaces() -> None:
    """Spaces are converted to middle dots."""
    from pytest_patterns.plugin import _format_whitespace

    assert _format_whitespace("    ") == "····"


def test_format_whitespace_tabs() -> None:
    """Tabs are converted to right arrows."""
    from pytest_patterns.plugin import _format_whitespace

    assert _format_whitespace("\t\t") == "→→"


def test_format_whitespace_mixed() -> None:
    """Mixed whitespace formatting."""
    from pytest_patterns.plugin import _format_whitespace

    assert _format_whitespace(" \t ") == "·→·"


def test_format_whitespace_empty() -> None:
    """Empty string."""
    from pytest_patterns.plugin import _format_whitespace

    assert _format_whitespace("") == ""


def test_format_whitespace_other() -> None:
    """Other characters pass through."""
    from pytest_patterns.plugin import _format_whitespace

    assert _format_whitespace("x") == "x"


# --- Additional format_line_report tests ---


def test_format_line_report_expected() -> None:
    """Format expected line."""
    from pytest_patterns.plugin import format_line_report, Status

    result = format_line_report(
        Status.EXPECTED, "🟢", "pattern1", "line content"
    )
    assert "🟢" in result
    assert "pattern1" in result
    assert "line content" in result


def test_format_line_report_optional() -> None:
    """Format optional line."""
    from pytest_patterns.plugin import format_line_report, Status

    result = format_line_report(
        Status.OPTIONAL, "⚪️", "pattern1", "line content"
    )
    assert "⚪️" in result
    assert "pattern1" in result


def test_format_line_report_unexpected() -> None:
    """Format unexpected line."""
    from pytest_patterns.plugin import format_line_report, Status

    result = format_line_report(Status.UNEXPECTED, "🟡", "", "line content")
    assert "🟡" in result
    assert "line content" in result


def test_format_line_report_with_trailing_whitespace() -> None:
    """Format line with trailing whitespace (colored)."""
    from pytest_patterns.plugin import format_line_report, Status

    result = format_line_report(
        Status.UNEXPECTED,
        "🟡",
        "",
        "line   ",  # Display line (tabs replaced)
        "line   ",  # Original line
        use_color=True,
    )
    assert "🟡" in result
    assert "·" in result  # Whitespace marker


def test_format_line_report_with_trailing_whitespace_no_color() -> None:
    """Format line with trailing whitespace (no color)."""
    from pytest_patterns.plugin import format_line_report, Status

    result = format_line_report(
        Status.UNEXPECTED,
        "🟡",
        "",
        "line   ",
        "line   ",
        use_color=False,
    )
    assert "🟡" in result
    assert "·" in result  # Whitespace marker still shown
    assert "\x1b[" not in result  # No ANSI codes


def test_format_line_report_whitespace_only() -> None:
    """Format whitespace-only line."""
    from pytest_patterns.plugin import format_line_report, Status

    result = format_line_report(
        Status.UNEXPECTED,
        "🟡",
        "",
        "    ",
        "    ",
        use_color=True,
    )
    assert "🟡" in result
    assert "·" in result


def test_format_line_report_with_tabs() -> None:
    """Format line with trailing tabs."""
    from pytest_patterns.plugin import format_line_report, Status

    result = format_line_report(
        Status.UNEXPECTED,
        "🟡",
        "",
        "        ",  # Tab replaced with spaces
        "\t",  # Original has tab
        use_color=True,
    )
    assert "🟡" in result
    # Tab should be shown as arrow in the whitespace part
    assert "→" in result or "·" in result


def test_format_line_report_long_cause() -> None:
    """Format with long pattern name (truncated to 15 chars)."""
    from pytest_patterns.plugin import format_line_report, Status

    result = format_line_report(
        Status.EXPECTED, "🟢", "very_long_pattern_name", "line"
    )
    assert "very_long_patte" in result  # Truncated to 15


def test_format_line_report_no_original_line() -> None:
    """Format without original line (uses display line)."""
    from pytest_patterns.plugin import format_line_report, Status

    result = format_line_report(
        Status.UNEXPECTED,
        "🟡",
        "",
        "line  ",  # Only display line provided
        use_color=True,
    )
    assert "🟡" in result
    # Should still detect trailing whitespace from display line
    assert "·" in result


# --- Audit whitespace collection tests ---


def test_collect_whitespace_unexpected_trailing() -> None:
    """Collect trailing whitespace from unexpected lines."""
    from pytest_patterns.plugin import Audit

    audit = Audit("line  ")
    audit.in_order("pattern1", ["line"])  # Won't match due to trailing space
    issues = audit._collect_whitespace_issues()
    assert len(issues) > 0
    assert issues[0][0] == 1  # Line number
    assert "trailing" in issues[0][1]


def test_collect_whitespace_unexpected_only_whitespace() -> None:
    """Collect whitespace-only unexpected lines."""
    from pytest_patterns.plugin import Audit

    audit = Audit("   ")
    # Don't add any patterns so line stays unexpected
    issues = audit._collect_whitespace_issues()
    assert len(issues) > 0
    assert "spaces" in issues[0][1]


def test_collect_whitespace_unmatched_expected() -> None:
    """Collect whitespace from unmatched expected lines."""
    from pytest_patterns.plugin import Audit

    audit = Audit("line1")
    audit.in_order("pattern1", ["line1 "])  # Trailing space won't match
    issues = audit._collect_whitespace_issues()
    # Should detect whitespace in unmatched expectation
    assert any("trailing" in issue[1] for issue in issues)
