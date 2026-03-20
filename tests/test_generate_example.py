"""Tests for generate_example() feature."""

import pytest

from pytest_patterns.plugin import PatternsLib


# TestGenerateExampleBasic - Basic generate_example tests.


def test_in_order_returns_exact_lines(patterns):
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
    patterns,
):
    """continuous pattern returns exact lines."""
    patterns.simple.continuous(
        """\
line1
line2
"""
    )
    example = patterns.simple.generate_example()

    assert example == "line1\nline2"


def test_optional_returns_exact_lines(patterns):
    """optional pattern returns lines (as if they appear)."""
    patterns.simple.optional(
        """\
maybe1
maybe2
"""
    )
    example = patterns.simple.generate_example()

    assert example == "maybe1\nmaybe2"


# TestGenerateExampleWildcards - Test wildcard handling in generate_example.


def test_ellipsis_replaced_with_placeholder(
    patterns,
):
    """... is replaced with [...] placeholder."""
    patterns.simple.in_order("...error...")
    example = patterns.simple.generate_example()

    assert example == "[...]error[...]"


def test_ellipsis_in_middle(patterns):
    """... in middle of line is replaced."""
    patterns.simple.in_order("prefix...suffix")
    example = patterns.simple.generate_example()

    assert example == "prefix[...]suffix"


def test_empty_line_marker(patterns):
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


# TestGenerateExampleRefused - Test refused pattern handling.


def test_refused_ignored(patterns):
    """refused patterns are ignored in example."""
    patterns.simple.in_order("good")
    patterns.simple.refused("...bad...")
    example = patterns.simple.generate_example()

    assert example == "good"


def test_refused_only_returns_empty(patterns):
    """pattern with only refused returns empty string."""
    patterns.simple.refused("...error...")
    example = patterns.simple.generate_example()

    assert example == ""


# TestGenerateExampleMerge - Test merge handling in generate_example.


def test_merge_combines_patterns(patterns):
    """merge combines lines from all patterns."""
    patterns.first.in_order("line1")
    patterns.second.in_order("line2")

    patterns.combined.merge("first", "second")
    example = patterns.combined.generate_example()

    # Order from merge: first, then second
    assert "line1" in example
    assert "line2" in example


def test_merge_with_optional(patterns):
    """merge with optional includes optional lines."""
    patterns.required.in_order("must")
    patterns.maybe.optional("optional")

    patterns.full.merge("required", "maybe")
    example = patterns.full.generate_example()

    assert "must" in example
    assert "optional" in example


# TestGenerateExampleMixed - Test mixed pattern types.


def test_mixed_in_order_and_continuous(patterns):
    """mixed in_order and continuous patterns."""
    patterns.simple.in_order("first")
    patterns.simple.continuous("second")
    example = patterns.simple.generate_example()

    # Both should appear (order: ops order)
    assert "first" in example
    assert "second" in example


def test_empty_pattern_returns_empty(patterns):
    """pattern with no ops returns empty string."""
    example = patterns.empty.generate_example()

    assert example == ""


# TestGenerateExampleModes - Test text generation modes.


def test_zen_mode_replaces_with_zen_words(patterns):
    """zen mode replaces ... with words from Zen of Python."""
    patterns.simple.in_order("prefix...suffix")
    example = patterns.simple.generate_example(mode="zen")

    assert example.startswith("prefix")
    assert example.endswith("suffix")
    assert "[...]" not in example
    # Should have 2 words in the middle (space-separated)
    middle = example[len("prefix") : -len("suffix")]
    assert len(middle.split()) == 2


def test_mra_mode_replaces_with_rot13(patterns):
    """mra mode replaces ... with ROT13-encoded words."""
    patterns.simple.in_order("prefix...suffix")
    example = patterns.simple.generate_example(mode="mra")

    assert example.startswith("prefix")
    assert example.endswith("suffix")
    assert "[...]" not in example
    # Should have 2 words in the middle
    middle = example[len("prefix") : -len("suffix")]
    assert len(middle.split()) == 2


def test_placeholder_mode_is_default(patterns):
    """placeholder mode is the default."""
    patterns.simple.in_order("prefix...suffix")
    example = patterns.simple.generate_example()

    assert example == "prefix[...]suffix"


def test_mode_parameter_overrides_class_default(patterns):
    """mode parameter overrides Pattern.example_mode."""
    patterns.simple.in_order("prefix...suffix")
    patterns.simple.example_mode = "zen"
    example = patterns.simple.generate_example(mode="placeholder")

    assert example == "prefix[...]suffix"


def test_zen_mode_sequential_words(patterns):
    """zen mode uses sequential words for consistency."""
    patterns.multi.in_order("...-...-... end")
    example = patterns.multi.generate_example(mode="zen")

    # Should have 3 different filler sections
    parts = example.split("-")
    assert len(parts) == 3
    # Each part should have 2 words (inline wildcards)
    # Last part ends with " end" so we check before that
    for part in parts[:-1]:
        assert len(part.split()) == 2
    # Last part: 2 words + "end" (with space before)
    last_words = parts[-1].split()
    assert len(last_words) == 3
    assert last_words[-1] == "end"


def test_zen_mode_empty_line(patterns):
    """zen mode handles empty-line marker correctly."""
    patterns.simple.in_order(
        """\
line1
<empty-line>
line2
"""
    )
    example = patterns.simple.generate_example(mode="zen")

    assert example == "line1\n\nline2"


def test_class_level_example_mode(patterns):
    """Pattern.example_mode can be set to change default mode."""
    patterns.simple.in_order("...test...")
    patterns.simple.example_mode = "zen"
    example = patterns.simple.generate_example()

    assert "[...]" not in example
    assert "test" in example
