import tempfile
from pathlib import Path
from src.docs_sync import parser


def test_parse_simple_function(tmp_path: Path):
    p = tmp_path / "mod.py"
    p.write_text("""
def foo(a, b=1):
    \"\"\"This is foo.\"\"\"
    return a+b
""")
    res = parser.parse_file(str(p), module="mod")
    assert len(res["functions"]) == 1
    f = res["functions"][0]
    assert f.name == "foo"
    assert "a" in f.signature
    assert "This is foo" in (f.docstring or "")


def test_parse_class_with_method(tmp_path: Path):
    p = tmp_path / "mod2.py"
    p.write_text("""
class A:
    \"\"\"Class A\"\"\"
    def bar(self, x):
        \"\"\"Bar method\"\"\"
        return x
""")
    res = parser.parse_file(str(p), module="mod2")
    assert len(res["classes"]) == 1
    c = res["classes"][0]
    assert c.name == "A"
    assert len(c.methods) == 1


def test_parse_missing_file(tmp_path: Path):
    p = tmp_path / "nonexistent.py"
    try:
        parser.parse_file(str(p))
        assert False, "Expected FileNotFoundError"
    except FileNotFoundError:
        pass
