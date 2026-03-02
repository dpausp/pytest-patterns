from __future__ import annotations

import enum
import json
import re
import sys
from collections.abc import Iterator
from typing import Any

import pytest


@pytest.fixture
def patterns() -> PatternsLib:
    return PatternsLib()


def pytest_addoption(parser: pytest.Parser) -> None:
    """Add --patterns-json flag for structured agent output."""
    group = parser.getgroup("pytest-patterns")
    group.addoption(
        "--patterns-json",
        action="store_true",
        default=False,
        help="Output pattern match results as JSON for agents/CI",
    )


def pytest_assertrepr_compare(
    config: pytest.Config,
    op: str,
    left: Any,
    right: Any,
) -> list[str] | None:
    if op != "==":
        return None
    if isinstance(left, Pattern):
        audit = left._audit(right)
        if config.getoption("--patterns-json"):
            return [json.dumps(audit.to_json(), indent=2)]
        report_lines = list(audit.report())
        # Print full report to stderr (skip summary line, avoids truncation)
        for line in report_lines[1:]:
            print(line, file=sys.stderr)
        # Return only summary for assertion explanation
        return [report_lines[0]] if report_lines else None
    elif isinstance(right, Pattern):
        audit = right._audit(left)
        if config.getoption("--patterns-json"):
            return [json.dumps(audit.to_json(), indent=2)]
        report_lines = list(audit.report())
        # Print full report to stderr (skip summary line, avoids truncation)
        for line in report_lines[1:]:
            print(line, file=sys.stderr)
        # Return only summary for assertion explanation
        return [report_lines[0]] if report_lines else None
    else:
        return None


class Status(enum.Enum):
    UNEXPECTED = 1
    OPTIONAL = 2
    EXPECTED = 3
    REFUSED = 4

    @property
    def symbol(self) -> str:
        return STATUS_SYMBOLS[self]


STATUS_SYMBOLS = {
    Status.UNEXPECTED: "🟡",
    Status.EXPECTED: "🟢",
    Status.OPTIONAL: "⚪️",
    Status.REFUSED: "🔴",
}

EMPTY_LINE_PATTERN = "<empty-line>"

# ANSI codes for whitespace highlighting
YELLOW_BG = "\x1b[43m"
RESET = "\x1b[0m"


def describe_whitespace(line: str) -> str | None:
    """Describe whitespace issue in a line, if any.

    Returns None if no whitespace issue, otherwise a description like:
    - "4 spaces" (whitespace-only line)
    - "trailing 2 spaces" (line with trailing whitespace)
    - "2 spaces + 1 tab" (mixed whitespace)
    """
    # Empty line is not a whitespace issue
    if not line:
        return None

    # Check for whitespace-only line
    if not line.strip():
        return _describe_whitespace_components(line, "")

    # Check for trailing whitespace
    stripped = line.rstrip()
    if stripped != line:
        trailing = line[len(stripped) :]
        return _describe_whitespace_components(trailing, "trailing ")

    return None


def _describe_whitespace_components(ws: str, prefix: str) -> str:
    """Build description like '4 spaces' or '2 spaces + 1 tab + 2 spaces'."""
    if not ws:
        return ""

    components: list[str] = []
    i = 0
    while i < len(ws):
        char = ws[i]
        count = 1
        while i + count < len(ws) and ws[i + count] == char:
            count += 1

        if char == " ":
            components.append(f"{count} space{'s' if count != 1 else ''}")
        elif char == "\t":
            components.append(f"{count} tab{'s' if count != 1 else ''}")
        else:
            # Other whitespace (shouldn't happen often)
            components.append(f"{count} {char!r}")

        i += count

    return prefix + " + ".join(components)


def tab_replace(line: str) -> str:
    while (position := line.find("\t")) != -1:
        fill = " " * (8 - (position % 8))
        line = line.replace("\t", fill)
    return line


ascii_to_control_pictures = {
    0x00: "\u2400",  # NUL -> ␀
    0x01: "\u2401",  # SOH -> ␁
    0x02: "\u2402",  # STX -> ␂
    0x03: "\u2403",  # ETX -> ␃
    0x04: "\u2404",  # EOT -> ␄
    0x05: "\u2405",  # ENQ -> ␅
    0x06: "\u2406",  # ACK -> ␆
    0x07: "\u2407",  # BEL -> ␇
    0x08: "\u2408",  # BS  -> ␈
    0x09: "\u2409",  # HT  -> ␉
    0x0A: "\u240a",  # LF  -> ␊
    0x0B: "\u240b",  # VT  -> ␋
    0x0C: "\u240c",  # FF  -> ␌
    0x0D: "\u240d",  # CR  -> ␍
    0x0E: "\u240e",  # SO  -> ␎
    0x0F: "\u240f",  # SI  -> ␏
    0x10: "\u2410",  # DLE -> ␐
    0x11: "\u2411",  # DC1 -> ␑
    0x12: "\u2412",  # DC2 -> ␒
    0x13: "\u2413",  # DC3 -> ␓
    0x14: "\u2414",  # DC4 -> ␔
    0x15: "\u2415",  # NAK -> ␕
    0x16: "\u2416",  # SYN -> ␖
    0x17: "\u2417",  # ETB -> ␗
    0x18: "\u2418",  # CAN -> ␘
    0x19: "\u2419",  # EM  -> ␙
    0x1A: "\u241a",  # SUB -> ␚
    0x1B: "\u241b",  # ESC -> ␛
    0x1C: "\u241c",  # FS  -> ␜
    0x1D: "\u241d",  # GS  -> ␝
    0x1E: "\u241e",  # RS  -> ␞
    0x1F: "\u241f",  # US  -> ␟
    0x20: "\u2420",  # SPACE -> ␠
    0x7F: "\u2421",  # DEL -> ␡
}


def to_control_picture(char: str) -> str:
    return ascii_to_control_pictures.get(ord(char), char)


def line_to_control_pictures(line: str) -> str:
    return "".join(to_control_picture(char) for char in line)


def match(pattern: str, line: str) -> bool | re.Match[str] | None:
    if pattern == EMPTY_LINE_PATTERN:
        if not line:
            return True

    line = tab_replace(line)
    pattern = re.escape(pattern)
    pattern = pattern.replace(r"\.\.\.", ".*?")
    re_pattern = re.compile("^" + pattern + "$")
    return re_pattern.match(line)


class Line:
    status: Status = Status.UNEXPECTED
    status_cause: str = ""

    def __init__(self, data: str):
        self.data = data

    def matches(self, expectation: str) -> bool:
        return bool(match(expectation, self.data))

    def mark(self, status: Status, cause: str) -> None:
        if status.value <= self.status.value:
            # Stay in the current status
            return
        self.status = status
        self.status_cause = cause


class Audit:
    content: list[Line]
    unmatched_expectations: list[tuple[str, str]]
    matched_refused: set[tuple[str, str]]
    # Track positions for JSON output:
    # (pattern_name, expected_line) -> line_number (1-based)
    _unmatched_positions: dict[tuple[str, str], int]
    # Track positions for matched refused:
    # (pattern_name, refused_line) -> line_number (1-based)
    _matched_refused_positions: dict[tuple[str, str], int]

    def __init__(self, content: str):
        self.unmatched_expectations = []
        self.matched_refused = set()
        self._unmatched_positions = {}
        self._matched_refused_positions = {}

        self.content = []
        for line in content.splitlines():
            self.content.append(Line(line))

    def cursor(self) -> Iterator[Line]:
        return iter(self.content)

    def in_order(self, name: str, expected_lines: list[str]) -> None:
        """Expect all lines exist and come in order, but they
        may be interleaved with other lines."""
        cursor = self.cursor()
        cursor_index = 0  # Track position for JSON output (1-based)
        last_match_position = 0  # Position of last successful match
        have_some_match = False
        for expected_line in expected_lines:
            start_position = (
                last_match_position + 1
            )  # Where we started searching
            for line in cursor:
                cursor_index += 1
                if line.matches(expected_line):
                    line.mark(Status.EXPECTED, name)
                    have_some_match = True
                    last_match_position = cursor_index
                    break
            else:
                # No match found - record position where matching
                # stopped. The failure position is the line after
                # the last successful match.
                failure_position = start_position
                self.unmatched_expectations.append((name, expected_line))
                self._unmatched_positions[(name, expected_line)] = (
                    failure_position
                )
                if not have_some_match:
                    # Reset the scan, if we didn't have any previous
                    # match - maybe a later line will produce a partial match.
                    # But do not reset if we already have something matching,
                    # because that would defeat the "in order" assumption.
                    cursor = self.cursor()
                    cursor_index = 0
                    last_match_position = 0

    def optional(self, name: str, tolerated_lines: list[str]) -> None:
        """Those lines may exist and then they may appear anywhere
        a number of times, or they may not exist.
        """
        for tolerated_line in tolerated_lines:
            for line in self.cursor():
                if line.matches(tolerated_line):
                    line.mark(Status.OPTIONAL, name)

    def refused(self, name: str, refused_lines: list[str]) -> None:
        for refused_line in refused_lines:
            for line_index, line in enumerate(self.cursor()):
                if line.matches(refused_line):
                    line.mark(Status.REFUSED, name)
                    self.matched_refused.add((name, refused_line))
                    # Store position (1-based line number)
                    self._matched_refused_positions[(name, refused_line)] = (
                        line_index + 1
                    )

    def continuous(self, name: str, continuous_lines: list[str]) -> None:
        continuous_cursor = enumerate(continuous_lines)
        continuous_index, continuous_line = next(continuous_cursor)
        for line in self.cursor():
            if continuous_index and not line.data:
                # Continuity still allows empty lines (after the first line) in
                # between as we filter them out from the pattern to make those
                # more readable.
                line.mark(Status.OPTIONAL, name)
                continue
            if line.matches(continuous_line):
                line.mark(Status.EXPECTED, name)
                try:
                    continuous_index, continuous_line = next(continuous_cursor)
                except StopIteration:
                    # We exhausted the pattern and are happy.
                    break
            elif continuous_index:
                # This is not the first focus line any more, it's not valid to
                # not match
                line.mark(Status.REFUSED, name)
                self.unmatched_expectations.append((name, continuous_line))
                self.unmatched_expectations.extend(
                    [(name, line) for i, line in continuous_cursor]
                )
                break
        else:
            self.unmatched_expectations.append((name, continuous_line))
            self.unmatched_expectations.extend(
                [(name, line) for i, line in continuous_cursor]
            )

    def _build_summary(self) -> str:
        """Build informative summary line with pattern names and counts."""
        # Collect all pattern names
        all_names: set[str] = set()
        for line in self.content:
            if line.status_cause:
                all_names.add(line.status_cause)
        for name, _ in self.unmatched_expectations:
            all_names.add(name)
        for name, _ in self.matched_refused:
            all_names.add(name)

        # Collect pattern names by failure type
        refused_names: set[str] = set()
        unmatched_names: set[str] = set()

        for line in self.content:
            if line.status == Status.REFUSED and line.status_cause:
                refused_names.add(line.status_cause)
        for name, _ in self.unmatched_expectations:
            unmatched_names.add(name)
        for name, _ in self.matched_refused:
            refused_names.add(name)

        # Count by status
        counts = dict.fromkeys(Status, 0)
        for line in self.content:
            counts[line.status] += 1

        # Build failure details
        failures: list[str] = []
        is_single_pattern = len(all_names) == 1
        single_pattern_name = (
            next(iter(all_names)) if is_single_pattern else None
        )

        if counts[Status.REFUSED] > 0:
            if is_single_pattern:
                failures.append(f"{counts[Status.REFUSED]} refused")
            else:
                for name in sorted(refused_names):
                    failures.append(
                        f"[{name}] - {counts[Status.REFUSED]} refused"
                    )
        if self.unmatched_expectations:
            if is_single_pattern:
                failures.append(f"{len(self.unmatched_expectations)} unmatched")
            else:
                for name in sorted(unmatched_names):
                    failures.append(
                        f"[{name}] - {len(self.unmatched_expectations)} unmatched"
                    )
        if counts[Status.UNEXPECTED] > 0:
            failures.append(f"{counts[Status.UNEXPECTED]} unexpected")

        if not failures:
            return "String did not meet the expectations."

        if all_names:
            sorted_names = sorted(all_names)
            return f"Pattern [{', '.join(sorted_names)}] mismatch: {'; '.join(failures)}."
        return f"Pattern mismatch: {'; '.join(failures)}."

    def report(self) -> Iterator[str]:
        yield self._build_summary()
        yield ""
        yield " | ".join(
            [
                Status.EXPECTED.symbol + "=EXPECTED",
                Status.OPTIONAL.symbol + "=OPTIONAL",
                Status.UNEXPECTED.symbol + "=UNEXPECTED",
                Status.REFUSED.symbol + "=REFUSED/UNMATCHED",
            ]
        )
        yield ""
        yield "Here is the string that was tested: "
        yield ""
        for line in self.content:
            yield format_line_report(
                line.status,
                line.status.symbol,
                line.status_cause,
                tab_replace(line.data),
            )
        if self.unmatched_expectations:
            yield ""
            yield "These are the unmatched expected lines: "
            yield ""
            for name, line_str in self.unmatched_expectations:
                yield format_line_report(
                    Status.REFUSED, Status.REFUSED.symbol, name, line_str
                )
        if self.matched_refused:
            yield ""
            yield "These are the matched refused lines: "
            yield ""
            for name, line_str in self.matched_refused:
                yield format_line_report(
                    Status.REFUSED, Status.REFUSED.symbol, name, line_str
                )
        # Whitespace warning section
        ws_issues = self._collect_whitespace_issues()
        if ws_issues:
            yield ""
            yield "⚠️  Whitespace issues detected:"
            yield ""
            for line_no, description in ws_issues:
                yield f"   Line {line_no}: {description}"

    def _collect_whitespace_issues(self) -> list[tuple[int, str]]:
        """Collect whitespace issues from unexpected content lines.

        Returns list of (line_number, description) tuples.
        """
        issues: list[tuple[int, str]] = []

        # Check unexpected content lines
        for i, line in enumerate(self.content):
            if line.status == Status.UNEXPECTED:
                ws_desc = describe_whitespace(line.data)
                if ws_desc:
                    issues.append((i + 1, ws_desc))  # 1-based line number

        # Check unmatched expected lines
        for name, expected_line in self.unmatched_expectations:
            ws_desc = describe_whitespace(expected_line)
            if ws_desc:
                # Find position if available
                pos = self._unmatched_positions.get((name, expected_line), 0)
                issues.append((pos, f"expected '{expected_line}' [{ws_desc}]"))

        return issues

    def is_ok(self) -> bool:
        if self.unmatched_expectations:
            return False
        for line in self.content:
            if line.status not in [Status.EXPECTED, Status.OPTIONAL]:
                return False
        return True

    def _build_context(self, position: int) -> tuple[int, list[str]]:
        """Build context around a position.

        Returns (context_start, context_lines) where:
        - context_start: 1-based line number of first context line
        - context_lines: list of line contents (3 before + actual + 3 after)

        Position is 1-based line number where the problem occurred.
        """
        # Convert to 0-based index
        idx = position - 1
        # 3 lines before, the line itself, 3 lines after
        start = max(0, idx - 3)
        end = min(len(self.content), idx + 4)  # +4 because slice is exclusive
        context_start = start + 1  # Convert back to 1-based
        context_lines = [self.content[i].data for i in range(start, end)]
        return context_start, context_lines

    def to_json(self) -> dict[str, Any]:
        """Return structured JSON representation for agents/CI."""
        # Count by status
        counts = dict.fromkeys(Status, 0)
        for line in self.content:
            counts[line.status] += 1

        # Count primary vs cascading failures
        total_unmatched = len(self.unmatched_expectations)
        primary_failures = 1 if total_unmatched > 0 else 0
        cascading_failures = max(0, total_unmatched - 1)

        return {
            "status": "passed" if self.is_ok() else "failed",
            "summary": {
                "total_lines": len(self.content),
                "expected": counts[Status.EXPECTED],
                "optional": counts[Status.OPTIONAL],
                "unexpected": counts[Status.UNEXPECTED],
                "refused": counts[Status.REFUSED],
                "unmatched": total_unmatched,
                "primary_failures": primary_failures,
                "cascading_failures": cascading_failures,
            },
            "lines": [
                {
                    "number": i + 1,
                    "content": line.data,
                    "status": line.status.name.lower(),
                    "pattern": line.status_cause or None,
                }
                for i, line in enumerate(self.content)
            ],
            "unmatched_patterns": [
                self._build_unmatched_entry(name, line_str, is_primary=(i == 0))
                for i, (name, line_str) in enumerate(
                    self.unmatched_expectations
                )
            ],
            "matched_refused": [
                self._build_matched_refused_entry(name, line_str)
                for name, line_str in self.matched_refused
            ],
        }

    def _build_unmatched_entry(
        self, name: str, expected_line: str, *, is_primary: bool = True
    ) -> dict[str, Any]:
        """Build JSON entry for an unmatched pattern with context."""
        entry: dict[str, Any] = {
            "pattern": name,
            "expected_line": expected_line,
            "failure_type": "primary" if is_primary else "cascading",
        }
        position = self._unmatched_positions.get((name, expected_line))
        if position is not None:
            entry["actual_at_line"] = position
            # Get actual line content at that position (if exists)
            if 1 <= position <= len(self.content):
                entry["actual_line"] = self.content[position - 1].data
            # Build context
            context_start, context_lines = self._build_context(position)
            entry["context_start"] = context_start
            entry["context_lines"] = context_lines
        return entry

    def _build_matched_refused_entry(
        self, name: str, refused_line: str
    ) -> dict[str, Any]:
        """Build JSON entry for a matched refused pattern with context."""
        entry: dict[str, Any] = {
            "pattern": name,
            "refused_line": refused_line,
        }
        position = self._matched_refused_positions.get((name, refused_line))
        if position is not None:
            entry["actual_at_line"] = position
            if 1 <= position <= len(self.content):
                entry["actual_line"] = self.content[position - 1].data
            context_start, context_lines = self._build_context(position)
            entry["context_start"] = context_start
            entry["context_lines"] = context_lines
        return entry


def format_line_report(
    status: Status,
    symbol: str,
    cause: str,
    line: str,
) -> str:
    if status not in [Status.EXPECTED, Status.OPTIONAL]:
        # Check for whitespace issues in unexpected/refused lines
        ws_issue = describe_whitespace(line)
        if ws_issue:
            # Apply yellow background and annotation
            highlighted = (
                YELLOW_BG
                + line_to_control_pictures(line)
                + RESET
                + f"  [{ws_issue}]"
            )
            return symbol + " " + cause.ljust(15)[:15] + " | " + highlighted
        line = line_to_control_pictures(line)
    return symbol + " " + cause.ljust(15)[:15] + " | " + line


def pattern_lines(lines: str) -> list[str]:
    # Remove leading whitespace, ignore empty lines.
    return list(filter(None, lines.splitlines()))


class Pattern:
    name: str
    library: PatternsLib
    ops: list[tuple[str, str, Any]]
    inherited: set[str]

    def __init__(self, library: PatternsLib, name: str):
        self.name = name
        self.library = library
        self.ops = []
        self.inherited = set()

    # Modifiers (Verbs)

    def merge(self, *base_patterns: str) -> None:
        """Merge rules from base_patterns (recursively) into this pattern."""
        self.inherited.update(base_patterns)

    def normalize(self, mode: str) -> None:
        pass

    # Matches (Adjectives)

    def continuous(self, lines: str) -> None:
        """These lines must appear once and they must be continuous."""
        self.ops.append(("continuous", self.name, pattern_lines(lines)))

    def in_order(self, lines: str) -> None:
        """These lines must appear once and they must be in order."""
        self.ops.append(("in_order", self.name, pattern_lines(lines)))

    def optional(self, lines: str) -> None:
        """These lines are optional."""
        self.ops.append(("optional", self.name, pattern_lines(lines)))

    def refused(self, lines: str) -> None:
        """If those lines appear they are refused."""
        self.ops.append(("refused", self.name, pattern_lines(lines)))

    # Internal API

    def flat_ops(self) -> Iterator[tuple[str, str, Any]]:
        for inherited_pattern in self.inherited:
            yield from getattr(self.library, inherited_pattern).flat_ops()
        yield from self.ops

    def _audit(self, content: str) -> Audit:
        audit = Audit(content)
        for op, *args in self.flat_ops():
            getattr(audit, op)(*args)
        return audit

    def generate_example(self) -> str:
        """Generate example text that matches this pattern.

        Simple placeholder strategy:
        - ... → [...]
        - <empty-line> → (empty string)
        - refused patterns are ignored
        """
        lines = []

        for op, _name, pattern_lines in self.flat_ops():
            if op == "refused":
                # Skip refused patterns (Option A: ignore)
                continue

            for pattern_line in pattern_lines:
                replaced = self._replace_wildcards(pattern_line)
                lines.append(replaced)

        return "\n".join(lines)

    def _replace_wildcards(self, line: str) -> str:
        """Replace wildcards with simple placeholders."""
        # <empty-line> → empty string
        if line == EMPTY_LINE_PATTERN:
            return ""
        # ... → [...]
        line = line.replace("...", "[...]")
        return line

    def __eq__(self, other: object) -> bool:
        assert isinstance(other, str)
        audit = self._audit(other)
        return audit.is_ok()


class PatternsLib:
    def __getattr__(self, name: str) -> Pattern:
        res = self.__dict__[name] = Pattern(self, name)
        return res
