from pathlib import Path

from pytest_patterns.plugin import PatternsLib

GENERIC_HEADER = [
    "",  # Summary line (dynamic, tested separately)
    "🟢=EXPECTED | ⚪️=OPTIONAL | 🟡=UNEXPECTED | 🔴=REFUSED/UNMATCHED",
    "",
    "Here is the string that was tested: ",
    "",
]


def extract_summary(report_lines):
    """Extract the first line (summary) from a report."""
    return report_lines[0] if report_lines else ""


def strip_summary(report_lines):
    """Remove the dynamic summary line for comparison."""
    return report_lines[1:] if report_lines else []


def strip_line_numbers(lines):
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


def test_ical_ordering_produces_reasonable_reports(
    patterns,
):
    with (Path(__file__).parent / "fixtures" / "ical-ordering.ical").open(
        "r"
    ) as f:
        test_data = f.read()

    # We used this pattern and got a weird match originally. Here's what
    # we expect it to look like:
    p = patterns.schedule
    p.in_order(
        """
BEGIN:VCALENDAR\r
VERSION:2.0\r
PRODID:-//fc.support//fcio//\r

BEGIN:VEVENT
SUMMARY:cedric (1\\, platform)
DTSTART;VALUE=DATE:20110201
DTEND;VALUE=DATE:20110201
DTSTAMP;VALUE=DATE-TIME:19700101T000140Z
UID:46f2574f64d22dc70db2379b08d83c0f51305c0729cb0d0e8852208b0deb4d87
END:VEVENT

BEGIN:VEVENT
SUMMARY:cedric (1\\, platform)
DTSTART;VALUE=DATE:20110202
DTEND;VALUE=DATE:20110202
DTSTAMP;VALUE=DATE-TIME:19700101T000140Z
UID:0b3f15fedfdf1c627afd2efd990b8c52e7f8822eebf62767e38b33cd5763d5c9
END:VEVENT

BEGIN:VEVENT
SUMMARY:cedric (1\\, platform)
DTSTART;VALUE=DATE:20110203
DTEND;VALUE=DATE:20110203
DTSTAMP;VALUE=DATE-TIME:19700101T000140Z
UID:a1d00464af0a25c9292aa72d0bf5236b5749d5e42c13e484080d2abbfb6ad89e
END:VEVENT

BEGIN:VEVENT
SUMMARY:cedric (1\\, platform)
DTSTART;VALUE=DATE:20110204
DTEND;VALUE=DATE:20110204
DTSTAMP;VALUE=DATE-TIME:19700101T000140Z
UID:4d6e48685c893ddf8856c8439f4d6bde05fbe603118fa68ebd7d3f37b4e3e6ed
END:VEVENT

BEGIN:VEVENT
SUMMARY:alice (1\\, platform)
DTSTART;VALUE=DATE:20110205
DTEND;VALUE=DATE:20110205
DTSTAMP;VALUE=DATE-TIME:19700101T000140Z
UID:31638940439cb48412420108cbb265a34baf2714075df401723bf82da0586743
END:VEVENT

BEGIN:VEVENT
SUMMARY:alice (1\\, platform)
DTSTART;VALUE=DATE:20110206
DTEND;VALUE=DATE:20110206
DTSTAMP;VALUE=DATE-TIME:19700101T000140Z
UID:8288d3266bf9cef59ddeafd8ec03d58bc0314dfe9e825617c9de90f856361eff
END:VEVENT

BEGIN:VEVENT
SUMMARY:alice (1\\, appops)
DTSTART;VALUE=DATE:20110201
DTEND;VALUE=DATE:20110201
DTSTAMP;VALUE=DATE-TIME:19700101T000140Z
UID:36a6983685c626a8255f480ec59930ea6f38a257ba79460982149461c733506a
END:VEVENT

BEGIN:VEVENT
SUMMARY:bob (2\\, appops)
DTSTART;VALUE=DATE:20110201
DTEND;VALUE=DATE:20110201
DTSTAMP;VALUE=DATE-TIME:19700101T000140Z
UID:42d5f543bdbb6f589bd19a893fd209fe89f4558c7be5ebcb93bcd12ba9ae9161
END:VEVENT

BEGIN:VEVENT
SUMMARY:alice (1\\, appops)
DTSTART;VALUE=DATE:20110202
DTEND;VALUE=DATE:20110202
DTSTAMP;VALUE=DATE-TIME:19700101T000140Z
UID:6db22f58ee442b51955546b6b617c2e39c07acc0a77b1dcc4230a04d63dc08a4
END:VEVENT

BEGIN:VEVENT
SUMMARY:bob (2\\, appops)
DTSTART;VALUE=DATE:20110202
DTEND;VALUE=DATE:20110202
DTSTAMP;VALUE=DATE-TIME:19700101T000140Z
UID:92100821b84973eccd2fb036c068bd405698af95e16f4420341940e5cc5ac148
END:VEVENT

BEGIN:VEVENT
SUMMARY:alice (1\\, appops)
DTSTART;VALUE=DATE:20110203
DTEND;VALUE=DATE:20110203
DTSTAMP;VALUE=DATE-TIME:19700101T000140Z
UID:bd1b1d019cfdff07456a7be437ecc6c7027f8c4ec6904e65c6f297a52f3eee14
END:VEVENT

BEGIN:VEVENT
SUMMARY:bob (2\\, appops)
DTSTART;VALUE=DATE:20110203
DTEND;VALUE=DATE:20110203
DTSTAMP;VALUE=DATE-TIME:19700101T000140Z
UID:becfafc6c131961b1d8913f3109aef3af1b6142bdbbc4e4642503fcd1cce05a6
END:VEVENT

BEGIN:VEVENT
SUMMARY:alice (1\\, appops)
DTSTART;VALUE=DATE:20110204
DTEND;VALUE=DATE:20110204
DTSTAMP;VALUE=DATE-TIME:19700101T000140Z
UID:834e1ddc937baae355d08f8960967466baab83f172d5f967a49083550cbd9e06
END:VEVENT

BEGIN:VEVENT
SUMMARY:bob (2\\, appops)
DTSTART;VALUE=DATE:20110204
DTEND;VALUE=DATE:20110204
DTSTAMP;VALUE=DATE-TIME:19700101T000140Z
UID:08e07e2b92b3fbb3264abd48e1aa1983962626902630beb6a5b4d5fece22a7da
END:VEVENT

BEGIN:VEVENT
SUMMARY:bob (1\\, appops)
DTSTART;VALUE=DATE:20110205
DTEND;VALUE=DATE:20110205
DTSTAMP;VALUE=DATE-TIME:19700101T000140Z
UID:16f138f3f88c54fe5a6e248de42f6a8e3a9b0c3f941c9f9c760b9aa639c1d457
END:VEVENT

BEGIN:VEVENT
SUMMARY:bob (1\\, appops)
DTSTART;VALUE=DATE:20110206
DTEND;VALUE=DATE:20110206
DTSTAMP;VALUE=DATE-TIME:19700101T000140Z
UID:0afbce38bf534b30031618c9a7c0f884b8ae69ccfe99d32753790edfab033405
END:VEVENT

END:VCALENDAR\r
"""
    )

    audit = p._audit(test_data)
    report = list(audit.report())
    assert (
        extract_summary(report)
        == "Pattern [schedule]: 71 unexpected; 71 unmatched."
    )
    assert strip_line_numbers(strip_summary(report)) == [
        *GENERIC_HEADER,
        "🟢 schedule        | BEGIN:VCALENDAR",
        "🟢 schedule        | VERSION:2.0",
        "🟢 schedule        | PRODID:-//fc.support//fcio//",
        "🟢 schedule        | BEGIN:VEVENT",
        "🟡                 | SUMMARY:alice (1\\, appops)",
        "🟡                 | DTSTART;VALUE=DATE:20110201",
        "🟡                 | DTEND;VALUE=DATE:20110201",
        "🟡                 | DTSTAMP;VALUE=DATE-TIME:19700101T000140Z",
        "🟡                 | "
        "UID:36a6983685c626a8255f480ec59930ea6f38a257ba79460982149461c733506a",
        "🟡                 | END:VEVENT",
        "🟡                 | BEGIN:VEVENT",
        "🟡                 | SUMMARY:bob (2\\, appops)",
        "🟡                 | DTSTART;VALUE=DATE:20110201",
        "🟡                 | DTEND;VALUE=DATE:20110201",
        "🟡                 | DTSTAMP;VALUE=DATE-TIME:19700101T000140Z",
        "🟡                 | "
        "UID:42d5f543bdbb6f589bd19a893fd209fe89f4558c7be5ebcb93bcd12ba9ae9161",
        "🟡                 | END:VEVENT",
        "🟡                 | BEGIN:VEVENT",
        "🟡                 | SUMMARY:alice (1\\, appops)",
        "🟡                 | DTSTART;VALUE=DATE:20110202",
        "🟡                 | DTEND;VALUE=DATE:20110202",
        "🟡                 | DTSTAMP;VALUE=DATE-TIME:19700101T000140Z",
        "🟡                 | "
        "UID:6db22f58ee442b51955546b6b617c2e39c07acc0a77b1dcc4230a04d63dc08a4",
        "🟡                 | END:VEVENT",
        "🟡                 | BEGIN:VEVENT",
        "🟡                 | SUMMARY:bob (2\\, appops)",
        "🟡                 | DTSTART;VALUE=DATE:20110202",
        "🟡                 | DTEND;VALUE=DATE:20110202",
        "🟡                 | DTSTAMP;VALUE=DATE-TIME:19700101T000140Z",
        "🟡                 | "
        "UID:92100821b84973eccd2fb036c068bd405698af95e16f4420341940e5cc5ac148",
        "🟡                 | END:VEVENT",
        "🟡                 | BEGIN:VEVENT",
        "🟡                 | SUMMARY:alice (1\\, appops)",
        "🟡                 | DTSTART;VALUE=DATE:20110203",
        "🟡                 | DTEND;VALUE=DATE:20110203",
        "🟡                 | DTSTAMP;VALUE=DATE-TIME:19700101T000140Z",
        "🟡                 | "
        "UID:bd1b1d019cfdff07456a7be437ecc6c7027f8c4ec6904e65c6f297a52f3eee14",
        "🟡                 | END:VEVENT",
        "🟡                 | BEGIN:VEVENT",
        "🟡                 | SUMMARY:bob (2\\, appops)",
        "🟡                 | DTSTART;VALUE=DATE:20110203",
        "🟡                 | DTEND;VALUE=DATE:20110203",
        "🟡                 | DTSTAMP;VALUE=DATE-TIME:19700101T000140Z",
        "🟡                 | "
        "UID:becfafc6c131961b1d8913f3109aef3af1b6142bdbbc4e4642503fcd1cce05a6",
        "🟡                 | END:VEVENT",
        "🟡                 | BEGIN:VEVENT",
        "🟡                 | SUMMARY:alice (1\\, appops)",
        "🟡                 | DTSTART;VALUE=DATE:20110204",
        "🟡                 | DTEND;VALUE=DATE:20110204",
        "🟡                 | DTSTAMP;VALUE=DATE-TIME:19700101T000140Z",
        "🟡                 | "
        "UID:834e1ddc937baae355d08f8960967466baab83f172d5f967a49083550cbd9e06",
        "🟡                 | END:VEVENT",
        "🟡                 | BEGIN:VEVENT",
        "🟡                 | SUMMARY:bob (2\\, appops)",
        "🟡                 | DTSTART;VALUE=DATE:20110204",
        "🟡                 | DTEND;VALUE=DATE:20110204",
        "🟡                 | DTSTAMP;VALUE=DATE-TIME:19700101T000140Z",
        "🟡                 | "
        "UID:08e07e2b92b3fbb3264abd48e1aa1983962626902630beb6a5b4d5fece22a7da",
        "🟡                 | END:VEVENT",
        "🟡                 | BEGIN:VEVENT",
        "🟡                 | SUMMARY:bob (1\\, appops)",
        "🟡                 | DTSTART;VALUE=DATE:20110205",
        "🟡                 | DTEND;VALUE=DATE:20110205",
        "🟡                 | DTSTAMP;VALUE=DATE-TIME:19700101T000140Z",
        "🟡                 | "
        "UID:16f138f3f88c54fe5a6e248de42f6a8e3a9b0c3f941c9f9c760b9aa639c1d457",
        "🟡                 | END:VEVENT",
        "🟡                 | BEGIN:VEVENT",
        "🟡                 | SUMMARY:bob (1\\, appops)",
        "🟡                 | DTSTART;VALUE=DATE:20110206",
        "🟡                 | DTEND;VALUE=DATE:20110206",
        "🟡                 | DTSTAMP;VALUE=DATE-TIME:19700101T000140Z",
        "🟡                 | "
        "UID:0afbce38bf534b30031618c9a7c0f884b8ae69ccfe99d32753790edfab033405",
        "🟡                 | END:VEVENT",
        "🟡                 | BEGIN:VEVENT",
        "🟢 schedule        | SUMMARY:cedric (1\\, platform)",
        "🟢 schedule        | DTSTART;VALUE=DATE:20110201",
        "🟢 schedule        | DTEND;VALUE=DATE:20110201",
        "🟢 schedule        | DTSTAMP;VALUE=DATE-TIME:19700101T000140Z",
        "🟢 schedule        | "
        "UID:46f2574f64d22dc70db2379b08d83c0f51305c0729cb0d0e8852208b0deb4d87",
        "🟢 schedule        | END:VEVENT",
        "🟢 schedule        | BEGIN:VEVENT",
        "🟢 schedule        | SUMMARY:cedric (1\\, platform)",
        "🟢 schedule        | DTSTART;VALUE=DATE:20110202",
        "🟢 schedule        | DTEND;VALUE=DATE:20110202",
        "🟢 schedule        | DTSTAMP;VALUE=DATE-TIME:19700101T000140Z",
        "🟢 schedule        | "
        "UID:0b3f15fedfdf1c627afd2efd990b8c52e7f8822eebf62767e38b33cd5763d5c9",
        "🟢 schedule        | END:VEVENT",
        "🟢 schedule        | BEGIN:VEVENT",
        "🟢 schedule        | SUMMARY:cedric (1\\, platform)",
        "🟢 schedule        | DTSTART;VALUE=DATE:20110203",
        "🟢 schedule        | DTEND;VALUE=DATE:20110203",
        "🟢 schedule        | DTSTAMP;VALUE=DATE-TIME:19700101T000140Z",
        "🟢 schedule        | "
        "UID:a1d00464af0a25c9292aa72d0bf5236b5749d5e42c13e484080d2abbfb6ad89e",
        "🟢 schedule        | END:VEVENT",
        "🟢 schedule        | BEGIN:VEVENT",
        "🟢 schedule        | SUMMARY:cedric (1\\, platform)",
        "🟢 schedule        | DTSTART;VALUE=DATE:20110204",
        "🟢 schedule        | DTEND;VALUE=DATE:20110204",
        "🟢 schedule        | DTSTAMP;VALUE=DATE-TIME:19700101T000140Z",
        "🟢 schedule        | "
        "UID:4d6e48685c893ddf8856c8439f4d6bde05fbe603118fa68ebd7d3f37b4e3e6ed",
        "🟢 schedule        | END:VEVENT",
        "🟢 schedule        | BEGIN:VEVENT",
        "🟢 schedule        | SUMMARY:alice (1\\, platform)",
        "🟢 schedule        | DTSTART;VALUE=DATE:20110205",
        "🟢 schedule        | DTEND;VALUE=DATE:20110205",
        "🟢 schedule        | DTSTAMP;VALUE=DATE-TIME:19700101T000140Z",
        "🟢 schedule        | "
        "UID:31638940439cb48412420108cbb265a34baf2714075df401723bf82da0586743",
        "🟢 schedule        | END:VEVENT",
        "🟢 schedule        | BEGIN:VEVENT",
        "🟢 schedule        | SUMMARY:alice (1\\, platform)",
        "🟢 schedule        | DTSTART;VALUE=DATE:20110206",
        "🟢 schedule        | DTEND;VALUE=DATE:20110206",
        "🟢 schedule        | DTSTAMP;VALUE=DATE-TIME:19700101T000140Z",
        "🟢 schedule        | "
        "UID:8288d3266bf9cef59ddeafd8ec03d58bc0314dfe9e825617c9de90f856361eff",
        "🟢 schedule        | END:VEVENT",
        "🟡                 | END:VCALENDAR",
        "",
        "These are the unmatched expected lines: ",
        "",
        "🔴 schedule        | BEGIN:VEVENT",
        "🔴 schedule        | SUMMARY:alice (1\\, appops)",
        "🔴 schedule        | DTSTART;VALUE=DATE:20110201",
        "🔴 schedule        | DTEND;VALUE=DATE:20110201",
        "🔴 schedule        | DTSTAMP;VALUE=DATE-TIME:19700101T000140Z",
        "🔴 schedule        | "
        "UID:36a6983685c626a8255f480ec59930ea6f38a257ba79460982149461c733506a",
        "🔴 schedule        | END:VEVENT",
        "🔴 schedule        | BEGIN:VEVENT",
        "🔴 schedule        | SUMMARY:bob (2\\, appops)",
        "🔴 schedule        | DTSTART;VALUE=DATE:20110201",
        "🔴 schedule        | DTEND;VALUE=DATE:20110201",
        "🔴 schedule        | DTSTAMP;VALUE=DATE-TIME:19700101T000140Z",
        "🔴 schedule        | "
        "UID:42d5f543bdbb6f589bd19a893fd209fe89f4558c7be5ebcb93bcd12ba9ae9161",
        "🔴 schedule        | END:VEVENT",
        "🔴 schedule        | BEGIN:VEVENT",
        "🔴 schedule        | SUMMARY:alice (1\\, appops)",
        "🔴 schedule        | DTSTART;VALUE=DATE:20110202",
        "🔴 schedule        | DTEND;VALUE=DATE:20110202",
        "🔴 schedule        | DTSTAMP;VALUE=DATE-TIME:19700101T000140Z",
        "🔴 schedule        | "
        "UID:6db22f58ee442b51955546b6b617c2e39c07acc0a77b1dcc4230a04d63dc08a4",
        "🔴 schedule        | END:VEVENT",
        "🔴 schedule        | BEGIN:VEVENT",
        "🔴 schedule        | SUMMARY:bob (2\\, appops)",
        "🔴 schedule        | DTSTART;VALUE=DATE:20110202",
        "🔴 schedule        | DTEND;VALUE=DATE:20110202",
        "🔴 schedule        | DTSTAMP;VALUE=DATE-TIME:19700101T000140Z",
        "🔴 schedule        | "
        "UID:92100821b84973eccd2fb036c068bd405698af95e16f4420341940e5cc5ac148",
        "🔴 schedule        | END:VEVENT",
        "🔴 schedule        | BEGIN:VEVENT",
        "🔴 schedule        | SUMMARY:alice (1\\, appops)",
        "🔴 schedule        | DTSTART;VALUE=DATE:20110203",
        "🔴 schedule        | DTEND;VALUE=DATE:20110203",
        "🔴 schedule        | DTSTAMP;VALUE=DATE-TIME:19700101T000140Z",
        "🔴 schedule        | "
        "UID:bd1b1d019cfdff07456a7be437ecc6c7027f8c4ec6904e65c6f297a52f3eee14",
        "🔴 schedule        | END:VEVENT",
        "🔴 schedule        | BEGIN:VEVENT",
        "🔴 schedule        | SUMMARY:bob (2\\, appops)",
        "🔴 schedule        | DTSTART;VALUE=DATE:20110203",
        "🔴 schedule        | DTEND;VALUE=DATE:20110203",
        "🔴 schedule        | DTSTAMP;VALUE=DATE-TIME:19700101T000140Z",
        "🔴 schedule        | "
        "UID:becfafc6c131961b1d8913f3109aef3af1b6142bdbbc4e4642503fcd1cce05a6",
        "🔴 schedule        | END:VEVENT",
        "🔴 schedule        | BEGIN:VEVENT",
        "🔴 schedule        | SUMMARY:alice (1\\, appops)",
        "🔴 schedule        | DTSTART;VALUE=DATE:20110204",
        "🔴 schedule        | DTEND;VALUE=DATE:20110204",
        "🔴 schedule        | DTSTAMP;VALUE=DATE-TIME:19700101T000140Z",
        "🔴 schedule        | "
        "UID:834e1ddc937baae355d08f8960967466baab83f172d5f967a49083550cbd9e06",
        "🔴 schedule        | END:VEVENT",
        "🔴 schedule        | BEGIN:VEVENT",
        "🔴 schedule        | SUMMARY:bob (2\\, appops)",
        "🔴 schedule        | DTSTART;VALUE=DATE:20110204",
        "🔴 schedule        | DTEND;VALUE=DATE:20110204",
        "🔴 schedule        | DTSTAMP;VALUE=DATE-TIME:19700101T000140Z",
        "🔴 schedule        | "
        "UID:08e07e2b92b3fbb3264abd48e1aa1983962626902630beb6a5b4d5fece22a7da",
        "🔴 schedule        | END:VEVENT",
        "🔴 schedule        | BEGIN:VEVENT",
        "🔴 schedule        | SUMMARY:bob (1\\, appops)",
        "🔴 schedule        | DTSTART;VALUE=DATE:20110205",
        "🔴 schedule        | DTEND;VALUE=DATE:20110205",
        "🔴 schedule        | DTSTAMP;VALUE=DATE-TIME:19700101T000140Z",
        "🔴 schedule        | "
        "UID:16f138f3f88c54fe5a6e248de42f6a8e3a9b0c3f941c9f9c760b9aa639c1d457",
        "🔴 schedule        | END:VEVENT",
        "🔴 schedule        | BEGIN:VEVENT",
        "🔴 schedule        | SUMMARY:bob (1\\, appops)",
        "🔴 schedule        | DTSTART;VALUE=DATE:20110206",
        "🔴 schedule        | DTEND;VALUE=DATE:20110206",
        "🔴 schedule        | DTSTAMP;VALUE=DATE-TIME:19700101T000140Z",
        "🔴 schedule        | "
        "UID:0afbce38bf534b30031618c9a7c0f884b8ae69ccfe99d32753790edfab033405",
        "🔴 schedule        | END:VEVENT",
        "🔴 schedule        | END:VCALENDAR",
    ]
    assert not audit.is_ok()
