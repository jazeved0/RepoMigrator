# RepoMigrator

Short Python scripts that assist in repository migration between Github.com and Github Enterprise. The repository contains two different scripts: `migrate.py`, the main script, and `batch.py` a helper wrapper script that assists with repeated migration. I originally made these scripts to help move 10 or so of my private repositories on my school's Github Enterprise to private repos on Github.com, and I've uploaded them in case they help anyone else.

## Usage

### `migrate.py`

```
usage: migrate.py [-h] [--sourceUser user] [--sourceToken token]
                  [--destUser user] [--destToken token] [--temp path]
                  [--remote name] [--timeout ms]
                  sourceRepo destRepo

Migrate github repositories between two different optionally authenticated
remotes.

positional arguments:
  sourceRepo           the source github repository
  destRepo             the destination github repository

optional arguments:
  -h, --help           show this help message and exit
  --sourceUser user    authentication user for the source repo
  --sourceToken token  authentication token/password for the source repo
  --destUser user      authentication user for the dest repo
  --destToken token    authentication token/password for the dest repo
  --temp path          temp directory for cloning the source repo
  --remote name        name of the destination remote to use
  --timeout ms         max amount of time to wait between command parses
```

### `batch.py`

```
usage: batch.py [-h] [--sourceUser user] [--sourceToken token] --destUser user
                [--destToken token] [--temp path] [--remote name]
                [--timeout ms]
                src_site dest_site repo [repo ...]

Migrates multiple repositories at once

positional arguments:
  src_site             the source github site
  dest_site            the destination github site
  repo                 each source repo to use; either user/repo or repo

optional arguments:
  -h, --help           show this help message and exit
  --sourceUser user    authentication user for the source repo(s)
  --sourceToken token  authentication token/password for the source repo(s)
  --destUser user      authentication user for the dest repo(s)
  --destToken token    authentication token/password for the dest repo(s)
  --temp path          temp directory for cloning the source repo(s)
  --remote name        name of the destination remote to use
  --timeout ms         max amount of time to wait between command parses
```

## Dependencies

The scripts have only been tested on Python 3.6 and depend on the following dependency, installable with `pip install <name>`:

- [pexpect](https://pexpect.readthedocs.io/en/stable/) - Python module for spawning child applications, controlling them, and responding to expected patterns in their output
