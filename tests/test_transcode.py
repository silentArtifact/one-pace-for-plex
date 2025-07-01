import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "dist"))

from transcode import parse_nfo


def test_parse_nfo(tmp_path):
    xml_content = """<?xml version='1.0' encoding='UTF-8'?>
<episodedetails>
  <title>Test Title</title>
  <showtitle>One Pace</showtitle>
  <season>1</season>
  <episode>10</episode>
  <plot>This is a test description.</plot>
</episodedetails>
"""
    nfo_file = tmp_path / "test.nfo"
    nfo_file.write_text(xml_content)
    result = parse_nfo(nfo_file)
    assert result == {
        "title": "Test Title",
        "showtitle": "One Pace",
        "season": "1",
        "episode": "10",
        "description": "This is a test description.",
    }

from transcode import prompt_directory


def test_prompt_directory_handles_quotes(tmp_path, monkeypatch):
    quoted = tmp_path / "with space"
    quoted.mkdir()

    def fake_input(prompt):
        return f'"{quoted}"'

    monkeypatch.setattr("builtins.input", fake_input)
    result = prompt_directory()
    assert result == quoted
