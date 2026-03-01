"""Tests for generate_example() feature."""

import pytest

from pytest_patterns.plugin import PatternsLib


class TestGenerateExampleBasic:
    """Basic generate_example tests."""

    def test_in_order_returns_exact_lines(self, patterns: PatternsLib) -> None:
        """in_order pattern returns exact lines."""
        patterns.simple.in_order(
            """\
line1
line2
line3
"""
        )
        example = patterns.simple.generate_example()

        assert example == "line1\nline2\nline3"

    def test_continuous_returns_exact_lines(
        self, patterns: PatternsLib
    ) -> None:
        """continuous pattern returns exact lines."""
        patterns.simple.continuous(
            """\
line1
line2
"""
        )
        example = patterns.simple.generate_example()

        assert example == "line1\nline2"

    def test_optional_returns_exact_lines(self, patterns: PatternsLib) -> None:
        """optional pattern returns lines (as if they appear)."""
        patterns.simple.optional(
            """\
maybe1
maybe2
"""
        )
        example = patterns.simple.generate_example()

        assert example == "maybe1\nmaybe2"


class TestGenerateExampleWildcards:
    """Test wildcard handling in generate_example."""

    def test_ellipsis_replaced_with_placeholder(
        self, patterns: PatternsLib
    ) -> None:
        """... is replaced with [...] placeholder."""
        patterns.simple.in_order("...error...")
        example = patterns.simple.generate_example()

        assert example == "[...]error[...]"

    def test_ellipsis_in_middle(self, patterns: PatternsLib) -> None:
        """... in middle of line is replaced."""
        patterns.simple.in_order("prefix...suffix")
        example = patterns.simple.generate_example()

        assert example == "prefix[...]suffix"

    def test_empty_line_marker(self, patterns: PatternsLib) -> None:
        """<empty-line> is replaced with empty string."""
        patterns.simple.in_order(
            """\
line1
<empty-line>
line2
"""
        )
        example = patterns.simple.generate_example()

        assert example == "line1\n\nline2"


class TestGenerateExampleRefused:
    """Test refused pattern handling."""

    def test_refused_ignored(self, patterns: PatternsLib) -> None:
        """refused patterns are ignored in example."""
        patterns.simple.in_order("good")
        patterns.simple.refused("...bad...")
        example = patterns.simple.generate_example()

        assert example == "good"

    def test_refused_only_returns_empty(self, patterns: PatternsLib) -> None:
        """pattern with only refused returns empty string."""
        patterns.simple.refused("...error...")
        example = patterns.simple.generate_example()

        assert example == ""


class TestGenerateExampleMerge:
    """Test merge handling in generate_example."""

    def test_merge_combines_patterns(self, patterns: PatternsLib) -> None:
        """merge combines lines from all patterns."""
        patterns.first.in_order("line1")
        patterns.second.in_order("line2")

        patterns.combined.merge("first", "second")
        example = patterns.combined.generate_example()

        # Order from merge: first, then second
        assert "line1" in example
        assert "line2" in example

    def test_merge_with_optional(self, patterns: PatternsLib) -> None:
        """merge with optional includes optional lines."""
        patterns.required.in_order("must")
        patterns.maybe.optional("optional")

        patterns.full.merge("required", "maybe")
        example = patterns.full.generate_example()

        assert "must" in example
        assert "optional" in example


class TestGenerateExampleMixed:
    """Test mixed pattern types."""

    def test_mixed_in_order_and_continuous(self, patterns: PatternsLib) -> None:
        """mixed in_order and continuous patterns."""
        patterns.simple.in_order("first")
        patterns.simple.continuous("second")
        example = patterns.simple.generate_example()

        # Both should appear (order: ops order)
        assert "first" in example
        assert "second" in example

    def test_empty_pattern_returns_empty(self, patterns: PatternsLib) -> None:
        """pattern with no ops returns empty string."""
        example = patterns.empty.generate_example()

        assert example == ""
