# Simple Package Poller (SPP)

SPP polls the Astroconda, Astroconda-dev, and Conda Main channels as well as Pypi and Gitgub, displaying the latest version available for a given package.

## Support

None.

## Requirements

SPP Requires requests and beautifultable as well as Python >= 3.

## Usage

```
$ spp --help
usage: spp.py [-h] --package PACKAGE (required)
              [--platform {osx-64,linux-32,linux-64,win-32,win-64,noarch}] (optional)
              [--all] (optional)
```


## Examples

-What versions of astroscrappy are available?

```bash
$ spp -p astroscrappy
```

On linux-64?

```bash
$ spp -p astroscrappy -p linux-64
```

All info

```bash
$ spp -p astroscrappy -p linux-64 --all
```
