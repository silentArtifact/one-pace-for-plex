import sys
from pathlib import Path

# Add dist folder to import path
sys.path.append(str(Path(__file__).resolve().parents[1] / "dist"))

from rename import get_episode_from_id, get_episode_from_nfo, get_episode_from_media, Episode, SHOW_NAME


def test_get_episode_from_id():
    ep = get_episode_from_id("One Pace", "S05E02")
    assert ep.show == "One Pace"
    assert ep.season == 5
    assert ep.number == 2


def test_get_episode_from_nfo(tmp_path):
    fname = "One Pace - S02E03 - Cool Title.nfo"
    path = tmp_path / fname
    path.write_text("")
    ep = get_episode_from_nfo(path)
    assert ep.title == "Cool Title"
    assert ep.season == 2
    assert ep.number == 3
    assert ep.extended is False


def test_get_episode_from_media(tmp_path):
    fname = "[One Pace][1] TestArc 05 [1080p][ABC123].mkv"
    path = tmp_path / fname
    path.write_text("")
    seasons = {"TestArc": 1}
    ep = get_episode_from_media(path, seasons)
    assert ep.show == SHOW_NAME
    assert ep.season == 1
    assert ep.number == 5
    assert ep.extended is False
