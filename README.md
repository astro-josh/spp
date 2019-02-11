# Simple Package Poller (SPP)

SPP polls the Astroconda, Astroconda-dev, and Conda Main channels as well as Pypi and Gitgub, displaying the latest version available for a given package.

## Support

None.

## Requirements

SPP requires the requests and beautifultable modules as well as Python >= 3.

## Usage

```
$ spp [-h] --package PACKAGE
              [--platform {osx-64,linux-32,linux-64,win-32,win-64,noarch}]
              [--all] [--json]

optional arguments:
  -h, --help            show this help message and exit
  --package, -p         Specify a package name to check.
  --platform, pl {osx-64,linux-32,linux-64,win-32,win-64,noarch}
                        Specify a platform.
  --all, -a             Display all versions available on each channel.
  --json, -j            Save JSON output.
```

## Examples

What versions of astroscrappy are available and what channel/repo are they in?

```bash
$ spp -p astroscrappy
```

On linux-64?

```bash
$ spp -p astroscrappy -pl linux-64
```

All info

```bash
$ spp -p astroscrappy -pl linux-64 -a
```

Output to JSON file

```bash
$ spp -p astroscrappy -pl linux-64 -a -j
```
