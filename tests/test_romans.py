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


def test_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0


def test_basic():
    with NamedTemporaryFile() as tmp:
        result = runner.invoke(app, [str(ROMANS_STEM), tmp.name])
        assert result.exit_code == 0
        assert Path(tmp.name).exists()


def test_root():
    with NamedTemporaryFile() as tmp:
        result = runner.invoke(app, [str(ROMANS_STEM), tmp.name, "--root", "ATEXT"])
        assert result.exit_code == 0
        assert Path(tmp.name).exists()
        assert "strict digraph  {\nATEXT [color=red, label=ATEXT]" in Path(tmp.name).read_text()

        
def test_root_color():
    with NamedTemporaryFile() as tmp:
        result = runner.invoke(app, [str(ROMANS_STEM), tmp.name, "--root", "ATEXT", "--root-color", "green"])
        assert result.exit_code == 0
        assert Path(tmp.name).exists()
        assert "strict digraph  {\nATEXT [color=green, label=ATEXT]" in Path(tmp.name).read_text()

        
def test_color_toml():
    with NamedTemporaryFile() as tmp:
        result = runner.invoke(app, [str(ROMANS_STEM), tmp.name, "--root", "ATEXT", "--colors", str(COLORS_TOML)])
        assert result.exit_code == 0
        assert Path(tmp.name).exists()
        output = Path(tmp.name).read_text()
        assert "strict digraph  {\nATEXT [color=red, label=ATEXT]" in output
        assert "L1159 [color=blue, label=L1159" in output

        
def test_color_json():
    with NamedTemporaryFile() as tmp:
        result = runner.invoke(app, [str(ROMANS_STEM), tmp.name, "--root", "ATEXT", "--colors", str(COLORS_JSON)])
        assert result.exit_code == 0
        assert Path(tmp.name).exists()
        output = Path(tmp.name).read_text()
        assert "strict digraph  {\nATEXT [color=red, label=ATEXT]" in output
        assert "L1159 [color=blue, label=L1159" in output

        
        
