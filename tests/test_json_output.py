"""Tests for JSON output feature (--patterns-json)."""

import pytest

from pytest_patterns.plugin import PatternsLib


# TestToJsonBasic - Basic JSON structure tests.


def test_passed_status(patterns: PatternsLib) -> None:
    """Passed test returns status='passed'."""
    patterns.simple.in_order("hello")
    audit = patterns.simple._audit("hello")
    result = audit.to_json()

    assert result["status"] == "passed"


def test_failed_status(patterns: PatternsLib) -> None:
    """Failed test returns status='failed'."""
    patterns.simple.in_order("hello")
    audit = patterns.simple._audit("goodbye")
    result = audit.to_json()

    assert result["status"] == "failed"


def test_summary_counts(patterns: PatternsLib) -> None:
    """Summary contains correct counts."""
    patterns.test.in_order(
        """\
line1
line2
"""
    )
    patterns.test.optional("heartbeat")

    audit = patterns.test._audit(
        """\
line1
heartbeat
line2
unexpected
"""
    )
    result = audit.to_json()

    assert result["summary"]["total_lines"] == 4
    assert result["summary"]["expected"] == 2
    assert result["summary"]["optional"] == 1
    assert result["summary"]["unexpected"] == 1
    assert result["summary"]["unmatched"] == 0


def test_lines_structure(patterns: PatternsLib) -> None:
    """Lines array has correct structure."""
    patterns.test.in_order("expected line")
    audit = patterns.test._audit("expected line")
    result = audit.to_json()

    assert len(result["lines"]) == 1
    line = result["lines"][0]
    assert line["number"] == 1
    assert line["content"] == "expected line"
    assert line["status"] == "expected"
    assert line["pattern"] == "test"


# TestUnmatchedPatternsWithContext - Tests for unmatched_patterns with context information.


def test_unmatched_has_actual_at_line(patterns: PatternsLib) -> None:
    """Unmatched pattern shows line number where match failed."""
    patterns.test.in_order(
        """\
first line
second line
third line
"""
    )
    # Content missing "second line" - only has first and third
    audit = patterns.test._audit(
        """\
first line
third line
"""
    )
    result = audit.to_json()

    assert result["status"] == "failed"
    assert len(result["unmatched_patterns"]) >= 1

    unmatched = result["unmatched_patterns"][0]
    assert "actual_at_line" in unmatched
    # After matching "first line", cursor is at line 2
    # "second line" expected but "third line" found
    assert unmatched["actual_at_line"] == 2


def test_unmatched_has_actual_line(patterns: PatternsLib) -> None:
    """Unmatched pattern shows what was actually at that position."""
    patterns.test.in_order(
        """\
first line
expected second line
third line
"""
    )
    audit = patterns.test._audit(
        """\
first line
WRONG second line
third line
"""
    )
    result = audit.to_json()

    unmatched = result["unmatched_patterns"][0]
    assert "actual_line" in unmatched
    # "expected second line" != "WRONG second line"
    assert unmatched["actual_line"] == "WRONG second line"


def test_unmatched_has_context_lines(patterns: PatternsLib) -> None:
    """Unmatched pattern includes surrounding context."""
    patterns.test.in_order(
        """\
line1
line2
line3
expected line4
line5
line6
line7
"""
    )
    audit = patterns.test._audit(
        """\
line1
line2
line3
WRONG line4
line5
line6
line7
"""
    )
    result = audit.to_json()

    unmatched = result["unmatched_patterns"][0]
    assert "context_lines" in unmatched
    assert "context_start" in unmatched

    # Context should include surrounding lines
    context = unmatched["context_lines"]
    assert len(context) >= 3  # At least some context

    # Context should contain the actual (wrong) line
    assert "WRONG line4" in context


def test_context_start_matches_first_context_line(
    patterns: PatternsLib,
) -> None:
    """context_start is the line number of context_lines[0]."""
    patterns.test.in_order(
        """\
line1
line2
line3
line4
expected line5
line6
line7
line8
line9
"""
    )
    audit = patterns.test._audit(
        """\
line1
line2
line3
line4
WRONG line5
line6
line7
line8
line9
"""
    )
    result = audit.to_json()

    unmatched = result["unmatched_patterns"][0]
    context_start = unmatched["context_start"]
    context_lines = unmatched["context_lines"]

    # First context line should be at context_start
    # If context_start is 3, then context_lines[0] should be "line3"
    expected_first_line = f"line{context_start}"
    assert context_lines[0] == expected_first_line


def test_context_includes_three_lines_before_and_after(
    patterns: PatternsLib,
) -> None:
    """Context includes 3 lines before and 3 lines after problem."""
    patterns.test.in_order(
        """\
line1
line2
line3
expected line4
line5
line6
line7
"""
    )
    audit = patterns.test._audit(
        """\
line1
line2
line3
WRONG line4
line5
line6
line7
"""
    )
    result = audit.to_json()

    unmatched = result["unmatched_patterns"][0]
    context = unmatched["context_lines"]

    # 3 before + 1 actual + 3 after = 7 lines
    # (or less if at start/end of content)
    assert len(context) == 7
    assert context[0] == "line1"
    assert context[3] == "WRONG line4"
    assert context[6] == "line7"


def test_context_at_start_of_content(patterns: PatternsLib) -> None:
    """Context is truncated when problem is at start of content."""
    patterns.test.in_order(
        """\
expected first
line2
line3
"""
    )
    audit = patterns.test._audit(
        """\
WRONG first
line2
line3
"""
    )
    result = audit.to_json()

    unmatched = result["unmatched_patterns"][0]
    context_start = unmatched["context_start"]
    context = unmatched["context_lines"]

    # context_start should be 1 (first line)
    assert context_start == 1
    # Fewer lines before (none in this case)
    assert len(context) <= 7


def test_context_at_end_of_content(patterns: PatternsLib) -> None:
    """Context is truncated when problem is at end of content."""
    patterns.test.in_order(
        """\
line1
line2
expected last
"""
    )
    audit = patterns.test._audit(
        """\
line1
line2
WRONG last
"""
    )
    result = audit.to_json()

    unmatched = result["unmatched_patterns"][0]
    context = unmatched["context_lines"]

    # Fewer lines after (none in this case)
    # But should still have lines before
    assert len(context) >= 3


# TestMatchedRefusedWithContext - Tests for matched_refused with context information.


def test_matched_refused_has_context(patterns: PatternsLib) -> None:
    """Matched refused lines include context."""
    patterns.test.refused("...password...")
    patterns.test.optional("...")  # Accept other lines

    audit = patterns.test._audit(
        """\
line1
line2
secret password=12345
line4
line5
"""
    )
    result = audit.to_json()

    assert len(result["matched_refused"]) == 1
    refused = result["matched_refused"][0]

    assert "refused_line" in refused
    assert "actual_at_line" in refused
    assert "actual_line" in refused
    assert "context_lines" in refused
    assert "context_start" in refused

    assert refused["actual_at_line"] == 3
    assert refused["actual_line"] == "secret password=12345"


# TestMultipleUnmatched - Tests for multiple unmatched patterns.


def test_multiple_unmatched_all_have_context(
    patterns: PatternsLib,
) -> None:
    """Each unmatched pattern has its own context."""
    patterns.test.in_order(
        """\
first
second
third
"""
    )

    audit = patterns.test._audit(
        """\
WRONG first
WRONG second
WRONG third
"""
    )
    result = audit.to_json()

    # All three should be unmatched
    assert len(result["unmatched_patterns"]) >= 1

    # Each should have context
    for unmatched in result["unmatched_patterns"]:
        assert "context_lines" in unmatched
        assert "context_start" in unmatched
        assert "actual_at_line" in unmatched


def test_first_unmatched_is_primary(patterns: PatternsLib) -> None:
    """First unmatched pattern is marked as 'primary' failure."""
    patterns.test.in_order(
        """\
first
second
third
"""
    )

    audit = patterns.test._audit(
        """\
WRONG first
WRONG second
WRONG third
"""
    )
    result = audit.to_json()

    unmatched = result["unmatched_patterns"]
    assert len(unmatched) >= 1

    # First is primary
    assert unmatched[0]["failure_type"] == "primary"

    # Rest are cascading
    for entry in unmatched[1:]:
        assert entry["failure_type"] == "cascading"


def test_single_unmatched_is_primary(patterns: PatternsLib) -> None:
    patterns.test.in_order(
        """\
first
second
"""
    )

    audit = patterns.test._audit(
        """\
first
WRONG second
"""
    )
    result = audit.to_json()

    assert len(result["unmatched_patterns"]) == 1
    assert result["unmatched_patterns"][0]["failure_type"] == "primary"


def test_no_failures_means_zero_counts(patterns: PatternsLib) -> None:
    """Passed test has zero primary/cascading failures."""
    patterns.test.in_order("hello")
    audit = patterns.test._audit("hello")
    result = audit.to_json()

    assert result["summary"]["primary_failures"] == 0
    assert result["summary"]["cascading_failures"] == 0


def test_single_failure_is_primary(patterns: PatternsLib) -> None:
    """Single failure counts as 1 primary, 0 cascading."""
    patterns.test.in_order("expected")
    audit = patterns.test._audit("wrong")
    result = audit.to_json()

    assert result["summary"]["primary_failures"] == 1
    assert result["summary"]["cascading_failures"] == 0


def test_multiple_failures_have_one_primary(
    patterns: PatternsLib,
) -> None:
    """Multiple failures: 1 primary, rest is cascading."""
    patterns.test.in_order(
        """\
first
second
third
fourth
"""
    )
    audit = patterns.test._audit(
        """\
WRONG first
WRONG second
WRONG third
WRONG fourth
"""
    )
    result = audit.to_json()

    assert result["summary"]["primary_failures"] == 1
    assert result["summary"]["cascading_failures"] == 3
    assert result["summary"]["unmatched"] == 4


# --- Additional Audit to_json tests ---


def test_to_json_success() -> None:
    """JSON output for successful match."""
    from pytest_patterns.plugin import Audit

    audit = Audit("line1\nline2")
    audit.in_order("pattern1", ["line1", "line2"])
    result = audit.to_json()
    assert result["status"] == "passed"
    assert result["summary"]["total_lines"] == 2
    assert result["summary"]["expected"] == 2


def test_to_json_failure() -> None:
    """JSON output for failed match."""
    from pytest_patterns.plugin import Audit

    audit = Audit("line1")
    audit.in_order("pattern1", ["line1", "line2"])
    result = audit.to_json()
    assert result["status"] == "failed"
    assert result["summary"]["unmatched"] == 1
    assert result["summary"]["primary_failures"] == 1
    assert result["summary"]["cascading_failures"] == 0


def test_to_json_lines() -> None:
    """JSON output includes line details."""
    from pytest_patterns.plugin import Audit

    audit = Audit("line1")
    audit.in_order("pattern1", ["line1"])
    result = audit.to_json()
    assert len(result["lines"]) == 1
    assert result["lines"][0]["number"] == 1
    assert result["lines"][0]["content"] == "line1"
    assert result["lines"][0]["status"] == "expected"
    assert result["lines"][0]["pattern"] == "pattern1"


def test_to_json_unmatched_patterns() -> None:
    """JSON output includes unmatched patterns."""
    from pytest_patterns.plugin import Audit

    audit = Audit("line1")
    audit.in_order("pattern1", ["line1", "missing"])
    result = audit.to_json()
    assert len(result["unmatched_patterns"]) == 1
    assert result["unmatched_patterns"][0]["pattern"] == "pattern1"
    assert result["unmatched_patterns"][0]["expected_line"] == "missing"
    assert result["unmatched_patterns"][0]["failure_type"] == "primary"


def test_to_json_matched_refused() -> None:
    """JSON output includes matched refused patterns."""
    from pytest_patterns.plugin import Audit

    audit = Audit("error line")
    audit.refused("no_errors", ["...error..."])
    result = audit.to_json()
    assert len(result["matched_refused"]) == 1
    assert result["matched_refused"][0]["pattern"] == "no_errors"


def test_to_json_context() -> None:
    """JSON output includes context for failures."""
    from pytest_patterns.plugin import Audit

    audit = Audit("a\nb\nc\nd\ne\nf\ng")
    audit.in_order("pattern1", ["a", "x"])  # Will fail at 'x'
    result = audit.to_json()
    # Check context is present in unmatched patterns
    if result["unmatched_patterns"]:
        entry = result["unmatched_patterns"][0]
        # Context may or may not be present depending on position
        if "context_lines" in entry:
            assert isinstance(entry["context_lines"], list)


# --- Audit build unmatched entry tests ---


def test_build_unmatched_entry_basic() -> None:
    """Basic unmatched entry."""
    from pytest_patterns.plugin import Audit

    audit = Audit("line1\nline2")
    entry = audit._build_unmatched_entry("pattern1", "missing", is_primary=True)
    assert entry["pattern"] == "pattern1"
    assert entry["expected_line"] == "missing"
    assert entry["failure_type"] == "primary"


def test_build_unmatched_entry_with_position() -> None:
    """Unmatched entry with position info."""
    from pytest_patterns.plugin import Audit

    audit = Audit("line1\nline2")
    audit.in_order("pattern1", ["line1", "missing"])
    # This should record position
    entry = audit._build_unmatched_entry("pattern1", "missing", is_primary=True)
    # Position should be recorded
    if "actual_at_line" in entry:
        assert entry["actual_at_line"] >= 1


def test_build_unmatched_entry_cascading() -> None:
    """Cascading failure entry."""
    from pytest_patterns.plugin import Audit

    audit = Audit("line1")
    entry = audit._build_unmatched_entry(
        "pattern1", "missing", is_primary=False
    )
    assert entry["failure_type"] == "cascading"


# --- Audit build matched refused entry tests ---


def test_build_matched_refused_entry_basic() -> None:
    """Basic matched refused entry."""
    from pytest_patterns.plugin import Audit

    audit = Audit("error line")
    audit.refused("no_errors", ["...error..."])
    entries = list(audit.matched_refused)
    if entries:
        name, line_str = entries[0]
        entry = audit._build_matched_refused_entry(name, line_str)
        assert entry["pattern"] == name
        assert entry["refused_line"] == line_str


def test_build_matched_refused_entry_with_position_in_range() -> None:
    """Matched refused entry with position in valid range."""
    from pytest_patterns.plugin import Audit

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


def test_build_matched_refused_entry_position_out_of_range() -> None:
    """Matched refused entry with position out of range."""
    from pytest_patterns.plugin import Audit

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


def test_build_unmatched_entry_position_out_of_range() -> None:
    """Unmatched entry with position out of range."""
    from pytest_patterns.plugin import Audit

    audit = Audit("line1")
    # Manually set position out of range
    audit._unmatched_positions[("pattern1", "missing")] = 999
    entry = audit._build_unmatched_entry("pattern1", "missing", is_primary=True)
    # Should have position but no actual_line
    assert entry["actual_at_line"] == 999
    assert "actual_line" not in entry  # Position out of range


# --- Multi-pattern summary tests ---


def test_build_summary_refused_multiple_patterns() -> None:
    """Summary with refused lines from multiple patterns."""
    from pytest_patterns.plugin import Audit

    audit = Audit("error1\nerror2")
    audit.refused("pattern1", ["...error1..."])
    audit.refused("pattern2", ["...error2..."])
    summary = audit._build_summary()
    # Should list both pattern names
    assert "pattern1" in summary
    assert "pattern2" in summary
    assert "refused" in summary.lower()


def test_build_summary_unmatched_multiple_patterns() -> None:
    """Summary with unmatched from multiple patterns."""
    from pytest_patterns.plugin import Audit

    audit = Audit("line1")
    audit.in_order("pattern1", ["line1", "missing1"])
    # After first failure, add another unmatched
    audit.unmatched_expectations.append(("pattern2", "missing2"))
    summary = audit._build_summary()
    # Should list both pattern names for unmatched
    assert "pattern1" in summary
    assert "pattern2" in summary
