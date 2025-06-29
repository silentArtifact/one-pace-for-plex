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
    }
