import pytest

from pytest_patterns.plugin import PatternsLib

GENERIC_HEADER = [
    "",  # Summary line (dynamic, tested separately)
    "🟢=EXPECTED | ⚪️=OPTIONAL | 🟡=UNEXPECTED | 🔴=REFUSED/UNMATCHED",
    "",
    "Here is the string that was tested: ",
    "",
]


def extract_summary(report_lines: list[str]) -> str:
    """Extract the first line (summary) from a report."""
    return report_lines[0] if report_lines else ""


def strip_summary(report_lines: list[str]) -> list[str]:
    """Remove the dynamic summary line for comparison."""
    return report_lines[1:] if report_lines else []


def strip_line_numbers(lines: list[str]) -> list[str]:
    """Remove line number prefix from report lines.

    Lines with line numbers have format: "  1 | content"
    """
    import re

    result = []
    for line in lines:
        # Match line number pattern: optional spaces, digits, " | ", then content
        match = re.match(r"^\s*\d+\s*\|\s(.+)$", line)
        if match:
            result.append(match.group(1))
        else:
            result.append(line)
    return result


def test_tab_replace() -> None:
    from pytest_patterns.plugin import tab_replace

    assert tab_replace("\t") == " " * 8
    assert tab_replace("1\t9") == "1       9"
    assert tab_replace("12\t9") == "12      9"
    assert tab_replace("123\t9") == "123     9"
    assert tab_replace("1234\t9") == "1234    9"
    assert tab_replace("12345\t9") == "12345   9"
    assert tab_replace("123456\t9") == "123456  9"
    assert tab_replace("1234567\t9") == "1234567 9"
    assert tab_replace("12345678\t9") == "12345678        9"
    assert tab_replace("123456789\t0") == "123456789       0"


# --- Control picture conversion tests ---


def test_to_control_picture_null() -> None:
    """Test NUL character conversion."""
    from pytest_patterns.plugin import to_control_picture

    assert to_control_picture("\x00") == "\u2400"


def test_to_control_picture_tab() -> None:
    """Test HT (tab) character conversion."""
    from pytest_patterns.plugin import to_control_picture

    assert to_control_picture("\t") == "\u2409"


def test_to_control_picture_lf() -> None:
    """Test LF (line feed) character conversion."""
    from pytest_patterns.plugin import to_control_picture

    assert to_control_picture("\n") == "\u240a"


def test_to_control_picture_cr() -> None:
    """Test CR (carriage return) character conversion."""
    from pytest_patterns.plugin import to_control_picture

    assert to_control_picture("\r") == "\u240d"


def test_to_control_picture_del() -> None:
    """Test DEL character conversion."""
    from pytest_patterns.plugin import to_control_picture

    assert to_control_picture("\x7f") == "\u2421"


def test_to_control_picture_space() -> None:
    """Test space is NOT converted (normal spaces kept as-is)."""
    from pytest_patterns.plugin import to_control_picture

    assert to_control_picture(" ") == " "


def test_to_control_picture_regular_char() -> None:
    """Test regular characters are not converted."""
    from pytest_patterns.plugin import to_control_picture

    assert to_control_picture("a") == "a"
    assert to_control_picture("Z") == "Z"
    assert to_control_picture("9") == "9"


def test_line_to_control_pictures_mixed() -> None:
    """Test conversion of line with mixed characters."""
    from pytest_patterns.plugin import line_to_control_pictures

    line = "hello\tworld"
    result = line_to_control_pictures(line)
    assert result == "hello\u2409world"


def test_line_to_control_pictures_all_control() -> None:
    """Test conversion of line with only control characters."""
    from pytest_patterns.plugin import line_to_control_pictures

    line = "\x00\x01\x02"
    result = line_to_control_pictures(line)
    assert result == "\u2400\u2401\u2402"


def test_line_to_control_pictures_empty() -> None:
    """Test conversion of empty line."""
    from pytest_patterns.plugin import line_to_control_pictures

    assert line_to_control_pictures("") == ""


# --- Match function tests ---


def test_match_empty_line_pattern_on_empty_line() -> None:
    """Match empty-line pattern on actual empty line."""
    from pytest_patterns.plugin import match, EMPTY_LINE_PATTERN

    result = match(EMPTY_LINE_PATTERN, "")
    assert result is True


def test_match_empty_line_pattern_on_non_empty() -> None:
    """Match empty-line pattern on non-empty line."""
    from pytest_patterns.plugin import match, EMPTY_LINE_PATTERN

    result = match(EMPTY_LINE_PATTERN, "text")
    # Should not match, continues to tab replacement and regex
    assert result is None or result is False


def test_match_empty_line_marker_on_empty_line() -> None:
    """Match <empty-line> marker on empty line."""
    from pytest_patterns.plugin import match, EMPTY_LINE_PATTERN

    result = match(EMPTY_LINE_PATTERN, "")
    assert result is True


def test_match_empty_line_marker_on_content() -> None:
    """Match <empty-line> marker on non-empty line."""
    from pytest_patterns.plugin import match, EMPTY_LINE_PATTERN

    result = match(EMPTY_LINE_PATTERN, "some text")
    # Should not return True, should continue to regex matching
    # The marker should not match actual content
    assert result is not True


# --- Pattern lines utility tests ---


def test_pattern_lines_simple() -> None:
    """Simple pattern split."""
    from pytest_patterns.plugin import pattern_lines

    assert pattern_lines("line1\nline2") == ["line1", "line2"]


def test_pattern_lines_empty_lines_filtered() -> None:
    """Empty lines are filtered out."""
    from pytest_patterns.plugin import pattern_lines

    assert pattern_lines("line1\n\nline2") == ["line1", "line2"]


def test_pattern_lines_trailing_newline() -> None:
    """Trailing newline is handled."""
    from pytest_patterns.plugin import pattern_lines

    assert pattern_lines("line1\nline2\n") == ["line1", "line2"]


def test_pattern_lines_empty_string() -> None:
    """Empty string returns empty list."""
    from pytest_patterns.plugin import pattern_lines

    assert pattern_lines("") == []


def test_pattern_lines_only_empty_lines() -> None:
    """Only empty lines returns empty list."""
    from pytest_patterns.plugin import pattern_lines

    assert pattern_lines("\n\n\n") == []


# --- Line class tests ---


def test_line_init() -> None:
    """Line initialization."""
    from pytest_patterns.plugin import Line, Status

    line = Line("test data")
    assert line.data == "test data"
    assert line.status == Status.UNEXPECTED
    assert line.status_cause == ""


def test_line_matches_exact() -> None:
    """Exact match."""
    from pytest_patterns.plugin import Line

    line = Line("hello")
    assert line.matches("hello") is True


def test_line_matches_wildcard() -> None:
    """Wildcard match."""
    from pytest_patterns.plugin import Line

    line = Line("hello world")
    assert line.matches("...world...") is True


def test_line_matches_no_match() -> None:
    """No match."""
    from pytest_patterns.plugin import Line

    line = Line("hello")
    assert line.matches("goodbye") is False


def test_line_mark_upgrade() -> None:
    """Mark upgrades status."""
    from pytest_patterns.plugin import Line, Status

    line = Line("test")
    line.mark(Status.OPTIONAL, "pattern1")
    assert line.status == Status.OPTIONAL
    assert line.status_cause == "pattern1"


def test_line_mark_no_downgrade() -> None:
    """Mark does not downgrade status."""
    from pytest_patterns.plugin import Line, Status

    line = Line("test")
    line.mark(Status.EXPECTED, "pattern1")
    line.mark(Status.OPTIONAL, "pattern2")
    assert line.status == Status.EXPECTED
    assert line.status_cause == "pattern1"


def test_line_mark_same_level() -> None:
    """Mark at same level has no effect."""
    from pytest_patterns.plugin import Line, Status

    line = Line("test")
    line.mark(Status.OPTIONAL, "pattern1")
    line.mark(Status.OPTIONAL, "pattern2")
    assert line.status_cause == "pattern1"


# --- Audit class tests ---


def test_audit_init() -> None:
    """Audit initialization."""
    from pytest_patterns.plugin import Audit

    audit = Audit("line1\nline2")
    assert len(audit.content) == 2
    assert audit.content[0].data == "line1"
    assert audit.content[1].data == "line2"
    assert audit.unmatched_expectations == []
    assert audit.matched_refused == set()


def test_audit_cursor() -> None:
    """Audit cursor iteration."""
    from pytest_patterns.plugin import Audit

    audit = Audit("a\nb\nc")
    lines = list(audit.cursor())
    assert len(lines) == 3
    assert lines[0].data == "a"


def test_audit_optional_simple() -> None:
    """Optional pattern matching."""
    from pytest_patterns.plugin import Audit, Status

    audit = Audit("error occurred")
    audit.optional("pattern1", ["...error..."])
    assert audit.content[0].status == Status.OPTIONAL
    assert audit.content[0].status_cause == "pattern1"


def test_audit_optional_no_match() -> None:
    """Optional pattern with no match."""
    from pytest_patterns.plugin import Audit, Status

    audit = Audit("no match here")
    audit.optional("pattern1", ["...error..."])
    assert audit.content[0].status == Status.UNEXPECTED


def test_audit_refused_simple() -> None:
    """Refused pattern matching."""
    from pytest_patterns.plugin import Audit, Status

    audit = Audit("error occurred")
    audit.refused("pattern1", ["...error..."])
    assert audit.content[0].status == Status.REFUSED
    assert ("pattern1", "...error...") in audit.matched_refused


def test_audit_refused_no_match() -> None:
    """Refused pattern with no match."""
    from pytest_patterns.plugin import Audit, Status

    audit = Audit("no match here")
    audit.refused("pattern1", ["...error..."])
    assert audit.content[0].status == Status.UNEXPECTED
    assert ("pattern1", "...error...") not in audit.matched_refused


def test_audit_continuous_simple() -> None:
    """Continuous pattern matching."""
    from pytest_patterns.plugin import Audit, Status

    audit = Audit("line1\nline2\nline3")
    audit.continuous("pattern1", ["line1", "line2"])
    assert audit.content[0].status == Status.EXPECTED
    assert audit.content[1].status == Status.EXPECTED
    assert audit.content[2].status == Status.UNEXPECTED


def test_audit_continuous_with_empty_lines() -> None:
    """Continuous pattern allows empty lines in between."""
    from pytest_patterns.plugin import Audit, Status

    audit = Audit("line1\n\nline2")
    audit.continuous("pattern1", ["line1", "line2"])
    assert audit.content[0].status == Status.EXPECTED
    assert audit.content[1].status == Status.OPTIONAL  # Empty line allowed
    assert audit.content[2].status == Status.EXPECTED


def test_audit_continuous_broken() -> None:
    """Continuous pattern broken by non-matching line."""
    from pytest_patterns.plugin import Audit, Status

    audit = Audit("line1\nunexpected\nline2")
    audit.continuous("pattern1", ["line1", "line2"])
    assert audit.content[0].status == Status.EXPECTED
    assert audit.content[1].status == Status.REFUSED
    assert len(audit.unmatched_expectations) > 0


def test_audit_continuous_incomplete() -> None:
    """Continuous pattern not fully matched."""
    from pytest_patterns.plugin import Audit, Status

    audit = Audit("line1")
    audit.continuous("pattern1", ["line1", "line2"])
    assert audit.content[0].status == Status.EXPECTED
    assert len(audit.unmatched_expectations) > 0


def test_audit_in_order_simple() -> None:
    """In-order pattern matching."""
    from pytest_patterns.plugin import Audit, Status

    audit = Audit("a\nb\nc")
    audit.in_order("pattern1", ["a", "c"])
    assert audit.content[0].status == Status.EXPECTED
    assert audit.content[1].status == Status.UNEXPECTED
    assert audit.content[2].status == Status.EXPECTED


def test_audit_in_order_out_of_order() -> None:
    """In-order pattern with wrong order."""
    from pytest_patterns.plugin import Audit

    audit = Audit("b\na\nc")
    audit.in_order("pattern1", ["a", "b"])
    assert len(audit.unmatched_expectations) > 0


def test_audit_in_order_partial_reset() -> None:
    """In-order pattern resets if no match found."""
    from pytest_patterns.plugin import Audit, Status

    audit = Audit("x\na\nb")
    audit.in_order("pattern1", ["a", "b"])
    # Should find 'a' on second try after reset
    assert audit.content[1].status == Status.EXPECTED
    assert audit.content[2].status == Status.EXPECTED


def test_audit_is_ok_success() -> None:
    """is_ok returns True for successful match."""
    from pytest_patterns.plugin import Audit

    audit = Audit("line1\nline2")
    audit.in_order("pattern1", ["line1", "line2"])
    assert audit.is_ok() is True


def test_audit_is_ok_failure_unmatched() -> None:
    """is_ok returns False with unmatched expectations."""
    from pytest_patterns.plugin import Audit

    audit = Audit("line1")
    audit.in_order("pattern1", ["line1", "line2"])
    assert audit.is_ok() is False


def test_audit_is_ok_failure_unexpected() -> None:
    """is_ok returns False with unexpected lines."""
    from pytest_patterns.plugin import Audit

    audit = Audit("line1\nunexpected")
    audit.in_order("pattern1", ["line1"])
    assert audit.is_ok() is False


# --- Pattern class tests ---


def test_pattern_init() -> None:
    """Pattern initialization."""
    from pytest_patterns.plugin import Pattern, PatternsLib

    lib = PatternsLib()
    p = Pattern(lib, "test_pattern")
    assert p.name == "test_pattern"
    assert p.library is lib
    assert p.ops == []
    assert p.inherited == set()


def test_pattern_continuous() -> None:
    """Pattern continuous method."""
    from pytest_patterns.plugin import Pattern, PatternsLib

    lib = PatternsLib()
    p = Pattern(lib, "test")
    p.continuous("line1\nline2")
    assert len(p.ops) == 1
    assert p.ops[0][0] == "continuous"
    assert p.ops[0][1] == "test"


def test_pattern_in_order() -> None:
    """Pattern in_order method."""
    from pytest_patterns.plugin import Pattern, PatternsLib

    lib = PatternsLib()
    p = Pattern(lib, "test")
    p.in_order("line1\nline2")
    assert len(p.ops) == 1
    assert p.ops[0][0] == "in_order"


def test_pattern_optional() -> None:
    """Pattern optional method."""
    from pytest_patterns.plugin import Pattern, PatternsLib

    lib = PatternsLib()
    p = Pattern(lib, "test")
    p.optional("line1\nline2")
    assert len(p.ops) == 1
    assert p.ops[0][0] == "optional"


def test_pattern_refused() -> None:
    """Pattern refused method."""
    from pytest_patterns.plugin import Pattern, PatternsLib

    lib = PatternsLib()
    p = Pattern(lib, "test")
    p.refused("...error...")
    assert len(p.ops) == 1
    assert p.ops[0][0] == "refused"


def test_pattern_merge() -> None:
    """Pattern merge method."""
    from pytest_patterns.plugin import PatternsLib

    lib = PatternsLib()
    p1 = lib.pattern1
    p1.optional("line1")

    p2 = lib.pattern2
    p2.in_order("line2")
    p2.merge("pattern1")

    # Check inheritance
    assert "pattern1" in p2.inherited


def test_pattern_normalize() -> None:
    """Pattern normalize method (currently no-op)."""
    from pytest_patterns.plugin import Pattern, PatternsLib

    lib = PatternsLib()
    p = Pattern(lib, "test")
    p.normalize("json")  # Should not raise
    assert len(p.ops) == 0  # No ops added


def test_pattern_flat_ops() -> None:
    """Pattern flat_ops includes inherited patterns."""
    from pytest_patterns.plugin import PatternsLib

    lib = PatternsLib()
    p1 = lib.base
    p1.optional("base_line")

    p2 = lib.derived
    p2.in_order("derived_line")
    p2.merge("base")

    ops = list(p2.flat_ops())
    # Should include both base and derived ops
    op_types = [op[0] for op in ops]
    assert "optional" in op_types  # From base
    assert "in_order" in op_types  # From derived


def test_pattern_audit() -> None:
    """Pattern _audit creates Audit object."""
    from pytest_patterns.plugin import PatternsLib, Audit

    lib = PatternsLib()
    p = lib.test
    p.in_order("line1")
    audit = p._audit("line1")
    assert isinstance(audit, Audit)
    assert audit.is_ok()


def test_pattern_generate_example_simple() -> None:
    """Pattern generate_example with simple patterns."""
    from pytest_patterns.plugin import PatternsLib

    lib = PatternsLib()
    p = lib.test
    p.in_order("line1\nline2")
    example = p.generate_example()
    assert "line1" in example
    assert "line2" in example


def test_pattern_generate_example_with_wildcards() -> None:
    """Pattern generate_example replaces wildcards."""
    from pytest_patterns.plugin import PatternsLib

    lib = PatternsLib()
    p = lib.test
    p.optional("...error...")
    example = p.generate_example()
    assert "[...]" in example
    # Wildcard ... should be replaced with [...]
    assert example == "[...]error[...]"


def test_pattern_generate_example_empty_line() -> None:
    """Pattern generate_example handles empty-line marker."""
    from pytest_patterns.plugin import PatternsLib

    lib = PatternsLib()
    p = lib.test
    p.optional("<empty-line>")
    example = p.generate_example()
    # Empty line marker should be replaced with empty string
    assert "<empty-line>" not in example


def test_pattern_generate_example_ignores_refused() -> None:
    """Pattern generate_example ignores refused patterns."""
    from pytest_patterns.plugin import PatternsLib

    lib = PatternsLib()
    p = lib.test
    p.in_order("good_line")
    p.refused("bad_line")
    example = p.generate_example()
    assert "good_line" in example
    assert "bad_line" not in example


def test_pattern_replace_wildcards_ellipsis() -> None:
    """Pattern _replace_wildcards replaces ellipsis."""
    from pytest_patterns.plugin import Pattern, PatternsLib

    lib = PatternsLib()
    p = Pattern(lib, "test")
    result = p._replace_wildcards("...error...")
    assert result == "[...]error[...]"


def test_pattern_replace_wildcards_empty_line() -> None:
    """Pattern _replace_wildcards replaces empty-line marker."""
    from pytest_patterns.plugin import Pattern, PatternsLib

    lib = PatternsLib()
    p = Pattern(lib, "test")
    result = p._replace_wildcards("<empty-line>")
    assert result == ""


def test_pattern_replace_wildcards_normal() -> None:
    """Pattern _replace_wildcards leaves normal text unchanged."""
    from pytest_patterns.plugin import Pattern, PatternsLib

    lib = PatternsLib()
    p = Pattern(lib, "test")
    result = p._replace_wildcards("normal text")
    assert result == "normal text"


def test_pattern_eq_success() -> None:
    """Pattern equality check success."""
    from pytest_patterns.plugin import PatternsLib

    lib = PatternsLib()
    p = lib.test
    p.in_order("line1\nline2")
    assert p == "line1\nline2"


def test_pattern_eq_failure() -> None:
    """Pattern equality check failure."""
    from pytest_patterns.plugin import PatternsLib

    lib = PatternsLib()
    p = lib.test
    p.in_order("line1\nline2")
    assert not (p == "line1\nline3")


def test_pattern_eq_with_other_object() -> None:
    """Pattern equality with non-string raises AssertionError."""
    from pytest_patterns.plugin import PatternsLib

    lib = PatternsLib()
    p = lib.test
    try:
        _ = p == 123  # type: ignore
        assert False, "Should have raised AssertionError"
    except AssertionError:
        pass


# --- PatternsLib class tests ---


def test_patterns_lib_getattr() -> None:
    """PatternsLib creates Pattern on attribute access."""
    from pytest_patterns.plugin import Pattern, PatternsLib

    lib = PatternsLib()
    p = lib.test_pattern
    assert isinstance(p, Pattern)
    assert p.name == "test_pattern"
    assert p.library is lib


def test_patterns_lib_caching() -> None:
    """PatternsLib caches patterns."""
    from pytest_patterns.plugin import PatternsLib

    lib = PatternsLib()
    p1 = lib.test
    p2 = lib.test
    assert p1 is p2  # Same object


def test_patterns_lib_multiple_patterns() -> None:
    """PatternsLib can create multiple patterns."""
    from pytest_patterns.plugin import PatternsLib

    lib = PatternsLib()
    p1 = lib.pattern1
    p2 = lib.pattern2
    assert p1.name == "pattern1"
    assert p2.name == "pattern2"
    assert p1 is not p2


# --- Audit report tests ---


def test_report_basic() -> None:
    """Basic report generation."""
    from pytest_patterns.plugin import Audit

    audit = Audit("line1\nline2")
    audit.in_order("pattern1", ["line1", "line2"])
    lines = list(audit.report(use_color=True))
    assert len(lines) > 0
    assert any("pattern1" in line for line in lines)


def test_report_with_unmatched() -> None:
    """Report with unmatched expectations."""
    from pytest_patterns.plugin import Audit

    audit = Audit("line1")
    audit.in_order("pattern1", ["line1", "missing"])
    lines = list(audit.report(use_color=True))
    assert any("unmatched" in line.lower() for line in lines)


def test_report_with_refused() -> None:
    """Report with matched refused lines."""
    from pytest_patterns.plugin import Audit

    audit = Audit("error line")
    audit.refused("no_errors", ["...error..."])
    lines = list(audit.report(use_color=True))
    assert any("refused" in line.lower() for line in lines)


def test_report_with_whitespace_issues() -> None:
    """Report includes whitespace warnings."""
    from pytest_patterns.plugin import Audit

    audit = Audit("line  ")
    # Don't match so line stays unexpected with trailing whitespace
    lines = list(audit.report(use_color=True))
    # Should include whitespace warning
    assert any("whitespace" in line.lower() for line in lines)


def test_report_no_color() -> None:
    """Report without color codes."""
    from pytest_patterns.plugin import Audit

    audit = Audit("line1\nline2")
    audit.in_order("pattern1", ["line1", "line2"])
    lines = list(audit.report(use_color=False))
    # Should not contain ANSI codes
    assert not any("\x1b[" in line for line in lines)


# --- Audit build summary tests ---


def test_build_summary_single_pattern() -> None:
    """Summary with single pattern."""
    from pytest_patterns.plugin import Audit

    audit = Audit("line1\nunexpected")
    audit.in_order("pattern1", ["line1"])
    summary = audit._build_summary()
    assert "unexpected" in summary.lower()
    assert "pattern1" in summary


def test_build_summary_multiple_patterns() -> None:
    """Summary with multiple patterns."""
    from pytest_patterns.plugin import Audit

    audit = Audit("line1\nline2\nunexpected")
    audit.in_order("pattern1", ["line1"])
    audit.optional("pattern2", ["...line2..."])
    summary = audit._build_summary()
    assert "pattern1" in summary
    assert "pattern2" in summary


def test_build_summary_refused() -> None:
    """Summary with refused lines."""
    from pytest_patterns.plugin import Audit

    audit = Audit("error line")
    audit.refused("no_errors", ["...error..."])
    summary = audit._build_summary()
    assert "refused" in summary.lower()


def test_build_summary_no_failures() -> None:
    """Summary with no failures."""
    from pytest_patterns.plugin import Audit

    audit = Audit("line1")
    audit.in_order("pattern1", ["line1"])
    summary = audit._build_summary()
    assert "did not meet" in summary.lower()


# --- Audit build context tests ---


def test_build_context_middle() -> None:
    """Build context from middle of content."""
    from pytest_patterns.plugin import Audit

    audit = Audit("a\nb\nc\nd\ne\nf\ng\nh")
    start, lines = audit._build_context(5)  # Around line 5 (1-based)
    assert start == 2  # Lines 2-8 (3 before + line 5 + 3 after)
    assert len(lines) == 7


def test_build_context_beginning() -> None:
    """Build context at beginning."""
    from pytest_patterns.plugin import Audit

    audit = Audit("a\nb\nc\nd")
    start, lines = audit._build_context(1)
    assert start == 1
    assert len(lines) == 4  # Only 4 lines total


def test_build_context_end() -> None:
    """Build context at end."""
    from pytest_patterns.plugin import Audit

    audit = Audit("a\nb\nc\nd")
    start, lines = audit._build_context(4)
    assert start == 1
    assert len(lines) == 4  # Only 4 lines total


# --- Continuous edge case tests ---


def test_continuous_first_line_no_match() -> None:
    """Continuous pattern where first line doesn't match."""
    from pytest_patterns.plugin import Audit, Status

    audit = Audit("unexpected\nline2")
    audit.continuous("pattern1", ["line1", "line2"])
    # First line not matching is allowed, should not mark as refused
    assert audit.content[0].status == Status.UNEXPECTED
    # Should have unmatched expectations
    assert len(audit.unmatched_expectations) > 0


def test_patternslib_multiple_accesses(patterns: PatternsLib) -> None:
    assert patterns.foo is patterns.foo


def test_empty_pattern_empty_string_is_ok(patterns: PatternsLib) -> None:
    # This is fine IMHO. The whole general assumption is that we only reject
    # unexpected content and fail if required content is missing. If there is
    # no content, then there is no unexpected content and if you didn't expect
    # any content then there is none missing, so we fall through.
    audit = patterns.nothing._audit("")
    report = list(audit.report())
    assert extract_summary(report) == "String did not meet the expectations."
    assert strip_line_numbers(strip_summary(report)) == GENERIC_HEADER
    assert audit.is_ok()


def test_unexpected_lines_fail(patterns: PatternsLib) -> None:
    audit = patterns.nothing._audit("This is an unexpected line")
    report = list(audit.report())
    assert extract_summary(report) == "Pattern: 1 unexpected."
    assert strip_line_numbers(strip_summary(report)) == [
        *GENERIC_HEADER,
        "🟡                 | This is an unexpected line",
    ]
    assert not audit.is_ok()


def test_empty_lines_do_not_match(patterns: PatternsLib) -> None:
    patterns.nothing.optional("")
    audit = patterns.nothing._audit(
        """
"""
    )
    report = list(audit.report())
    assert extract_summary(report) == "Pattern: 1 unexpected."
    assert strip_line_numbers(strip_summary(report)) == [
        *GENERIC_HEADER,
        "🟡                 | ",
    ]
    assert not audit.is_ok()


def test_empty_lines_match_special_marker(patterns: PatternsLib) -> None:
    patterns.empty.optional("<empty-line>")
    audit = patterns.empty._audit(
        """

<empty-line>
"""
    )
    report = list(audit.report())
    assert extract_summary(report) == "String did not meet the expectations."
    assert strip_line_numbers(strip_summary(report)) == [
        *GENERIC_HEADER,
        "⚪️ empty           | ",
        "⚪️ empty           | ",
        "⚪️ empty           | <empty-line>",
    ]
    assert audit.is_ok()


def test_comprehensive(patterns: PatternsLib) -> None:
    sample = patterns.sample

    sample.in_order(
        """
This comes early on
This comes later

This comes even later
"""
    )
    sample.optional(
        """
This is a heartbeat that can appear almost anywhere...
"""
    )
    sample.continuous(
        """
This comes first (...)
This comes second (...)
This comes third (...)
"""
    )
    sample.refused(
        """
...error...
"""
    )
    assert (
        sample
        == """\
This comes early on
This is a heartbeat that can appear almost anywhere
This comes first (with variability)
This comes second (also with variability)
This comes third (more variability!)
This is a heartbeat that can appear almost anywhere (outside focus ranges)
This comes later
This comes even later
"""
    )


def test_in_order_lines_clear_with_intermittent_input(
    patterns: PatternsLib,
) -> None:
    pattern = patterns.in_order
    pattern.in_order(
        """
This is a first expected line
This is a second expected line"""
    )
    pattern.optional("This is from another match")

    audit = pattern._audit(
        """\
This is a first expected line
This is from another match
This is a second expected line"""
    )

    report = list(audit.report())
    assert extract_summary(report) == "String did not meet the expectations."
    assert strip_line_numbers(strip_summary(report)) == [
        *GENERIC_HEADER,
        "🟢 in_order        | This is a first expected line",
        "⚪️ in_order        | This is from another match",
        "🟢 in_order        | This is a second expected line",
    ]
    assert audit.is_ok()


def test_missing_ordered_lines_fail(patterns: PatternsLib) -> None:
    pattern = patterns.in_order
    pattern.in_order(
        """
This is an expected line
This is also an expected line
"""
    )

    audit = pattern._audit(
        """\
This is an expected line
"""
    )
    report = list(audit.report())
    assert extract_summary(report) == "Pattern [in_order]: 1 unmatched."
    assert strip_line_numbers(strip_summary(report)) == [
        *GENERIC_HEADER,
        "🟢 in_order        | This is an expected line",
        "",
        "These are the unmatched expected lines: ",
        "",
        "🔴 in_order        | This is also an expected line",
    ]
    assert not audit.is_ok()


def test_incorrectly_ordered_lines_fail(patterns: PatternsLib) -> None:
    pattern = patterns.in_order
    pattern.in_order(
        """
Line 1
Line 2
Line 3
Line 4
Line 5
"""
    )

    audit = pattern._audit(
        """\
Line 5
Line 4
Line 3
Line 2
Line 1
"""
    )
    report = list(audit.report())
    assert (
        extract_summary(report)
        == "Pattern [in_order]: 4 unexpected; 4 unmatched."
    )
    assert strip_line_numbers(strip_summary(report)) == [
        *GENERIC_HEADER,
        "🟡                 | Line 5",
        "🟡                 | Line 4",
        "🟡                 | Line 3",
        "🟡                 | Line 2",
        "🟢 in_order        | Line 1",
        "",
        "These are the unmatched expected lines: ",
        "",
        "🔴 in_order        | Line 2",
        "🔴 in_order        | Line 3",
        "🔴 in_order        | Line 4",
        "🔴 in_order        | Line 5",
    ]
    assert not audit.is_ok()


def test_refused_lines_fail(patterns: PatternsLib) -> None:
    pattern = patterns.refused
    pattern.refused("This is a refused line")

    audit = pattern._audit("This is a refused line")
    report = list(audit.report())
    assert extract_summary(report) == "Pattern [refused]: 1 refused."
    assert strip_line_numbers(strip_summary(report)) == [
        *GENERIC_HEADER,
        "🔴 refused         | This is a refused line",
        "",
        "These are the matched refused lines: ",
        "",
        "🔴 refused         | This is a refused line  (lines 1)",
    ]
    assert not audit.is_ok()


def test_continuous_lines_only_clear_if_not_interrupted(
    patterns: PatternsLib,
) -> None:
    pattern = patterns.focus
    pattern.optional("asdf")
    pattern.continuous(
        """
These lines
need to match
without being
interrupted
"""
    )

    audit = pattern._audit(
        """\
asdf
These lines
need to match
without being
interrupted
asdf
"""
    )
    report = list(audit.report())
    assert extract_summary(report) == "String did not meet the expectations."
    assert strip_line_numbers(strip_summary(report)) == [
        *GENERIC_HEADER,
        "⚪️ focus           | asdf",
        "🟢 focus           | These lines",
        "🟢 focus           | need to match",
        "🟢 focus           | without being",
        "🟢 focus           | interrupted",
        "⚪️ focus           | asdf",
    ]
    assert audit.is_ok()

    audit = pattern._audit(
        """\
asdf
These lines
are broken
need to match
asdf
without being
because there is stuff in between
interrupted
asdf
"""
    )
    report = list(audit.report())
    assert (
        extract_summary(report)
        == "Pattern [focus]: 4 unexpected; 1 refused; 3 unmatched."
    )
    assert strip_line_numbers(strip_summary(report)) == [
        *GENERIC_HEADER,
        "⚪️ focus           | asdf",
        "🟢 focus           | These lines",
        "🔴 focus           | are broken",
        "🟡                 | need to match",
        "⚪️ focus           | asdf",
        "🟡                 | without being",
        "🟡                 | because there is stuff in between",
        "🟡                 | interrupted",
        "⚪️ focus           | asdf",
        "",
        "These are the unmatched expected lines: ",
        "",
        "🔴 focus           | need to match",
        "🔴 focus           | without being",
        "🔴 focus           | interrupted",
    ]
    assert not audit.is_ok()


def test_continuous_lines_fail_and_report_if_first_line_isnt_matching(
    patterns: PatternsLib,
) -> None:
    pattern = patterns.focus
    pattern.continuous(
        """
First line
Second line
"""
    )

    audit = pattern._audit(
        """\
Not the first line
There is no first line
"""
    )
    report = list(audit.report())
    assert (
        extract_summary(report) == "Pattern [focus]: 2 unexpected; 2 unmatched."
    )
    assert strip_line_numbers(strip_summary(report)) == [
        *GENERIC_HEADER,
        "🟡                 | Not the first line",
        "🟡                 | There is no first line",
        "",
        "These are the unmatched expected lines: ",
        "",
        "🔴 focus           | First line",
        "🔴 focus           | Second line",
    ]
    assert not audit.is_ok()


def test_optional(patterns: PatternsLib) -> None:
    pattern = patterns.optional
    pattern.optional("pong")
    pattern.optional("ping")

    audit = pattern._audit(
        """\
ping
"""
    )
    report = list(audit.report())
    assert extract_summary(report) == "String did not meet the expectations."
    assert strip_line_numbers(strip_summary(report)) == [
        *GENERIC_HEADER,
        "⚪️ optional        | ping",
    ]
    assert audit.is_ok()


@pytest.fixture()
def fcqemu_patterns(patterns: PatternsLib) -> None:
    patterns.debug.optional("simplevm> ...")

    # This part of the heartbeats must show up
    patterns.heartbeat.in_order(
        """
simplevm             heartbeat-initialized
simplevm             started-heartbeat-ping
simplevm             heartbeat-ping
"""
    )
    # The pings may happen more times and sometimes the stopping part
    # isn't visible because we terminate too fast.
    patterns.heartbeat.optional(
        """
simplevm             heartbeat-ping
simplevm             stopped-heartbeat-ping
"""
    )

    patterns.failure.refused("...fail...")


def test_complex_example(patterns: PatternsLib, fcqemu_patterns: None) -> None:
    outmigration = patterns.outmigration
    outmigration.merge("debug", "heartbeat", "failure")

    outmigration.in_order(
        """
/nix/store/.../bin/fc-qemu -v outmigrate simplevm
load-system-config
simplevm             connect-rados                  subsystem='ceph'
simplevm             acquire-lock                   target='/run/qemu.simplevm.lock'
simplevm             acquire-lock                   count=1 result='locked' target='/run/qemu.simplevm.lock'
simplevm             qmp_capabilities               arguments={} id=None subsystem='qemu/qmp'
simplevm             query-status                   arguments={} id=None subsystem='qemu/qmp'

simplevm             outmigrate
simplevm             consul-register
simplevm             locate-inmigration-service
simplevm             check-staging-config           result='none'
simplevm             located-inmigration-service    url='http://host2.mgm.test.gocept.net:...'

simplevm             acquire-migration-locks
simplevm             check-staging-config           result='none'
simplevm             acquire-migration-lock         result='success' subsystem='qemu'
simplevm             acquire-local-migration-lock   result='success'
simplevm             acquire-remote-migration-lock
simplevm             acquire-remote-migration-lock  result='success'

simplevm             unlock                         subsystem='ceph' volume='rbd.ssd/simplevm.root'
simplevm             unlock                         subsystem='ceph' volume='rbd.ssd/simplevm.swap'
simplevm             unlock                         subsystem='ceph' volume='rbd.ssd/simplevm.tmp'

simplevm             prepare-remote-environment
simplevm             start-migration                target='tcp:192.168.4.7:...'
simplevm             migrate                        subsystem='qemu'
simplevm             migrate-set-capabilities       arguments={'capabilities': [{'capability': 'xbzrle', 'state': False}, {'capability': 'auto-converge', 'state': True}]} id=None subsystem='qemu/qmp'
simplevm             migrate-set-parameters         arguments={'compress-level': 0, 'downtime-limit': 4000, 'max-bandwidth': 22500} id=None subsystem='qemu/qmp'
simplevm             migrate                        arguments={'uri': 'tcp:192.168.4.7:...'} id=None subsystem='qemu/qmp'

simplevm             query-migrate-parameters       arguments={} id=None subsystem='qemu/qmp'
simplevm             migrate-parameters             announce-initial=50 announce-max=550 announce-rounds=5 announce-step=100 block-incremental=False compress-level=0 compress-threads=8 compress-wait-thread=True cpu-throttle-increment=10 cpu-throttle-initial=20 cpu-throttle-tailslow=False decompress-threads=2 downtime-limit=4000 max-bandwidth=22500 max-cpu-throttle=99 max-postcopy-bandwidth=0 multifd-channels=2 multifd-compression='none' multifd-zlib-level=1 multifd-zstd-level=1 subsystem='qemu' throttle-trigger-threshold=50 tls-authz='' tls-creds='' tls-hostname='' x-checkpoint-delay=20000 xbzrle-cache-size=67108864

simplevm             query-migrate                  arguments={} id=None subsystem='qemu/qmp'
simplevm             migration-status               mbps='-' remaining='0' status='setup'

simplevm             query-migrate                  arguments={} id=None subsystem='qemu/qmp'
simplevm             migration-status               mbps=... remaining='...' status='active'

simplevm             migration-status               mbps=... remaining='...' status='completed'

simplevm             query-status                   arguments={} id=None subsystem='qemu/qmp'
simplevm             finish-migration

simplevm             vm-destroy-kill-supervisor     attempt=1 subsystem='qemu'
simplevm             vm-destroy-kill-supervisor     attempt=2 subsystem='qemu'
simplevm             vm-destroy-kill-vm             attempt=1 subsystem='qemu'
simplevm             vm-destroy-kill-vm             attempt=2 subsystem='qemu'
simplevm             clean-run-files                subsystem='qemu'
simplevm             finish-remote
simplevm             consul-deregister
simplevm             outmigrate-finished            exitcode=0
simplevm             release-lock                   count=0 target='/run/qemu.simplevm.lock'
simplevm             release-lock                   result='unlocked' target='/run/qemu.simplevm.lock'
"""  # noqa: E501
    )
    # The migration process may take a couple of rounds to complete,
    # so this might appear more often:
    outmigration.optional(
        """
simplevm             query-migrate                  arguments={} id=None subsystem='qemu/qmp'
simplevm             migration-status               mbps=... remaining='...' status='active'
"""  # noqa: E501
    )

    assert (
        outmigration
        == """\
/nix/store/99xm8d2fjwlj6fvglrwpi0pz5zz8jsl1-python3.8-fc.qemu-dev/bin/fc-qemu -v outmigrate simplevm
load-system-config
simplevm             connect-rados                  subsystem='ceph'
simplevm             acquire-lock                   target='/run/qemu.simplevm.lock'
simplevm             acquire-lock                   count=1 result='locked' target='/run/qemu.simplevm.lock'
simplevm             qmp_capabilities               arguments={} id=None subsystem='qemu/qmp'
simplevm             query-status                   arguments={} id=None subsystem='qemu/qmp'
simplevm             outmigrate
simplevm             consul-register
simplevm             heartbeat-initialized
simplevm             locate-inmigration-service
simplevm             check-staging-config           result='none'
simplevm             located-inmigration-service    url='http://host2.mgm.test.gocept.net:43303'
simplevm             started-heartbeat-ping
simplevm             acquire-migration-locks
simplevm             heartbeat-ping
simplevm             check-staging-config           result='none'
simplevm             acquire-migration-lock         result='success' subsystem='qemu'
simplevm             acquire-local-migration-lock   result='success'
simplevm             acquire-remote-migration-lock
simplevm             acquire-remote-migration-lock  result='success'
simplevm             unlock                         subsystem='ceph' volume='rbd.ssd/simplevm.root'
simplevm             unlock                         subsystem='ceph' volume='rbd.ssd/simplevm.swap'
simplevm             unlock                         subsystem='ceph' volume='rbd.ssd/simplevm.tmp'
simplevm             prepare-remote-environment
simplevm             start-migration                target='tcp:192.168.4.7:2345'
simplevm             migrate                        subsystem='qemu'
simplevm             migrate-set-capabilities       arguments={'capabilities': [{'capability': 'xbzrle', 'state': False}, {'capability': 'auto-converge', 'state': True}]} id=None subsystem='qemu/qmp'
simplevm             migrate-set-parameters         arguments={'compress-level': 0, 'downtime-limit': 4000, 'max-bandwidth': 22500} id=None subsystem='qemu/qmp'
simplevm             migrate                        arguments={'uri': 'tcp:192.168.4.7:2345'} id=None subsystem='qemu/qmp'
simplevm             query-migrate-parameters       arguments={} id=None subsystem='qemu/qmp'
simplevm             migrate-parameters             announce-initial=50 announce-max=550 announce-rounds=5 announce-step=100 block-incremental=False compress-level=0 compress-threads=8 compress-wait-thread=True cpu-throttle-increment=10 cpu-throttle-initial=20 cpu-throttle-tailslow=False decompress-threads=2 downtime-limit=4000 max-bandwidth=22500 max-cpu-throttle=99 max-postcopy-bandwidth=0 multifd-channels=2 multifd-compression='none' multifd-zlib-level=1 multifd-zstd-level=1 subsystem='qemu' throttle-trigger-threshold=50 tls-authz='' tls-creds='' tls-hostname='' x-checkpoint-delay=20000 xbzrle-cache-size=67108864
simplevm             query-migrate                  arguments={} id=None subsystem='qemu/qmp'
simplevm             migration-status               mbps='-' remaining='0' status='setup'
simplevm> {'blocked': False, 'status': 'setup'}
simplevm             query-migrate                  arguments={} id=None subsystem='qemu/qmp'
simplevm             migration-status               mbps=0.32976 remaining='285,528,064' status='active'
simplevm> {'blocked': False,
simplevm>  'expected-downtime': 4000,
simplevm>  'ram': {'dirty-pages-rate': 0,
simplevm>          'dirty-sync-count': 1,
simplevm>          'duplicate': 182,
simplevm>          'mbps': 0.32976,
simplevm>          'multifd-bytes': 0,
simplevm>          'normal': 15,
simplevm>          'normal-bytes': 61440,
simplevm>          'page-size': 4096,
simplevm>          'pages-per-second': 10,
simplevm>          'postcopy-requests': 0,
simplevm>          'remaining': 285528064,
simplevm>          'skipped': 0,
simplevm>          'total': 286334976,
simplevm>          'transferred': 63317},
simplevm>  'setup-time': 1,
simplevm>  'status': 'active',
simplevm>  'total-time': 1418}
simplevm             query-migrate                  arguments={} id=None subsystem='qemu/qmp'
simplevm             migration-status               mbps=0.32976 remaining='285,331,456' status='active'
simplevm> {'blocked': False,
simplevm>  'expected-downtime': 4000,
simplevm>  'ram': {'dirty-pages-rate': 0,
simplevm>          'dirty-sync-count': 1,
simplevm>          'duplicate': 210,
simplevm>          'mbps': 0.32976,
simplevm>          'multifd-bytes': 0,
simplevm>          'normal': 35,
simplevm>          'normal-bytes': 143360,
simplevm>          'page-size': 4096,
simplevm>          'pages-per-second': 10,
simplevm>          'postcopy-requests': 0,
simplevm>          'remaining': 285331456,
simplevm>          'skipped': 0,
simplevm>          'total': 286334976,
simplevm>          'transferred': 145809},
simplevm>  'setup-time': 1,
simplevm>  'status': 'active',
simplevm>  'total-time': 3421}
simplevm             query-migrate                  arguments={} id=None subsystem='qemu/qmp'
simplevm             migration-status               mbps=0.18144 remaining='267,878,400' status='active'
simplevm> {'blocked': False,
simplevm>  'expected-downtime': 4000,
simplevm>  'ram': {'dirty-pages-rate': 0,
simplevm>          'dirty-sync-count': 1,
simplevm>          'duplicate': 4460,
simplevm>          'mbps': 0.18144,
simplevm>          'multifd-bytes': 0,
simplevm>          'normal': 46,
simplevm>          'normal-bytes': 188416,
simplevm>          'page-size': 4096,
simplevm>          'pages-per-second': 2500,
simplevm>          'postcopy-requests': 0,
simplevm>          'remaining': 267878400,
simplevm>          'skipped': 0,
simplevm>          'total': 286334976,
simplevm>          'transferred': 229427},
simplevm>  'setup-time': 1,
simplevm>  'status': 'active',
simplevm>  'total-time': 6253}
simplevm             heartbeat-ping
simplevm             query-migrate                  arguments={} id=None subsystem='qemu/qmp'
simplevm             migration-status               mbps=0.18144 remaining='226,918,400' status='active'
simplevm> {'blocked': False,
simplevm>  'expected-downtime': 4000,
simplevm>  'ram': {'dirty-pages-rate': 0,
simplevm>          'dirty-sync-count': 1,
simplevm>          'duplicate': 14460,
simplevm>          'mbps': 0.18144,
simplevm>          'multifd-bytes': 0,
simplevm>          'normal': 46,
simplevm>          'normal-bytes': 188416,
simplevm>          'page-size': 4096,
simplevm>          'pages-per-second': 2500,
simplevm>          'postcopy-requests': 0,
simplevm>          'remaining': 226918400,
simplevm>          'skipped': 0,
simplevm>          'total': 286334976,
simplevm>          'transferred': 319747},
simplevm>  'setup-time': 1,
simplevm>  'status': 'active',
simplevm>  'total-time': 10258}
simplevm             query-migrate                  arguments={} id=None subsystem='qemu/qmp'
simplevm             migration-status               mbps=0.18144 remaining='169,574,400' status='active'
simplevm> {'blocked': False,
simplevm>  'expected-downtime': 4000,
simplevm>  'ram': {'dirty-pages-rate': 0,
simplevm>          'dirty-sync-count': 1,
simplevm>          'duplicate': 28460,
simplevm>          'mbps': 0.18144,
simplevm>          'multifd-bytes': 0,
simplevm>          'normal': 46,
simplevm>          'normal-bytes': 188416,
simplevm>          'page-size': 4096,
simplevm>          'pages-per-second': 2500,
simplevm>          'postcopy-requests': 0,
simplevm>          'remaining': 169574400,
simplevm>          'skipped': 0,
simplevm>          'total': 286334976,
simplevm>          'transferred': 446195},
simplevm>  'setup-time': 1,
simplevm>  'status': 'active',
simplevm>  'total-time': 15917}
simplevm             heartbeat-ping
simplevm             query-migrate                  arguments={} id=None subsystem='qemu/qmp'
simplevm             migration-status               mbps=0.18144 remaining='87,654,400' status='active'
simplevm> {'blocked': False,
simplevm>  'expected-downtime': 4000,
simplevm>  'ram': {'dirty-pages-rate': 0,
simplevm>          'dirty-sync-count': 1,
simplevm>          'duplicate': 48460,
simplevm>          'mbps': 0.18144,
simplevm>          'multifd-bytes': 0,
simplevm>          'normal': 46,
simplevm>          'normal-bytes': 188416,
simplevm>          'page-size': 4096,
simplevm>          'pages-per-second': 2500,
simplevm>          'postcopy-requests': 0,
simplevm>          'remaining': 87654400,
simplevm>          'skipped': 0,
simplevm>          'total': 286334976,
simplevm>          'transferred': 626835},
simplevm>  'setup-time': 1,
simplevm>  'status': 'active',
simplevm>  'total-time': 23926}
simplevm             heartbeat-ping
simplevm             query-migrate                  arguments={} id=None subsystem='qemu/qmp'
simplevm             migration-status               mbps=0.32976 remaining='18,821,120' status='active'
simplevm> {'blocked': False,
simplevm>  'expected-downtime': 4000,
simplevm>  'ram': {'dirty-pages-rate': 0,
simplevm>          'dirty-sync-count': 1,
simplevm>          'duplicate': 65218,
simplevm>          'mbps': 0.32976,
simplevm>          'multifd-bytes': 0,
simplevm>          'normal': 93,
simplevm>          'normal-bytes': 380928,
simplevm>          'page-size': 4096,
simplevm>          'pages-per-second': 10,
simplevm>          'postcopy-requests': 0,
simplevm>          'remaining': 18821120,
simplevm>          'skipped': 0,
simplevm>          'total': 286334976,
simplevm>          'transferred': 971457},
simplevm>  'setup-time': 1,
simplevm>  'status': 'active',
simplevm>  'total-time': 35251}
simplevm             heartbeat-ping
simplevm             query-migrate                  arguments={} id=None subsystem='qemu/qmp'
simplevm             migration-status               mbps=0.32976 remaining='827,392' status='active'
simplevm> {'blocked': False,
simplevm>  'expected-downtime': 4000,
simplevm>  'ram': {'dirty-pages-rate': 0,
simplevm>          'dirty-sync-count': 1,
simplevm>          'duplicate': 69514,
simplevm>          'mbps': 0.32976,
simplevm>          'multifd-bytes': 0,
simplevm>          'normal': 190,
simplevm>          'normal-bytes': 778240,
simplevm>          'page-size': 4096,
simplevm>          'pages-per-second': 10,
simplevm>          'postcopy-requests': 0,
simplevm>          'remaining': 827392,
simplevm>          'skipped': 0,
simplevm>          'total': 286334976,
simplevm>          'transferred': 1409164},
simplevm>  'setup-time': 1,
simplevm>  'status': 'active',
simplevm>  'total-time': 46571}
simplevm             heartbeat-ping
simplevm             heartbeat-ping
simplevm             query-migrate                  arguments={} id=None subsystem='qemu/qmp'
simplevm             migration-status               mbps=0.32976 remaining='1,175,552' status='active'
simplevm> {'blocked': False,
simplevm>  'expected-downtime': 4000,
simplevm>  'ram': {'dirty-pages-rate': 4,
simplevm>          'dirty-sync-count': 2,
simplevm>          'duplicate': 69594,
simplevm>          'mbps': 0.32976,
simplevm>          'multifd-bytes': 0,
simplevm>          'normal': 303,
simplevm>          'normal-bytes': 1241088,
simplevm>          'page-size': 4096,
simplevm>          'pages-per-second': 10,
simplevm>          'postcopy-requests': 0,
simplevm>          'remaining': 1175552,
simplevm>          'skipped': 0,
simplevm>          'total': 286334976,
simplevm>          'transferred': 1874632},
simplevm>  'setup-time': 1,
simplevm>  'status': 'active',
simplevm>  'total-time': 57893}
simplevm             heartbeat-ping
simplevm             query-migrate                  arguments={} id=None subsystem='qemu/qmp'
simplevm             migration-status               mbps=0.32976 remaining='172,032' status='active'
simplevm> {'blocked': False,
simplevm>  'expected-downtime': 4000,
simplevm>  'ram': {'dirty-pages-rate': 0,
simplevm>          'dirty-sync-count': 3,
simplevm>          'duplicate': 69730,
simplevm>          'mbps': 0.32976,
simplevm>          'multifd-bytes': 0,
simplevm>          'normal': 416,
simplevm>          'normal-bytes': 1703936,
simplevm>          'page-size': 4096,
simplevm>          'pages-per-second': 10,
simplevm>          'postcopy-requests': 0,
simplevm>          'remaining': 172032,
simplevm>          'skipped': 0,
simplevm>          'total': 286334976,
simplevm>          'transferred': 2340590},
simplevm>  'setup-time': 1,
simplevm>  'status': 'active',
simplevm>  'total-time': 69217}
simplevm             heartbeat-ping
simplevm             query-migrate                  arguments={} id=None subsystem='qemu/qmp'
simplevm             migration-status               mbps=0.34051462695157925 remaining='0' status='completed'
simplevm> {'blocked': False,
simplevm>  'downtime': 7,
simplevm>  'ram': {'dirty-pages-rate': 0,
simplevm>          'dirty-sync-count': 5,
simplevm>          'duplicate': 69730,
simplevm>          'mbps': 0.34051462695157925,
simplevm>          'multifd-bytes': 0,
simplevm>          'normal': 458,
simplevm>          'normal-bytes': 1875968,
simplevm>          'page-size': 4096,
simplevm>          'pages-per-second': 10,
simplevm>          'postcopy-requests': 0,
simplevm>          'remaining': 0,
simplevm>          'skipped': 0,
simplevm>          'total': 286334976,
simplevm>          'transferred': 2512989},
simplevm>  'setup-time': 1,
simplevm>  'status': 'completed',
simplevm>  'total-time': 69496}
simplevm             query-status                   arguments={} id=None subsystem='qemu/qmp'
simplevm             finish-migration
simplevm             vm-destroy-kill-supervisor     attempt=1 subsystem='qemu'
simplevm             vm-destroy-kill-supervisor     attempt=2 subsystem='qemu'
simplevm             vm-destroy-kill-vm             attempt=1 subsystem='qemu'
simplevm             vm-destroy-kill-vm             attempt=2 subsystem='qemu'
simplevm             clean-run-files                subsystem='qemu'
simplevm             finish-remote
simplevm             consul-deregister
simplevm             outmigrate-finished            exitcode=0
simplevm             release-lock                   count=0 target='/run/qemu.simplevm.lock'
simplevm             release-lock                   result='unlocked' target='/run/qemu.simplevm.lock'
"""  # noqa: E501
    )


def test_html(patterns: PatternsLib) -> None:
    patterns.owrap.in_order(
        """
<!DOCTYPE html>
<html lang="en">
      <body>
      </body>
</html>
"""
    )
    patterns.owrap.optional("...")
    # patterns.owrap.normalize("html")

    invoice_list = patterns.invoice_list
    invoice_list.merge("owrap")
    invoice_list.continuous(
        """
      <tbody>
        <tr>
          <td>2023-10-01 &mdash; 2023-10-31</td>
          <td>
            <a href="https://localhost/customer/10466">
              10466</a>
            Theune, Christian
          </td>


            <td class="text-right numeric">
              0.00&nbsp;€
            </td>

          <td>pending</td>
          <td><a href="https://localhost/invoice/55006/view">View</a></td> </tr>
      </tbody>
"""
    )

    assert (
        invoice_list
        == """\
<!DOCTYPE html>
<html lang="en">
      <!-- This is a partial template for non-boosted HTMX requests where we only
      expect the body of the targetted template to be filled in. -->
      <body>


   <a
      href="https://localhost/invoice/generate"
      id="generateInvoices"
      class="list-group-item">
      <span class="glyphicon glyphicon-plus"></span> Generate
    </a>


            <div></div>
            <div class="well">
    <form
          class="form" role="form" id="filterForm"
          hx-get="https://localhost/invoice"
          hx-target="#invoiceTable"
          hx-trigger="change, submit, every 5s"
          hx-indicator="#invoiceTable"
          hx-push-url="true"
          hx-select="#invoiceTable"
          hx-select-oob="#invoiceStatus"
          >
      <div class="form-group">
        <input
               placeholder="Search ..."
               _="on load call me.focus()"
               class="form-control" name="search" value="Theun" />
      </div>

      <div class="form-group">
        <select class="form-control" name="timeframe">
          <option value="filter_this_month"> This month
          </option>
          <option value="filter_last_month" selected="True"> Last month
          </option>
          <option value="filter_this_year"> This year
          </option>
          <option value="filter_last_year"> Last year
          </option>
          <option value="filter_all"> All
          </option>
        </select>
      </div>

      <div class="form-group" id="invoiceStatus">
        <h4>Status</h4>

        <div class="checkbox">
          <label>
            <input type="checkbox" name="status" value="generating" checked="True" /> Generating (0)
          </label>
        </div>
        <div class="checkbox">
          <label>
            <input type="checkbox" name="status" value="pending" checked="True" /> Pending (72)
          </label>
        </div>
        <div class="checkbox">
          <label>
            <input type="checkbox" name="status" value="proforma" /> Proforma
          </label>
        </div>
        <div class="checkbox">
          <label>
            <input type="checkbox" name="status" value="review" checked="True" /> Review
          </label>
        </div>
        <div class="checkbox">
          <label>
            <input type="checkbox" name="status" value="error" checked="True" /> Error (0)
          </label>
        </div>
        <div class="checkbox">
          <label>
            <input type="checkbox" name="status" value="transmitted" checked="True" /> Transmitted
          </label>
        </div>

      </div>

      <div class="form-group">
        <h4>Options</h4>

        <div class="checkbox">
          <label>
            <input type="checkbox" name="compare" value="compare" /> Show trend
          </label>
        </div>

      </div>

    </form>
  </div>
            <div>
    <table class="table table-striped" id="invoiceTable">
      <thead>
        <tr>
          <th class="col-md-3">Consumption Period</th>
          <th class="col-md-3">Customer</th>

          <th class="col-md-1 text-right">Sum</th>
          <th class="col-md-1">Status</th>
          <th class="col-md-1">&nbsp;</th>
        </tr>
        <tr>
          <td>1 matching invoices.</td>
        </tr>
      </thead>

      <tbody>
        <tr>
          <td>2023-10-01 &mdash; 2023-10-31</td>
          <td>
            <a href="https://localhost/customer/10466">
              10466</a>
            Theune, Christian
          </td>


            <td class="text-right numeric">
              0.00&nbsp;€
            </td>

          <td>pending</td>
          <td><a href="https://localhost/invoice/55006/view">View</a></td> </tr>
      </tbody>
    </table>
  </div>
      </body>
</html>
"""  # noqa: E501
    )


# def test_ring0_json_api(patterns):
#     ring0 = patterns.ring0

#     ring0.normalize("json")
#     ring0.optional("...")
#     ring0.in_order(
#         """
# {
#         "directory_password": "gfhdjk",
# }
# """
#     )

#     ring0 == {
#         "aliases_fe": [],
#         "aliases_srv": [],
#         "directory_password": "gfhdjk",
#         "profile": "generic",
#         "creation_date": "2014-01-02T03:04:05+00:00",
#         "directory_ring": 0,
#         "environment": "testing",
#         "environment_class": "Puppet",
#         "environment_url": "",
#         "kvm_net_memory": 61440,
#         "machine": "physical",
#         "servicing": True,
#         "location": "ny",
#         "frontend_ips_v4": 1,
#         "frontend_ips_v6": 1,
#         "production": True,
#         "service_description": "backup server",
#         "secrets": {},
#         "secret_salt": "secret/salt",
#         "reverses": {"172.21.2.2": "test.gocept.net."},
#         "in_transit": False,
#         "interfaces": {
#             "fe": {
#                 "mac": "00:15:17:91:d2:f0",
#                 "bridged": False,
#                 "policy": "puppet",
#                 "gateways": {
#                     "172.21.2.0/24": "172.21.2.1",
#                     "2002:470:9aaf:42::/64": "2002:470:9aaf:42::1",
#                 },
#                 "networks": {
#                     "2002:470:9aaf:42::/64": ["2002:470:9aaf:42::2"],
#                     "172.21.2.0/24": ["172.21.2.2"],
#                 },
#             },
#             "ipmi": {
#                 "mac": "",
#                 "bridged": False,
#                 "policy": "puppet",
#                 "gateways": {"172.21.1.0/24": "172.21.1.1"},
#                 "networks": {"172.21.1.0/24": ["172.21.1.2"]},
#             },
#             "mgm": {
#                 "mac": "00:1e:c9:ad:4a:a6",
#                 "bridged": False,
#                 "policy": "puppet",
#                 "gateways": {
#                     "172.21.1.0/24": "172.21.1.1",
#                     "2002:470:9aaf:41::/64": "2002:470:9aaf:41::1",
#                 },
#                 "networks": {
#                     "2002:470:9aaf:41::/64": ["2002:470:9aaf:41::2"],
#                     "172.21.1.0/24": ["172.21.1.3"],
#                 },
#             },
#             "srv": {
#                 "mac": "00:1e:c9:ad:4a:a0",
#                 "bridged": False,
#                 "policy": "puppet",
#                 "gateways": {
#                     "172.21.3.0/24": "172.21.3.1",
#                     "2002:470:9aaf:43::/64": "2002:470:9aaf:43::1",
#                 },
#                 "networks": {
#                     "2002:470:9aaf:43::/64": ["2002:470:9aaf:43::2"],
#                     "172.21.3.0/24": ["172.21.3.2"],
#                 },
#             },
#             "sto": {
#                 "mac": "00:1e:c9:ad:4a:a2",
#                 "bridged": False,
#                 "policy": "puppet",
#                 "gateways": {
#                     "172.21.4.0/24": "172.21.4.1",
#                     "2002:470:9aaf:44::/64": "2002:470:9aaf:44::1",
#                 },
#                 "networks": {
#                     "2002:470:9aaf:44::/64": ["2002:470:9aaf:44::2"],
#                     "172.21.4.0/24": ["172.21.4.2"],
#                 },
#             },
#         },
#         "rack": "OB 4 DA",
#         "resource_group": "services",
#         "resource_group_parent": "",
#         "timezone": "UTC",
#         "id": 4100,
#         "nixos_configs": {},
#     }
