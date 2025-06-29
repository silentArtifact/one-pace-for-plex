#!/usr/bin/env python3
"""Transcode One Pace episodes to mp4/x265 and embed metadata.

This script searches for media files within the given directory, converts them to
mp4 using the x265 codec and copies audio streams. Metadata contained in the
matching .nfo file is embedded into the resulting mp4 file.
"""

import argparse
import logging
import re
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(message)s")
logger = logging.getLogger(__name__)

MKV_EXT = ".mkv"
MP4_EXT = ".mp4"


def parse_nfo(nfo_path: Path) -> dict[str, str]:
    """Extract relevant fields from an nfo file."""
    tree = ET.parse(nfo_path)
    root = tree.getroot()
    fields = {}
    for tag in ["title", "showtitle", "season", "episode"]:
        el = root.find(tag)
        if el is not None and el.text:
            fields[tag] = el.text
    return fields


def parse_additional_metadata(nfo_path: Path, media_path: Path) -> dict[str, str]:
    """Extract extra fields like original episode numbers and arc name."""
    extras: dict[str, str] = {}

    try:
        tree = ET.parse(nfo_path)
        root = tree.getroot()
    except ET.ParseError as exc:
        logger.warning("Failed to parse %s: %s", nfo_path, exc)
        return extras

    plot = root.find("plot")
    if plot is not None and plot.text:
        match = re.search(r"Anime Episode\(s\):\s*(.*)", plot.text)
        if match:
            extras["original_episode"] = match.group(1).strip()

    season_nfo = media_path.parent / "season.nfo"
    if season_nfo.exists():
        try:
            sroot = ET.parse(season_nfo).getroot()
            title_el = sroot.find("title")
            if title_el is not None and title_el.text:
                title = title_el.text
                if "." in title:
                    title = title.split(".", 1)[1]
                extras["onepace_arc"] = title.strip()
        except ET.ParseError:
            pass

    return extras


def transcode_file(media_path: Path, replace: bool, dry_run: bool, embed_artwork: bool) -> None:
    nfo_path = media_path.with_suffix(".nfo")
    if not nfo_path.exists():
        logger.warning("Skipping %s: missing nfo", media_path)
        return

    meta = parse_nfo(nfo_path)
    meta.update(parse_additional_metadata(nfo_path, media_path))
    output_path = media_path.with_suffix(MP4_EXT)
    poster = None
    if embed_artwork and "season" in meta:
        try:
            season_num = int(meta["season"])
            poster_name = f"season{season_num:02d}-poster.png"
            candidate = media_path.parents[1] / poster_name
            if candidate.exists():
                poster = candidate
        except ValueError:
            pass

    cmd = ["ffmpeg", "-i", str(media_path)]
    if poster:
        cmd += ["-i", str(poster)]
    cmd += [
        "-c:v",
        "libx265",
        "-c:a",
        "copy",
    ]
    if poster:
        cmd += ["-map", "0", "-map", "1", "-disposition:v:1", "attached_pic"]
    for key, value in meta.items():
        ffkey = {
            "showtitle": "show",
            "episode": "episode_id",
        }.get(key, key)
        cmd += ["-metadata", f"{ffkey}={value}"]
    cmd.append(str(output_path))

    if dry_run:
        logger.info("DRYRUN: %s", " ".join(cmd))
        return

    logger.info("Running: %s", " ".join(cmd))
    subprocess.run(cmd, check=True)

    if replace and media_path.suffix != MP4_EXT:
        media_path.unlink()
        output_path.rename(media_path)


def scan_directory(directory: Path, replace: bool, dry_run: bool, embed_artwork: bool) -> None:
    for file in directory.rglob(f"*{MKV_EXT}"):
        transcode_file(file, replace, dry_run, embed_artwork)
    for file in directory.rglob(f"*{MP4_EXT}"):
        if file.suffix == MP4_EXT:
            continue
        transcode_file(file, replace, dry_run, embed_artwork)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Transcode media to mp4/x265 and embed metadata from nfo files"
    )
    parser.add_argument(
        "directory", nargs="?", default=".", help="Root directory containing episodes"
    )
    parser.add_argument(
        "--replace", action="store_true", help="Replace original files after transcoding"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Show ffmpeg commands without executing"
    )
    parser.add_argument(
        "--embed-artwork",
        action="store_true",
        help="Embed season poster as cover art when available",
    )
    args = parser.parse_args()

    scan_directory(Path(args.directory), args.replace, args.dry_run, args.embed_artwork)


if __name__ == "__main__":
    main()
