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

def _assert_root_with_color(dot_path: Path, color: str):
    text = dot_path.read_text()
    # Matches:
    # strict digraph { ... ATEXT [ ... color=<color> ... label=ATEXT ... ] ... }
    # in any attribute order / with optional semicolons / flexible whitespace.
    pattern = (
        r"strict\s+digraph\s*{\s*"
        r"ATEXT\s*\[\s*"
        r"(?:(?=[^\]]*color\s*=\s*" + re.escape(color) + r")(?=[^\]]*label\s*=\s*ATEXT)[^\]]*)"
        r"\]"
    )
    assert re.search(pattern, text, flags=re.DOTALL), f"Did not find ATEXT with color={color} and label=ATEXT"

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
        assert re.search(r"\nL1159\s*\[\s*(?=[^\]]*color\s*=\s*blue)(?=[^\]]*label\s*=\s*L1159)", text)

def test_color_json():
    with NamedTemporaryFile(suffix=".dot") as tmp:
        result = runner.invoke(app, [str(ROMANS_STEM), tmp.name, "--root", "ATEXT", "--colors", str(COLORS_JSON)])
        assert result.exit_code == 0
        assert Path(tmp.name).exists()
        text = Path(tmp.name).read_text()
        _assert_root_with_color(Path(tmp.name), "red")
        assert re.search(r"\nL1159\s*\[\s*(?=[^\]]*color\s*=\s*blue)(?=[^\]]*label\s*=\s*L1159)", text)
