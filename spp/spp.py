import json
import argparse
import requests
import platform as p
from pkg_resources import parse_version
from beautifultable import BeautifulTable


# used to map system/machine info to a channel platform
systems = dict(
    Linux = 'linux',
    Darwin = 'osx',
    Windows = 'win',
)

machines = dict(
    i386 = '32',
    x86_64 = '64',
)

# channels to search for a package
channels = {
    'Astroconda': "http://ssb.stsci.edu/astroconda/{platform}/repodata.json",
    'Astroconda-dev': "http://ssb.stsci.edu/astroconda-dev/{platform}/repodata.json",
    'Conda main': "https://repo.continuum.io/pkgs/main/{platform}/repodata.json",
    'Pypi': "https://pypi.org/pypi/{name}/json",
    'Github': "https://api.github.com/search/repositories?q={name}"
}


def get_channel_data(url):
    """Returns channel JSON data from a given url"""
    data = {}

    try:
        r = requests.get(url)
        r.raise_for_status()
        data = json.loads(r.text)
    except requests.exceptions.HTTPError as e:
        # http errors mean invalid url, server not reachable
        pass
    except requests.exceptions.RequestException as e:
        print(e)

    return data


def display_package_info(name, platform=None, all=False):
    """Displays package info"""
    name = name.lower()

    # if platform is not set, get user platform
    if platform is None:
        platform = get_platform()

    # format channels by adding platform to conda channels and package name to pypi
    fchannels = {k : v.format(platform=platform, name=name) for k, v in channels.items()}
    print(f"\nPackage: {name}\nSubdir: {platform}\n" + "-" * 30 + "\n")

    if all:
        for channel in fchannels.items():
            print(f"\nChannel: {channel[0]}\n" + "-" *30)
            releases = get_releases(channel, name)
            print_releases(releases, all, channel)
    else:
        releases = get_latest_releases(fchannels, name)
        print_releases(releases, all)


def print_releases(releases, all, channel=None):
    """Prints release info in table format"""

    if len(releases) > 0:
        table = BeautifulTable()
        table.set_style(BeautifulTable.STYLE_GRID)

        if all:
            if channel[0] == "Pypi":
                table.append_column('Version', releases)
            elif channel[0] == "Github":
                table.append_column('Version', [x['name'] for x in releases])
                table.append_column('File', [x['tarball_url'] for x in releases])
            else:
                table.append_column('Version', [x['version'] for x in releases])
                table.append_column('Build', [x['build'] for x in releases])
        else:
            table.column_headers = list(releases.keys())
            table.append_row(list(releases.values()))
        print(table)
    else:
        # releases is empty, no data for the package
        print("No releases.\n")


def get_releases(channel, name):
    """Gets release data for a channel and a specified package"""
    releases = ()

    try:
        if channel[0] == "Pypi":
            packages = get_channel_data(channel[1])['releases']
            # get only available (non-empty) releases
            releases = [k  for k in packages.keys() if k]
            releases.sort(key=lambda x: parse_version(x), reverse=True)
        elif channel[0] == "Github":
            packages = get_channel_data(channel[1])['items'][0]
            print(f"Repo: {packages['html_url']}\n")
            # get the releases from the tags endpoint
            releases = get_channel_data(packages['tags_url'])
            releases.sort(key=lambda x: parse_version(x['name']), reverse=True)
        else:
            packages = get_channel_data(channel[1])['packages']
            # get only the releases matching the name of the package
            releases = [x for x in packages.values() if x["name"] == str.casefold(name)]
            releases.sort(key=lambda x: parse_version(x['version']), reverse=True)

    # key or index error means returned channel data not formatted as expected, i.e. no releases
    except KeyError as e:
        pass
    except IndexError as e:
        pass

    return releases


def get_latest_releases(channels, name):
    """Gets the latest release version of a package for each channel"""
    latest_releases = dict(zip(channels.keys(), ['None'] * len(channels)))

    try:
        for channel, version in latest_releases.items():
            if channel == 'Pypi':
                # pypi always shows latest version in info
                latest_releases[channel] = get_channel_data(channels[channel])['info']['version']
            elif channel == 'Github':
                packages = get_channel_data(channels[channel])['items'][0]
                releases = get_channel_data(packages['tags_url'])
                # sort by version number
                releases.sort(key=lambda x: parse_version(x['name']), reverse=True)
                latest_releases[channel] = releases[0]['name']
            else:
                packages = get_channel_data(channels[channel])['packages']
                # get only the releases matching the name of the package
                releases = [x for x in packages.values() if x["name"] == str.casefold(name)]
                # sort by version number
                releases.sort(key=lambda x: parse_version(x['version']), reverse=True)
                if len(releases) > 0:
                    latest_releases[channel] = releases[0]['version']
    # key or index error means returned channel data not formatted as expected, i.e. no release
    except KeyError as e:
        pass
    except IndexError as e:
        pass

    return latest_releases


# gets user platform
def get_platform():
    """Gets the platform of the machine using system mappings"""
    system = systems[p.system()]
    machine = machines[p.machine()]
    return f"{system}-{machine}"


def main():
    """Gets arguments from command line to display package release info"""
    parser = argparse.ArgumentParser()

    parser.add_argument('--package', '-p', action = "store", dest = 'package', help = 'Specify a package name to check.', required=True)

    parser.add_argument('--platform', '-pl', action = "store", dest = 'platform',
                            choices=["osx-64", "linux-32", "linux-64", "win-32", "win-64", "noarch"],
                            help = '(Optional) Specify a platform.', required=False)

    # defaults to only showing latest version, shows all if given -a
    parser.add_argument('--all', '-a', action = "store_true", dest = 'all',
                            help = 'Display all versions available on each channel.', required=False)

    ## TODO: add option to output to file
    args = parser.parse_args()

    display_package_info(name=args.package, platform=args.platform, all=args.all)

if (__name__ == '__main__'):
    main()
