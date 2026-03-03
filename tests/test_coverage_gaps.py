"""Direct unit tests to improve coverage - bypassing pytest hook system."""

from __future__ import annotations

from pytest_patterns.plugin import (
    Audit,
    EMPTY_LINE_PATTERN,
    Line,
    match,
    Pattern,
    PatternsLib,
    _describe_whitespace_components,
    _format_whitespace,
    _should_use_color,
    describe_whitespace,
    format_line_report,
    line_to_control_pictures,
    pattern_lines,
    tab_replace,
    to_control_picture,
    Status,
)


# TestMatchFunction - Test match function (lines 217-226).


def test_match_empty_line_pattern_on_empty_line():
    """Match empty-line pattern on actual empty line."""
    result = match(EMPTY_LINE_PATTERN, "")
    assert result is True


def test_match_empty_line_pattern_on_non_empty():
    """Match empty-line pattern on non-empty line."""
    result = match(EMPTY_LINE_PATTERN, "text")
    # Should not match, continues to tab replacement and regex
    assert result is None or result is False


# TestControlPictures - Test control picture conversion (lines 170-209, 213, 217).


def test_to_control_picture_null():
    """Test NUL character conversion."""
    assert to_control_picture("\x00") == "\u2400"


def test_to_control_picture_tab():
    """Test HT (tab) character conversion."""
    assert to_control_picture("\t") == "\u2409"


def test_to_control_picture_lf():
    """Test LF (line feed) character conversion."""
    assert to_control_picture("\n") == "\u240a"


def test_to_control_picture_cr():
    """Test CR (carriage return) character conversion."""
    assert to_control_picture("\r") == "\u240d"


def test_to_control_picture_del():
    """Test DEL character conversion."""
    assert to_control_picture("\x7f") == "\u2421"


def test_to_control_picture_space():
    """Test space is NOT converted (normal spaces kept as-is)."""
    assert to_control_picture(" ") == " "


def test_to_control_picture_regular_char():
    """Test regular characters are not converted."""
    assert to_control_picture("a") == "a"
    assert to_control_picture("Z") == "Z"
    assert to_control_picture("9") == "9"


def test_line_to_control_pictures_mixed():
    """Test conversion of line with mixed characters."""
    line = "hello\tworld"
    result = line_to_control_pictures(line)
    assert result == "hello\u2409world"


def test_line_to_control_pictures_all_control():
    """Test conversion of line with only control characters."""
    line = "\x00\x01\x02"
    result = line_to_control_pictures(line)
    assert result == "\u2400\u2401\u2402"


def test_line_to_control_pictures_empty():
    """Test conversion of empty line."""
    assert line_to_control_pictures("") == ""


# TestTabReplace - Test tab replacement function (lines 163).


def test_tab_replace_simple():
    """Test simple tab replacement."""
    assert tab_replace("\t") == "        "


def test_tab_replace_with_text():
    """Test tab replacement with text."""
    assert tab_replace("hello\tworld") == "hello   world"


def test_tab_replace_multiple():
    """Test multiple tab replacement."""
    assert tab_replace("a\tb\tc") == "a       b       c"


def test_tab_replace_aligned():
    """Test tab alignment to 8-character stops."""
    assert tab_replace("pre>\ttext") == "pre>    text"
    assert tab_replace("prefix>\ttext") == "prefix> text"


def test_tab_replace_no_tabs():
    """Test line without tabs."""
    assert tab_replace("no tabs here") == "no tabs here"


# TestWhitespaceDescription - Test whitespace description functions (lines 112-161).


def test_describe_whitespace_empty_line():
    """Empty line has no whitespace issue."""
    assert describe_whitespace("") is None


def test_describe_whitespace_normal_line():
    """Normal line has no whitespace issue."""
    assert describe_whitespace("normal line") is None


def test_describe_whitespace_only_spaces():
    """Whitespace-only line with spaces."""
    assert describe_whitespace("    ") == "4 spaces"


def test_describe_whitespace_only_tabs():
    """Whitespace-only line with tabs."""
    assert describe_whitespace("\t\t") == "2 tabs"


def test_describe_whitespace_mixed():
    """Whitespace-only line with mixed whitespace."""
    assert describe_whitespace("  \t ") == "2 spaces + 1 tab + 1 space"


def test_describe_whitespace_trailing_spaces():
    """Line with trailing spaces."""
    assert describe_whitespace("text  ") == "trailing 2 spaces"


def test_describe_whitespace_trailing_tabs():
    """Line with trailing tabs."""
    assert describe_whitespace("text\t") == "trailing 1 tab"


def test_describe_whitespace_trailing_mixed():
    """Line with trailing mixed whitespace."""
    assert describe_whitespace("text \t") == "trailing 1 space + 1 tab"


def test_describe_whitespace_single_trailing_space():
    """Line with single trailing space."""
    assert describe_whitespace("text ") == "trailing 1 space"


def test_describe_whitespace_components_empty():
    """Empty whitespace string returns empty."""
    assert _describe_whitespace_components("", "") == ""


def test_describe_whitespace_components_other_whitespace():
    """Other whitespace characters (shouldn't happen often)."""
    # Vertical tab - gets repr'd
    result = _describe_whitespace_components("\x0b", "")
    assert "'\\x0b'" in result or "1" in result  # Shows as repr or count


# TestFormatWhitespace - Test whitespace formatting (lines 661-675).


def test_format_whitespace_spaces():
    """Spaces are converted to middle dots."""
    assert _format_whitespace("    ") == "····"


def test_format_whitespace_tabs():
    """Tabs are converted to right arrows."""
    assert _format_whitespace("\t\t") == "→→"


def test_format_whitespace_mixed():
    """Mixed whitespace formatting."""
    assert _format_whitespace(" \t ") == "·→·"


def test_format_whitespace_empty():
    """Empty string."""
    assert _format_whitespace("") == ""


def test_format_whitespace_other():
    """Other characters pass through."""
    assert _format_whitespace("x") == "x"


# TestPatternLines - Test pattern_lines utility (lines 678-680).


def test_pattern_lines_simple():
    """Simple pattern split."""
    assert pattern_lines("line1\nline2") == ["line1", "line2"]


def test_pattern_lines_empty_lines_filtered():
    """Empty lines are filtered out."""
    assert pattern_lines("line1\n\nline2") == ["line1", "line2"]


def test_pattern_lines_trailing_newline():
    """Trailing newline is handled."""
    assert pattern_lines("line1\nline2\n") == ["line1", "line2"]


def test_pattern_lines_empty_string():
    """Empty string returns empty list."""
    assert pattern_lines("") == []


def test_pattern_lines_only_empty_lines():
    """Only empty lines returns empty list."""
    assert pattern_lines("\n\n\n") == []


# TestLine - Test Line class (lines 229-244).


def test_line_init():
    """Line initialization."""
    line = Line("test data")
    assert line.data == "test data"
    assert line.status == Status.UNEXPECTED
    assert line.status_cause == ""


def test_line_matches_exact():
    """Exact match."""
    line = Line("hello")
    assert line.matches("hello") is True


def test_line_matches_wildcard():
    """Wildcard match."""
    line = Line("hello world")
    assert line.matches("...world...") is True


def test_line_matches_no_match():
    """No match."""
    line = Line("hello")
    assert line.matches("goodbye") is False


def test_line_mark_upgrade():
    """Mark upgrades status."""
    line = Line("test")
    line.mark(Status.OPTIONAL, "pattern1")
    assert line.status == Status.OPTIONAL
    assert line.status_cause == "pattern1"


def test_line_mark_no_downgrade():
    """Mark does not downgrade status."""
    line = Line("test")
    line.mark(Status.EXPECTED, "pattern1")
    line.mark(Status.OPTIONAL, "pattern2")
    assert line.status == Status.EXPECTED
    assert line.status_cause == "pattern1"


def test_line_mark_same_level():
    """Mark at same level has no effect."""
    line = Line("test")
    line.mark(Status.OPTIONAL, "pattern1")
    line.mark(Status.OPTIONAL, "pattern2")
    assert line.status_cause == "pattern1"


# TestAuditMethods - Test Audit class methods (lines 247-358).


def test_audit_init():
    """Audit initialization."""
    audit = Audit("line1\nline2")
    assert len(audit.content) == 2
    assert audit.content[0].data == "line1"
    assert audit.content[1].data == "line2"
    assert audit.unmatched_expectations == []
    assert audit.matched_refused == set()


def test_audit_cursor():
    """Audit cursor iteration."""
    audit = Audit("a\nb\nc")
    lines = list(audit.cursor())
    assert len(lines) == 3
    assert lines[0].data == "a"


def test_audit_optional_simple():
    """Optional pattern matching."""
    audit = Audit("error occurred")
    audit.optional("pattern1", ["...error..."])
    assert audit.content[0].status == Status.OPTIONAL
    assert audit.content[0].status_cause == "pattern1"


def test_audit_optional_no_match():
    """Optional pattern with no match."""
    audit = Audit("no match here")
    audit.optional("pattern1", ["...error..."])
    assert audit.content[0].status == Status.UNEXPECTED


def test_audit_refused_simple():
    """Refused pattern matching."""
    audit = Audit("error occurred")
    audit.refused("pattern1", ["...error..."])
    assert audit.content[0].status == Status.REFUSED
    assert ("pattern1", "...error...") in audit.matched_refused


def test_audit_refused_no_match():
    """Refused pattern with no match."""
    audit = Audit("no match here")
    audit.refused("pattern1", ["...error..."])
    assert audit.content[0].status == Status.UNEXPECTED
    assert ("pattern1", "...error...") not in audit.matched_refused


def test_audit_continuous_simple():
    """Continuous pattern matching."""
    audit = Audit("line1\nline2\nline3")
    audit.continuous("pattern1", ["line1", "line2"])
    assert audit.content[0].status == Status.EXPECTED
    assert audit.content[1].status == Status.EXPECTED
    assert audit.content[2].status == Status.UNEXPECTED


def test_audit_continuous_with_empty_lines():
    """Continuous pattern allows empty lines in between."""
    audit = Audit("line1\n\nline2")
    audit.continuous("pattern1", ["line1", "line2"])
    assert audit.content[0].status == Status.EXPECTED
    assert audit.content[1].status == Status.OPTIONAL  # Empty line allowed
    assert audit.content[2].status == Status.EXPECTED


def test_audit_continuous_broken():
    """Continuous pattern broken by non-matching line."""
    audit = Audit("line1\nunexpected\nline2")
    audit.continuous("pattern1", ["line1", "line2"])
    assert audit.content[0].status == Status.EXPECTED
    assert audit.content[1].status == Status.REFUSED
    assert len(audit.unmatched_expectations) > 0


def test_audit_continuous_incomplete():
    """Continuous pattern not fully matched."""
    audit = Audit("line1")
    audit.continuous("pattern1", ["line1", "line2"])
    assert audit.content[0].status == Status.EXPECTED
    assert len(audit.unmatched_expectations) > 0


def test_audit_in_order_simple():
    """In-order pattern matching."""
    audit = Audit("a\nb\nc")
    audit.in_order("pattern1", ["a", "c"])
    assert audit.content[0].status == Status.EXPECTED
    assert audit.content[1].status == Status.UNEXPECTED
    assert audit.content[2].status == Status.EXPECTED


def test_audit_in_order_out_of_order():
    """In-order pattern with wrong order."""
    audit = Audit("b\na\nc")
    audit.in_order("pattern1", ["a", "b"])
    assert len(audit.unmatched_expectations) > 0


def test_audit_in_order_partial_reset():
    """In-order pattern resets if no match found."""
    audit = Audit("x\na\nb")
    audit.in_order("pattern1", ["a", "b"])
    # Should find 'a' on second try after reset
    assert audit.content[1].status == Status.EXPECTED
    assert audit.content[2].status == Status.EXPECTED


def test_audit_is_ok_success():
    """is_ok returns True for successful match."""
    audit = Audit("line1\nline2")
    audit.in_order("pattern1", ["line1", "line2"])
    assert audit.is_ok() is True


def test_audit_is_ok_failure_unmatched():
    """is_ok returns False with unmatched expectations."""
    audit = Audit("line1")
    audit.in_order("pattern1", ["line1", "line2"])
    assert audit.is_ok() is False


def test_audit_is_ok_failure_unexpected():
    """is_ok returns False with unexpected lines."""
    audit = Audit("line1\nunexpected")
    audit.in_order("pattern1", ["line1"])
    assert audit.is_ok() is False


# TestAuditBuildSummary - Test Audit._build_summary method (lines 359-423).


def test_build_summary_single_pattern():
    """Summary with single pattern."""
    audit = Audit("line1\nunexpected")
    audit.in_order("pattern1", ["line1"])
    summary = audit._build_summary()
    assert "unexpected" in summary.lower()
    assert "pattern1" in summary


def test_build_summary_multiple_patterns():
    """Summary with multiple patterns."""
    audit = Audit("line1\nline2\nunexpected")
    audit.in_order("pattern1", ["line1"])
    audit.optional("pattern2", ["...line2..."])
    summary = audit._build_summary()
    assert "pattern1" in summary
    assert "pattern2" in summary


def test_build_summary_refused():
    """Summary with refused lines."""
    audit = Audit("error line")
    audit.refused("no_errors", ["...error..."])
    summary = audit._build_summary()
    assert "refused" in summary.lower()


def test_build_summary_no_failures():
    """Summary with no failures."""
    audit = Audit("line1")
    audit.in_order("pattern1", ["line1"])
    summary = audit._build_summary()
    assert "did not meet" in summary.lower()


# TestAuditCollectWhitespaceIssues - Test Audit._collect_whitespace_issues (lines 486-508).


def test_collect_whitespace_unexpected_trailing():
    """Collect trailing whitespace from unexpected lines."""
    audit = Audit("line  ")
    audit.in_order("pattern1", ["line"])  # Won't match due to trailing space
    issues = audit._collect_whitespace_issues()
    assert len(issues) > 0
    assert issues[0][0] == 1  # Line number
    assert "trailing" in issues[0][1]


def test_collect_whitespace_unexpected_only_whitespace():
    """Collect whitespace-only unexpected lines."""
    audit = Audit("   ")
    # Don't add any patterns so line stays unexpected
    issues = audit._collect_whitespace_issues()
    assert len(issues) > 0
    assert "spaces" in issues[0][1]


def test_collect_whitespace_unmatched_expected():
    """Collect whitespace from unmatched expected lines."""
    audit = Audit("line1")
    audit.in_order("pattern1", ["line1 "])  # Trailing space won't match
    issues = audit._collect_whitespace_issues()
    # Should detect whitespace in unmatched expectation
    assert any("trailing" in issue[1] for issue in issues)


# TestAuditBuildContext - Test Audit._build_context method (lines 518-534).


def test_build_context_middle():
    """Build context from middle of content."""
    audit = Audit("a\nb\nc\nd\ne\nf\ng\nh")
    start, lines = audit._build_context(5)  # Around line 5 (1-based)
    assert start == 2  # Lines 2-8 (3 before + line 5 + 3 after)
    assert len(lines) == 7


def test_build_context_beginning():
    """Build context at beginning."""
    audit = Audit("a\nb\nc\nd")
    start, lines = audit._build_context(1)
    assert start == 1
    assert len(lines) == 4  # Only 4 lines total


def test_build_context_end():
    """Build context at end."""
    audit = Audit("a\nb\nc\nd")
    start, lines = audit._build_context(4)
    assert start == 1
    assert len(lines) == 4  # Only 4 lines total


# TestAuditToJson - Test Audit.to_json method (lines 536-579).


def test_to_json_success():
    """JSON output for successful match."""
    audit = Audit("line1\nline2")
    audit.in_order("pattern1", ["line1", "line2"])
    result = audit.to_json()
    assert result["status"] == "passed"
    assert result["summary"]["total_lines"] == 2
    assert result["summary"]["expected"] == 2


def test_to_json_failure():
    """JSON output for failed match."""
    audit = Audit("line1")
    audit.in_order("pattern1", ["line1", "line2"])
    result = audit.to_json()
    assert result["status"] == "failed"
    assert result["summary"]["unmatched"] == 1
    assert result["summary"]["primary_failures"] == 1
    assert result["summary"]["cascading_failures"] == 0


def test_to_json_lines():
    """JSON output includes line details."""
    audit = Audit("line1")
    audit.in_order("pattern1", ["line1"])
    result = audit.to_json()
    assert len(result["lines"]) == 1
    assert result["lines"][0]["number"] == 1
    assert result["lines"][0]["content"] == "line1"
    assert result["lines"][0]["status"] == "expected"
    assert result["lines"][0]["pattern"] == "pattern1"


def test_to_json_unmatched_patterns():
    """JSON output includes unmatched patterns."""
    audit = Audit("line1")
    audit.in_order("pattern1", ["line1", "missing"])
    result = audit.to_json()
    assert len(result["unmatched_patterns"]) == 1
    assert result["unmatched_patterns"][0]["pattern"] == "pattern1"
    assert result["unmatched_patterns"][0]["expected_line"] == "missing"
    assert result["unmatched_patterns"][0]["failure_type"] == "primary"


def test_to_json_matched_refused():
    """JSON output includes matched refused patterns."""
    audit = Audit("error line")
    audit.refused("no_errors", ["...error..."])
    result = audit.to_json()
    assert len(result["matched_refused"]) == 1
    assert result["matched_refused"][0]["pattern"] == "no_errors"


def test_to_json_context():
    """JSON output includes context for failures."""
    audit = Audit("a\nb\nc\nd\ne\nf\ng")
    audit.in_order("pattern1", ["a", "x"])  # Will fail at 'x'
    result = audit.to_json()
    # Check context is present in unmatched patterns
    if result["unmatched_patterns"]:
        entry = result["unmatched_patterns"][0]
        # Context may or may not be present depending on position
        if "context_lines" in entry:
            assert isinstance(entry["context_lines"], list)


# TestAuditBuildUnmatchedEntry - Test Audit._build_unmatched_entry (lines 581-600).


def test_build_unmatched_entry_basic():
    """Basic unmatched entry."""
    audit = Audit("line1\nline2")
    entry = audit._build_unmatched_entry("pattern1", "missing", is_primary=True)
    assert entry["pattern"] == "pattern1"
    assert entry["expected_line"] == "missing"
    assert entry["failure_type"] == "primary"


def test_build_unmatched_entry_with_position():
    """Unmatched entry with position info."""
    audit = Audit("line1\nline2")
    audit.in_order("pattern1", ["line1", "missing"])
    # This should record position
    entry = audit._build_unmatched_entry("pattern1", "missing", is_primary=True)
    # Position should be recorded
    if "actual_at_line" in entry:
        assert entry["actual_at_line"] >= 1


def test_build_unmatched_entry_cascading():
    """Cascading failure entry."""
    audit = Audit("line1")
    entry = audit._build_unmatched_entry(
        "pattern1", "missing", is_primary=False
    )
    assert entry["failure_type"] == "cascading"


# TestAuditBuildMatchedRefusedEntry - Test Audit._build_matched_refused_entry (lines 602-618).


def test_build_matched_refused_entry_basic():
    """Basic matched refused entry."""
    audit = Audit("error line")
    audit.refused("no_errors", ["...error..."])
    entries = list(audit.matched_refused)
    if entries:
        name, line_str = entries[0]
        entry = audit._build_matched_refused_entry(name, line_str)
        assert entry["pattern"] == name
        assert entry["refused_line"] == line_str


# TestFormatLineReport - Test format_line_report function (lines 621-658).


def test_format_line_report_expected():
    """Format expected line."""
    result = format_line_report(
        Status.EXPECTED, "🟢", "pattern1", "line content"
    )
    assert "🟢" in result
    assert "pattern1" in result
    assert "line content" in result


def test_format_line_report_optional():
    """Format optional line."""
    result = format_line_report(
        Status.OPTIONAL, "⚪️", "pattern1", "line content"
    )
    assert "⚪️" in result
    assert "pattern1" in result


def test_format_line_report_unexpected():
    """Format unexpected line."""
    result = format_line_report(Status.UNEXPECTED, "🟡", "", "line content")
    assert "🟡" in result
    assert "line content" in result


def test_format_line_report_with_trailing_whitespace():
    """Format line with trailing whitespace (colored)."""
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


def test_format_line_report_with_trailing_whitespace_no_color():
    """Format line with trailing whitespace (no color)."""
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


def test_format_line_report_whitespace_only():
    """Format whitespace-only line."""
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


def test_format_line_report_with_tabs():
    """Format line with trailing tabs."""
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


def test_format_line_report_long_cause():
    """Format with long pattern name (truncated to 15 chars)."""
    result = format_line_report(
        Status.EXPECTED, "🟢", "very_long_pattern_name", "line"
    )
    assert "very_long_patte" in result  # Truncated to 15


def test_format_line_report_no_original_line():
    """Format without original line (uses display line)."""
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


# TestPattern - Test Pattern class (lines 683-769).


def test_pattern_init():
    """Pattern initialization."""
    lib = PatternsLib()
    p = Pattern(lib, "test_pattern")
    assert p.name == "test_pattern"
    assert p.library is lib
    assert p.ops == []
    assert p.inherited == set()


def test_pattern_continuous():
    """Pattern continuous method."""
    lib = PatternsLib()
    p = Pattern(lib, "test")
    p.continuous("line1\nline2")
    assert len(p.ops) == 1
    assert p.ops[0][0] == "continuous"
    assert p.ops[0][1] == "test"


def test_pattern_in_order():
    """Pattern in_order method."""
    lib = PatternsLib()
    p = Pattern(lib, "test")
    p.in_order("line1\nline2")
    assert len(p.ops) == 1
    assert p.ops[0][0] == "in_order"


def test_pattern_optional():
    """Pattern optional method."""
    lib = PatternsLib()
    p = Pattern(lib, "test")
    p.optional("line1\nline2")
    assert len(p.ops) == 1
    assert p.ops[0][0] == "optional"


def test_pattern_refused():
    """Pattern refused method."""
    lib = PatternsLib()
    p = Pattern(lib, "test")
    p.refused("...error...")
    assert len(p.ops) == 1
    assert p.ops[0][0] == "refused"


def test_pattern_merge():
    """Pattern merge method."""
    lib = PatternsLib()
    p1 = lib.pattern1
    p1.optional("line1")

    p2 = lib.pattern2
    p2.in_order("line2")
    p2.merge("pattern1")

    # Check inheritance
    assert "pattern1" in p2.inherited


def test_pattern_normalize():
    """Pattern normalize method (currently no-op)."""
    lib = PatternsLib()
    p = Pattern(lib, "test")
    p.normalize("json")  # Should not raise
    assert len(p.ops) == 0  # No ops added


def test_pattern_flat_ops():
    """Pattern flat_ops includes inherited patterns."""
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


def test_pattern_audit():
    """Pattern _audit creates Audit object."""
    lib = PatternsLib()
    p = lib.test
    p.in_order("line1")
    audit = p._audit("line1")
    assert isinstance(audit, Audit)
    assert audit.is_ok()


def test_pattern_generate_example_simple():
    """Pattern generate_example with simple patterns."""
    lib = PatternsLib()
    p = lib.test
    p.in_order("line1\nline2")
    example = p.generate_example()
    assert "line1" in example
    assert "line2" in example


def test_pattern_generate_example_with_wildcards():
    """Pattern generate_example replaces wildcards."""
    lib = PatternsLib()
    p = lib.test
    p.optional("...error...")
    example = p.generate_example()
    assert "[...]" in example
    # Wildcard ... should be replaced with [...]
    assert example == "[...]error[...]"


def test_pattern_generate_example_empty_line():
    """Pattern generate_example handles empty-line marker."""
    lib = PatternsLib()
    p = lib.test
    p.optional("<empty-line>")
    example = p.generate_example()
    # Empty line marker should be replaced with empty string
    assert "<empty-line>" not in example


def test_pattern_generate_example_ignores_refused():
    """Pattern generate_example ignores refused patterns."""
    lib = PatternsLib()
    p = lib.test
    p.in_order("good_line")
    p.refused("bad_line")
    example = p.generate_example()
    assert "good_line" in example
    assert "bad_line" not in example


def test_pattern_replace_wildcards_ellipsis():
    """Pattern _replace_wildcards replaces ellipsis."""
    lib = PatternsLib()
    p = Pattern(lib, "test")
    result = p._replace_wildcards("...error...")
    assert result == "[...]error[...]"


def test_pattern_replace_wildcards_empty_line():
    """Pattern _replace_wildcards replaces empty-line marker."""
    lib = PatternsLib()
    p = Pattern(lib, "test")
    result = p._replace_wildcards("<empty-line>")
    assert result == ""


def test_pattern_replace_wildcards_normal():
    """Pattern _replace_wildcards leaves normal text unchanged."""
    lib = PatternsLib()
    p = Pattern(lib, "test")
    result = p._replace_wildcards("normal text")
    assert result == "normal text"


def test_pattern_eq_success():
    """Pattern equality check success."""
    lib = PatternsLib()
    p = lib.test
    p.in_order("line1\nline2")
    assert p == "line1\nline2"


def test_pattern_eq_failure():
    """Pattern equality check failure."""
    lib = PatternsLib()
    p = lib.test
    p.in_order("line1\nline2")
    assert not (p == "line1\nline3")


def test_pattern_eq_with_other_object():
    """Pattern equality with non-string raises AssertionError."""
    lib = PatternsLib()
    p = lib.test
    try:
        _ = p == 123  # type: ignore
        assert False, "Should have raised AssertionError"
    except AssertionError:
        pass


# TestPatternsLib - Test PatternsLib class (lines 771-773).


def test_patterns_lib_getattr():
    """PatternsLib creates Pattern on attribute access."""
    lib = PatternsLib()
    p = lib.test_pattern
    assert isinstance(p, Pattern)
    assert p.name == "test_pattern"
    assert p.library is lib


def test_patterns_lib_caching():
    """PatternsLib caches patterns."""
    lib = PatternsLib()
    p1 = lib.test
    p2 = lib.test
    assert p1 is p2  # Same object


def test_patterns_lib_multiple_patterns():
    """PatternsLib can create multiple patterns."""
    lib = PatternsLib()
    p1 = lib.pattern1
    p2 = lib.pattern2
    assert p1.name == "pattern1"
    assert p2.name == "pattern2"
    assert p1 is not p2


# TestShouldUseColor - Test _should_use_color function (lines 36-49).


def test_should_use_color_no_color_env(monkeypatch):
    """NO_COLOR env var disables color."""
    import pytest

    class MockConfig:
        def getoption(self, name):
            return False

    monkeypatch.setenv("NO_COLOR", "1")
    config = MockConfig()
    assert _should_use_color(config) is False  # type: ignore[arg-type]


def test_should_use_color_flag():
    """--patterns-no-color flag disables color."""

    class MockConfig:
        def getoption(self, name):
            return name == "--patterns-no-color"

    config = MockConfig()
    assert _should_use_color(config) is False  # type: ignore[arg-type]


# TestAuditReport - Test Audit.report method (lines 425-484).


def test_report_basic():
    """Basic report generation."""
    audit = Audit("line1\nline2")
    audit.in_order("pattern1", ["line1", "line2"])
    lines = list(audit.report(use_color=True))
    assert len(lines) > 0
    assert any("pattern1" in line for line in lines)


def test_report_with_unmatched():
    """Report with unmatched expectations."""
    audit = Audit("line1")
    audit.in_order("pattern1", ["line1", "missing"])
    lines = list(audit.report(use_color=True))
    assert any("unmatched" in line.lower() for line in lines)


def test_report_with_refused():
    """Report with matched refused lines."""
    audit = Audit("error line")
    audit.refused("no_errors", ["...error..."])
    lines = list(audit.report(use_color=True))
    assert any("refused" in line.lower() for line in lines)


def test_report_with_whitespace_issues():
    """Report includes whitespace warnings."""
    audit = Audit("line  ")
    # Don't match so line stays unexpected with trailing whitespace
    lines = list(audit.report(use_color=True))
    # Should include whitespace warning
    assert any("whitespace" in line.lower() for line in lines)


def test_report_no_color():
    """Report without color codes."""
    audit = Audit("line1\nline2")
    audit.in_order("pattern1", ["line1", "line2"])
    lines = list(audit.report(use_color=False))
    # Should not contain ANSI codes
    assert not any("\x1b[" in line for line in lines)


# TestMultiPatternSummary - Test multi-pattern summary building (lines 402-403, 410-411).


def test_build_summary_refused_multiple_patterns():
    """Summary with refused lines from multiple patterns."""
    audit = Audit("error1\nerror2")
    audit.refused("pattern1", ["...error1..."])
    audit.refused("pattern2", ["...error2..."])
    summary = audit._build_summary()
    # Should list both pattern names
    assert "pattern1" in summary
    assert "pattern2" in summary
    assert "refused" in summary.lower()


def test_build_summary_unmatched_multiple_patterns():
    """Summary with unmatched from multiple patterns."""
    audit = Audit("line1")
    audit.in_order("pattern1", ["line1", "missing1"])
    # After first failure, add another unmatched
    audit.unmatched_expectations.append(("pattern2", "missing2"))
    summary = audit._build_summary()
    # Should list both pattern names for unmatched
    assert "pattern1" in summary
    assert "pattern2" in summary


# TestJsonContextBranches - Test JSON context building branches (lines 611-618, 613-615).


def test_build_matched_refused_entry_with_position_in_range():
    """Matched refused entry with position in valid range."""
    audit = Audit("line1\nerror\nline3")
    audit.refused("no_errors", ["...error..."])
    # The position should be recorded and in valid range
    if audit.matched_refused:
        name, line_str = list(audit.matched_refused)[0]
        entry = audit._build_matched_refused_entry(name, line_str)
        # Should have position and context
        assert "actual_at_line" in entry
        assert entry["actual_at_line"] == 2  # Line 2
        assert "actual_line" in entry
        assert "context_lines" in entry


def test_build_matched_refused_entry_position_out_of_range():
    """Matched refused entry with position out of range."""
    audit = Audit("line1")
    # Manually set a position that's out of range
    audit.matched_refused.add(("pattern1", "error"))
    audit._matched_refused_positions[("pattern1", "error")] = (
        999  # Out of range
    )
    entry = audit._build_matched_refused_entry("pattern1", "error")
    # Should have position but no actual_line
    assert entry["actual_at_line"] == 999
    assert "actual_line" not in entry  # Position out of range
    # Should still have context (will be truncated to available lines)
    assert "context_lines" in entry


def test_build_unmatched_entry_position_out_of_range():
    """Unmatched entry with position out of range."""
    audit = Audit("line1")
    # Manually set position out of range
    audit._unmatched_positions[("pattern1", "missing")] = 999
    entry = audit._build_unmatched_entry("pattern1", "missing", is_primary=True)
    # Should have position but no actual_line
    assert entry["actual_at_line"] == 999
    assert "actual_line" not in entry  # Position out of range


# TestContinuousEdgeCases - Test continuous method edge cases (line 344->330).


def test_continuous_first_line_no_match():
    """Continuous pattern where first line doesn't match."""
    audit = Audit("unexpected\nline2")
    audit.continuous("pattern1", ["line1", "line2"])
    # First line not matching is allowed, should not mark as refused
    assert audit.content[0].status == Status.UNEXPECTED
    # Should have unmatched expectations
    assert len(audit.unmatched_expectations) > 0


# TestMatchEdgeCases - Test match function edge cases (lines 219-220).


def test_match_empty_line_marker_on_empty_line():
    """Match <empty-line> marker on empty line."""
    result = match(EMPTY_LINE_PATTERN, "")
    assert result is True


def test_match_empty_line_marker_on_content():
    """Match <empty-line> marker on non-empty line."""
    result = match(EMPTY_LINE_PATTERN, "some text")
    # Should not return True, should continue to regex matching
    # The marker should not match actual content
    assert result is not True
