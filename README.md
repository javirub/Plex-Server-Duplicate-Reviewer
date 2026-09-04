# Plex Server Duplicate Reviewer

Scans a Plex library and reports every movie backed by **more than one media
file**, writing the results to a CSV so duplicates can be reviewed and cleaned
up manually.

## Requirements

- Python 3.10+
- [`plexapi`](https://pypi.org/project/PlexAPI/)

```bash
pip install -r requirements.txt
```

## Usage

The Plex token is read from the environment — it is never stored in the source.
[How to find your X-Plex-Token](https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/).

```bash
export PLEX_TOKEN="your-token"
python plex_multi_file_check.py --baseurl http://127.0.0.1:32400 --library Films
```

### Options

| Flag | Env var | Default | Description |
| --- | --- | --- | --- |
| `--baseurl` | `PLEX_BASEURL` | `http://127.0.0.1:32400` | Plex server URL |
| `--token` | `PLEX_TOKEN` | — (required) | Plex authentication token |
| `--library` | `PLEX_LIBRARY` | `Films` | Library section to scan |
| `-o`, `--output` | — | `multi_file_movies.csv` | CSV report path |
| `--timeout` | — | `30` | Connection timeout in seconds |

## Output

A CSV with one row per duplicated file:

```csv
Movie,File
The Matrix,/media/films/The Matrix (1999)/The Matrix 1080p.mkv
The Matrix,/media/films/The Matrix (1999)/The Matrix 4K.mkv
```

The script exits with `2` if no token is supplied and `1` if the server is
unreachable, the token is rejected or the library does not exist.

## License

MIT — see [LICENSE](./LICENSE).
