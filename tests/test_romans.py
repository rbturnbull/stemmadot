import re
from pathlib import Path
from tempfile import NamedTemporaryFile
from typer.testing import CliRunner
from stemmadot.main import app

runner = CliRunner()

TEST_DIR = Path(__file__).parent
DATA_DIR = TEST_DIR/"data"
ROMANS_STEM = DATA_DIR/"romans.stem"
COLORS_TOML = DATA_DIR/"romans-colors.toml"
COLORS_JSON = DATA_DIR/"romans-colors.json"

def _assert_node_with_attrs(dot_text: str, node: str, **attrs):
    """
    Assert that a node like `ATEXT` appears with all given attrs,
    regardless of order/spacing/line breaks, e.g. color='red', label='ATEXT'.
    """
    # Find the node block: ATEXT [ ... ]
    node_pat = re.compile(rf"\b{re.escape(node)}\b\s*\[\s*([^\]]*)\]", re.DOTALL)
    m = node_pat.search(dot_text)
    assert m, f"Did not find node {node}"

    inside = m.group(1)
    for k, v in attrs.items():
        # Accept bare identifiers or quoted values (Graphviz may quote)
        # e.g. label=ATEXT or label="ATEXT"
        attr_pat = re.compile(rf"\b{re.escape(k)}\s*=\s*(?:{re.escape(str(v))}|\"{re.escape(str(v))}\")\b")
        assert attr_pat.search(inside), f"Node {node} missing {k}={v}"

def _assert_root_with_color(dot_path, color: str):
    text = dot_path.read_text()
    _assert_node_with_attrs(text, "ATEXT", color=color, label="ATEXT")


def test_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0

def test_basic():
    with NamedTemporaryFile(suffix=".dot") as tmp:
        result = runner.invoke(app, [str(ROMANS_STEM), tmp.name])
        assert result.exit_code == 0
        assert Path(tmp.name).exists()

def test_root():
    with NamedTemporaryFile(suffix=".dot") as tmp:
        result = runner.invoke(app, [str(ROMANS_STEM), tmp.name, "--root", "ATEXT"])
        assert result.exit_code == 0
        assert Path(tmp.name).exists()
        _assert_root_with_color(Path(tmp.name), "red")

def test_root_color():
    with NamedTemporaryFile(suffix=".dot") as tmp:
        result = runner.invoke(app, [str(ROMANS_STEM), tmp.name, "--root", "ATEXT", "--root-color", "green"])
        assert result.exit_code == 0
        assert Path(tmp.name).exists()
        _assert_root_with_color(Path(tmp.name), "green")

def test_color_toml():
    with NamedTemporaryFile(suffix=".dot") as tmp:
        result = runner.invoke(app, [str(ROMANS_STEM), tmp.name, "--root", "ATEXT", "--colors", str(COLORS_TOML)])
        assert result.exit_code == 0
        assert Path(tmp.name).exists()
        text = Path(tmp.name).read_text()
        _assert_root_with_color(Path(tmp.name), "red")
        assert re.search(r"L1159", text)

def test_color_json():
    with NamedTemporaryFile(suffix=".dot") as tmp:
        result = runner.invoke(app, [str(ROMANS_STEM), tmp.name, "--root", "ATEXT", "--colors", str(COLORS_JSON)])
        assert result.exit_code == 0
        assert Path(tmp.name).exists()
        text = Path(tmp.name).read_text()
        _assert_root_with_color(Path(tmp.name), "red")
        assert re.search(r"L1159", text)
