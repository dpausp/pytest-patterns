# Research Report: JSON, HTML, CLI Output Normalization for Testing

**Date**: March 2026  
**Project**: pytest-patterns  
**Focus**: Python tools for output normalization, comparison, and diffing

---

## Executive Summary

**Key Findings**:

1. **JSON Normalization**: The Python ecosystem offers mature solutions with `canonicaljson` (v2.0.0, Mar 2023) providing RFC 7159 compliant canonical serialization, while `deepdiff` (v8.6.1, Sep 2025) and `jsondiff` (v2.2.1, Aug 2024) offer comprehensive comparison capabilities.

2. **HTML Normalization**: A three-tier approach exists - `lxml` (v6.0.2, Sep 2025) for performance-critical parsing, `beautifulsoup4` (v4.14.3, Nov 2025) for lenient HTML handling, and `html5lib` (v1.1, Jun 2020) for spec-compliant parsing.

3. **CLI Output Normalization**: `strip-ansi` (v0.1.1, Jun 2020) and `ansi` (v0.3.7, Jan 2024) handle ANSI code removal, while `pytest-subprocess` (v1.5.3, Jan 2025) provides CLI output testing patterns.

4. **Snapshot Testing**: `syrupy` (v5.1.0, Jan 2026) is the leading pytest snapshot plugin with extensible serializers and matchers, while `pytest-snapshot` (v0.9.0, Apr 2022) offers simpler file-based snapshots.

5. **Implementation Recommendation**: Implement normalization as a modular `normalize()` method with format-specific handlers (json, html, cli), leveraging existing libraries as optional dependencies while maintaining zero required dependencies.

---

## 1. JSON Normalization

### 1.1 Canonical JSON Serialization

**canonicaljson (v2.0.0)** - Matrix.org Team
- **License**: Apache 2.0
- **Python**: 3.7+
- **Status**: Production/Stable (Last release: Mar 2023)

**Features**:
- RFC 7159 compliant canonical JSON encoding
- Sorted object keys for deterministic output
- No insignificant whitespace (minimal output)
- Minimal escaping (U+0000-U+0019, U+0022, U+005C only)
- UTF-8 encoding
- Custom type serialization via preserialization callbacks

**Usage Example**:
```python
import canonicaljson

# Basic encoding
data = {"z": 1, "a": 2, "m": 3}
encoded = canonicaljson.encode_canonical_json(data)
# Returns: b'{"a":2,"m":3,"z":1}'
```

### 1.2 JSON Comparison & Diffing

**deepdiff (v8.6.1)** - Sep Dehpour
- **License**: MIT
- **Python**: 3.9+ (supports 3.13, 3.14)
- **Status**: Production/Stable (Last release: Sep 2025)

**Features**:
- Deep difference and search of any Python object
- Delta storage and application (recreate objects from diffs)
- Multiple diff syntaxes (compact, symmetric, explicit)
- Ignore paths/patterns during comparison
- Special handling for sets, datetime, UUIDs, IP addresses

**jsondiff (v2.2.1)** - Zoomer Analytics
- **License**: MIT
- **Python**: 3.8+
- **Status**: Production/Stable (Last release: Aug 2024)

**Features**:
- Diff JSON and JSON-like structures
- LCS (Longest Common Subsequence) for lists
- Multiple diff syntaxes
- Command-line tool (`jdiff`)

### 1.3 JSON Normalization Strategies

**Key Ordering**: `canonicaljson` always sorts keys for deterministic output

**Float Precision**:
```python
# deepdiff approach
diff = DeepDiff(t1, t2, 
                significant_digits=4,  # Ignore differences beyond 4 decimals
                ignore_numeric_type_changes=True)
```

**Non-deterministic Values**:
```python
# deepdiff with regex ignoring
diff = DeepDiff(t1, t2,
                exclude_regex_paths=[r"root\['timestamp'\]", r"root\['id'\]"])
```

---

## 2. HTML Normalization

### 2.1 HTML Parsing Libraries

**lxml (v6.0.2)** - lxml Team
- **License**: BSD-3-Clause
- **Python**: 3.8+ (supports 3.14)
- **Status**: Production/Stable (Last release: Sep 2025)

**Features**:
- C-based libxml2/libxslt bindings (fast)
- ElementTree API
- XPath, RelaxNG, XML Schema, XSLT, C14N support
- HTML parser with error recovery

**beautifulsoup4 (v4.14.3)** - Leonard Richardson
- **License**: MIT
- **Python**: 3.7.0+
- **Status**: Production/Stable (Last release: Nov 2025)

**Features**:
- Lenient HTML parsing (handles broken HTML)
- Multiple parser backends (lxml, html5lib, html.parser)
- Navigation API (find, find_all, select)
- Encoding detection

**html5lib (v1.1)** - WHATWG compliance
- **License**: MIT
- **Python**: 2.7, 3.5+ (not actively maintained)
- **Status**: Production/Stable (Last release: Jun 2020)

### 2.2 HTML Normalization Strategies

**Canonical Representation**:
```python
from lxml import html, etree

def normalize_html(html_string):
    # Parse HTML
    doc = html.fromstring(html_string)
    
    # Normalize attributes (sort, quote style)
    for elem in doc.iter():
        if elem.attrib:
            sorted_attrs = sorted(elem.attrib.items())
            elem.attrib.clear()
            elem.attrib.update(sorted_attrs)
    
    # Serialize with consistent formatting
    normalized = etree.tostring(doc,
                                encoding='unicode',
                                pretty_print=True,
                                method='html')
    return normalized
```

**Boilerplate Removal**:
```python
def remove_boilerplate(html_string, keep_tags=None):
    if keep_tags is None:
        keep_tags = {'html', 'body', 'head', 'title', 'meta', 'link'}
    
    soup = BeautifulSoup(html_string, 'lxml')
    
    # Remove script, style, comments
    for tag in soup.find_all(['script', 'style']):
        tag.decompose()
    
    return str(soup)
```

---

## 3. CLI Output Normalization

### 3.1 ANSI Code Handling

**strip-ansi (v0.1.1)** - Ewen Le Bihan
- **License**: MIT
- **Python**: 3.6+
- **Status**: Stable (Last release: Jun 2020)

**Usage**:
```python
from strip_ansi import strip_ansi

output = "\033[38mLorem ipsum\033[0m"
clean = strip_ansi(output)
# Returns: "Lorem ipsum"
```

**Regex-based Stripping** (lightweight alternative):
```python
import re

ANSI_ESCAPE = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

def strip_ansi(text):
    """Strip ANSI escape sequences from text."""
    return ANSI_ESCAPE.sub('', text)
```

### 3.2 Timestamp/Date Normalization

```python
import re

def normalize_timestamps(output, replacement="<TIMESTAMP>"):
    """Replace various timestamp formats with placeholder."""
    
    # ISO 8601
    output = re.sub(
        r'\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?',
        replacement,
        output
    )
    
    return output
```

### 3.3 Non-deterministic Output Handling

**Comprehensive CLI Normalizer**:
```python
import re

class CLINormalizer:
    """Normalize CLI output for testing."""
    
    def __init__(self):
        self.patterns = {
            'timestamp': (
                r'\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?',
                '<TIMESTAMP>'
            ),
            'pid': (r'\bPID:\s*\d+\b', 'PID: <PID>'),
            'port': (r':(\d{4,5})\b', ':<PORT>'),
            'uuid': (
                r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}',
                '<UUID>'
            ),
            'ansi': (r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', ''),
        }
    
    def normalize(self, output, enabled=None):
        """Apply all normalization patterns."""
        if enabled is None:
            enabled = self.patterns.keys()
        
        for name in enabled:
            if name in self.patterns:
                pattern, replacement = self.patterns[name]
                output = re.sub(pattern, replacement, output, flags=re.IGNORECASE)
        
        return output
```

---

## 4. Python Testing Tools & Libraries

### 4.1 Snapshot Testing

**syrupy (v5.1.0)** - Noah Ulster
- **License**: MIT
- **Python**: 3.10+
- **Pytest**: 8+
- **Status**: Production/Stable (Last release: Jan 2026)

**Key Features**:
- Zero-dependency pytest plugin
- Extensible serializers (Amber, JSON, PNG, SVG)
- Property matchers for dynamic values
- Diff modes for large snapshots

**Usage Example**:
```python
def test_api_response(snapshot):
    response = api_call()
    assert response == snapshot

# With matchers for dynamic data
from syrupy.matchers import path_type

def test_with_matchers(snapshot):
    data = {
        "id": 123,
        "created": datetime.now(),
        "name": "test"
    }
    assert data == snapshot(matcher=path_type({
        "id": (int,),
        "created": (datetime,)
    }))
```

**pytest-snapshot (v0.9.0)** - Joseph Roitman
- **License**: MIT
- **Python**: 3.5+
- **Status**: Beta (Last release: Apr 2022)

### 4.2 Tool Comparison Matrix

| Tool | Version | License | Python | Type | Key Strength |
|------|---------|---------|--------|------|--------------|
| deepdiff | 8.6.1 | MIT | 3.9+ | Object diff | Deep structure comparison |
| jsondiff | 2.2.1 | MIT | 3.8+ | JSON diff | LCS-based list diff |
| canonicaljson | 2.0.0 | Apache 2.0 | 3.7+ | Serialization | Canonical JSON |
| beautifulsoup4 | 4.14.3 | MIT | 3.7+ | HTML parsing | Lenient HTML handling |
| lxml | 6.0.2 | BSD | 3.8+ | XML/HTML parsing | Fast, feature-rich |
| html5lib | 1.1 | MIT | 2.7+ | HTML parsing | WHATWG compliant |
| strip-ansi | 0.1.1 | MIT | 3.6+ | ANSI stripping | Simple, focused |
| syrupy | 5.1.0 | MIT | 3.10+ | Snapshot testing | Extensible, modern |

---

## 5. Best Practices & Patterns

### 5.1 Normalization Strategy Patterns

**Pattern 1: Parse-Normalize-Serialize**
```
Input → Parse → Normalize → Serialize → Compare
```
- Best for: JSON, HTML, XML
- Pros: Handles structural variations
- Cons: Requires parsing overhead

**Pattern 2: Regex-Based Substitution**
```
Input → Pattern Replace → Compare
```
- Best for: CLI output, logs, timestamps
- Pros: Fast, flexible
- Cons: Brittle patterns

### 5.2 Trade-offs: Strict vs Lenient Comparison

**Strict Comparison**:
- Exact string matching
- Use when: Output is deterministic, format matters

**Lenient Comparison**:
- Ignores whitespace, ordering, volatile fields
- Use when: Output has non-deterministic elements

### 5.3 Performance Considerations

**Parsing Overhead**:
- lxml: ~2-5x faster than beautifulsoup4
- html5lib: ~10x slower than lxml
- canonicaljson: Minimal overhead over json

**Recommendations**:
1. Cache parsed structures when comparing multiple times
2. Use lxml for HTML when performance matters
3. Pre-compile regex patterns for repeated CLI normalization

---

## 6. Implementation Recommendations

### 6.1 Recommended Architecture for pytest-patterns

**Modular Normalizer Design**:
```python
class Normalizer:
    """Base class for format-specific normalizers."""
    
    def normalize(self, content: str) -> str:
        """Normalize content for comparison."""
        raise NotImplementedError


class JSONNormalizer(Normalizer):
    """JSON normalization using canonicaljson."""
    
    def __init__(self, 
                 sort_keys: bool = True,
                 ignore_fields: list[str] = None,
                 float_precision: int = None):
        self.sort_keys = sort_keys
        self.ignore_fields = ignore_fields or []
        self.float_precision = float_precision
    
    def normalize(self, content: str) -> str:
        import json
        from canonicaljson import encode_canonical_json
        
        obj = json.loads(content)
        obj = self._remove_fields(obj, self.ignore_fields)
        
        if self.float_precision:
            obj = self._round_floats(obj, self.float_precision)
        
        return encode_canonical_json(obj).decode('utf-8')
```

### 6.2 Dependency Strategy

**Recommended Approach**: Optional dependencies

**pyproject.toml**:
```toml
[project.optional-dependencies]
json = ["canonicaljson>=2.0.0"]
html = ["lxml>=5.0.0", "beautifulsoup4>=4.12.0"]
cli = ["strip-ansi>=0.1.1"]
all = ["canonicaljson>=2.0.0", "lxml>=5.0.0", "beautifulsoup4>=4.12.0", "strip-ansi>=0.1.1"]
```

### 6.3 Configuration API

**Runtime Configuration**:
```python
def test_json_api(patterns):
    p = patterns.api_response
    p.normalize('json', 
                ignore_fields=['timestamp', 'request_id'],
                float_precision=4)
    p.optional('..."status":...')
    assert p == api_response_json


def test_html_output(patterns):
    p = patterns.html_page
    p.normalize('html',
                remove_scripts=True,
                sort_attributes=True)
    p.optional('...<head>...')
    assert p == html_content


def test_cli_tool(patterns):
    p = patterns.cli_output
    p.normalize('cli',
                strip_ansi=True,
                normalize_timestamps=True)
    p.in_order("""
Started at <TIMESTAMP>
Processing...
Completed
""")
    assert p == cli_output
```

---

## 7. Sources & References

### JSON Tools
- canonicaljson: https://pypi.org/project/canonicaljson/ (v2.0.0, Mar 2023)
- deepdiff: https://pypi.org/project/deepdiff/ (v8.6.1, Sep 2025)
- jsondiff: https://pypi.org/project/jsondiff/ (v2.2.1, Aug 2024)

### HTML Tools
- lxml: https://pypi.org/project/lxml/ (v6.0.2, Sep 2025)
- beautifulsoup4: https://pypi.org/project/beautifulsoup4/ (v4.14.3, Nov 2025)
- html5lib: https://pypi.org/project/html5lib/ (v1.1, Jun 2020)

### CLI Tools
- strip-ansi: https://pypi.org/project/strip-ansi/ (v0.1.1, Jun 2020)
- ansi: https://pypi.org/project/ansi/ (v0.3.7, Jan 2024)
- pytest-subprocess: https://pypi.org/project/pytest-subprocess/ (v1.5.3, Jan 2025)

### Snapshot Testing
- syrupy: https://pypi.org/project/syrupy/ (v5.1.0, Jan 2026)
- pytest-snapshot: https://pypi.org/project/pytest-snapshot/ (v0.9.0, Apr 2022)

### Standards & Specifications
- RFC 7159 (JSON): https://tools.ietf.org/html/rfc7159
- WHATWG HTML: https://html.spec.whatwg.org/
- ECMA-48 (ANSI): https://www.ecma-international.org/publications-and-standards/standards/ecma-48/

---

## 8. Gaps & Limitations

### Information Gaps

1. **XML Normalization**: Not extensively researched; lxml provides C14N (canonicalization) but specific best practices for testing not covered.

2. **YAML Normalization**: Not covered; would require similar approach to JSON with ordering and whitespace considerations.

3. **Binary Format Comparison**: Not covered; would require hex dump or structural comparison approaches.

4. **Performance Benchmarks**: No quantitative performance comparison between libraries; only relative speeds mentioned.

5. **Large File Handling**: Strategies for normalizing/comparing very large outputs (100MB+) not covered in detail.

### Tool Limitations

1. **html5lib Maintenance**: Last release June 2020; may have compatibility issues with newer Python versions.

2. **pytest-snapshot Maintenance**: Last release April 2022; less active development than syrupy.

3. **strip-ansi Simplicity**: Very simple library; may not handle all ANSI edge cases.

### Recommendations for Further Research

1. **Benchmark Normalization Performance**: Measure actual performance impact of different normalization strategies.

2. **User Experience Study**: Survey pytest-patterns users about desired normalization features.

3. **Integration Prototype**: Build prototype integration with recommended tools to validate architecture.

4. **Edge Case Documentation**: Document common edge cases in HTML/JSON/CLI normalization.

5. **Comparison with Similar Tools**: Research how other testing frameworks handle output normalization.

---

**End of Research Report**
