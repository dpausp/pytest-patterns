"""Tests for JSON output feature (--patterns-json)."""

import pytest

from pytest_patterns.plugin import PatternsLib


class TestToJsonBasic:
    """Basic JSON structure tests."""

    def test_passed_status(self, patterns: PatternsLib) -> None:
        """Passed test returns status='passed'."""
        patterns.simple.in_order("hello")
        audit = patterns.simple._audit("hello")
        result = audit.to_json()

        assert result["status"] == "passed"

    def test_failed_status(self, patterns: PatternsLib) -> None:
        """Failed test returns status='failed'."""
        patterns.simple.in_order("hello")
        audit = patterns.simple._audit("goodbye")
        result = audit.to_json()

        assert result["status"] == "failed"

    def test_summary_counts(self, patterns: PatternsLib) -> None:
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

    def test_lines_structure(self, patterns: PatternsLib) -> None:
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


class TestUnmatchedPatternsWithContext:
    """Tests for unmatched_patterns with context information."""

    def test_unmatched_has_actual_at_line(self, patterns: PatternsLib) -> None:
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

    def test_unmatched_has_actual_line(self, patterns: PatternsLib) -> None:
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

    def test_unmatched_has_context_lines(self, patterns: PatternsLib) -> None:
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
        self, patterns: PatternsLib
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
        self, patterns: PatternsLib
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

    def test_context_at_start_of_content(self, patterns: PatternsLib) -> None:
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

    def test_context_at_end_of_content(self, patterns: PatternsLib) -> None:
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


class TestMatchedRefusedWithContext:
    """Tests for matched_refused with context information."""

    def test_matched_refused_has_context(self, patterns: PatternsLib) -> None:
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


class TestMultipleUnmatched:
    """Tests for multiple unmatched patterns."""

    def test_multiple_unmatched_all_have_context(
        self, patterns: PatternsLib
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
