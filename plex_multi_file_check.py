"""Find movies with more than one media file in a Plex library.

Connects to a Plex Media Server, scans a library section and reports every
movie that is backed by more than one file, so duplicates can be reviewed and
cleaned up manually.
"""

from __future__ import annotations

import argparse
import csv
import os
import sys
from collections.abc import Iterator
from pathlib import Path

from plexapi.exceptions import NotFound, Unauthorized
from plexapi.server import PlexServer

DEFAULT_BASEURL = "http://127.0.0.1:32400"
DEFAULT_LIBRARY = "Films"
DEFAULT_OUTPUT = Path("multi_file_movies.csv")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--baseurl",
        default=os.getenv("PLEX_BASEURL", DEFAULT_BASEURL),
        help="Plex server URL. Falls back to the PLEX_BASEURL env var.",
    )
    parser.add_argument(
        "--token",
        default=os.getenv("PLEX_TOKEN"),
        help="Plex authentication token (X-Plex-Token). "
        "Falls back to the PLEX_TOKEN env var. Never hardcode it.",
    )
    parser.add_argument(
        "--library",
        default=os.getenv("PLEX_LIBRARY", DEFAULT_LIBRARY),
        help="Name of the library section to scan.",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Path of the CSV report to write.",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="Connection timeout in seconds.",
    )
    return parser.parse_args(argv)


def iter_duplicates(section) -> Iterator[tuple[str, str]]:
    """Yield (title, file path) pairs for every movie with several files."""
    for movie in section.all():
        files = [part.file for media in movie.media for part in media.parts]
        if len(files) > 1:
            for file in files:
                yield movie.title, file


def write_report(rows: list[tuple[str, str]], output: Path) -> None:
    with output.open(mode="w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Movie", "File"])
        writer.writerows(rows)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    if not args.token:
        print(
            "error: a Plex token is required. Pass --token or set PLEX_TOKEN.\n"
            "See https://support.plex.tv/articles/"
            "204059436-finding-an-authentication-token-x-plex-token/",
            file=sys.stderr,
        )
        return 2

    try:
        plex = PlexServer(args.baseurl, args.token, timeout=args.timeout)
    except Unauthorized:
        print("error: Plex rejected the token.", file=sys.stderr)
        return 1
    except Exception as exc:  # pylint: disable=broad-except
        print(f"error: could not reach {args.baseurl}: {exc}", file=sys.stderr)
        return 1

    try:
        section = plex.library.section(args.library)
    except NotFound:
        available = ", ".join(s.title for s in plex.library.sections())
        print(
            f"error: library {args.library!r} not found. Available: {available}",
            file=sys.stderr,
        )
        return 1

    rows = list(iter_duplicates(section))
    write_report(rows, args.output)

    titles = len({title for title, _ in rows})
    print(f"Found {titles} movie(s) with duplicated files ({len(rows)} files).")
    print(f"Results saved as '{args.output}'")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
