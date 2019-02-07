import json
import argparse
import requests
import platform as p
from pkg_resources import parse_version


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
    name = name.lower()

    # if platform is not set, get user platform
    if platform is None:
        platform = get_platform()

    # format channels by adding platform to conda channels and package name to pypi
    fchannels = {k : v.format(platform=platform, name=name) for k, v in channels.items()}
    print(f"\nPackage: {name}\nSubdir: {platform}\n" + "-" * 30 + "\n")

    if all:
        for channel, channel_url in fchannels.items():
            print(f"\nChannel: {channel}\n" + "-" *30)
            try:
                if channel == "Pypi":
                    packages = get_channel_data(channel_url)['releases']
                    # get only available (non-empty) releases
                    releases = {k : v for k, v in packages.items() if v}
                    print_releases(releases, channel, name)
                elif channel == "Github":
                    packages = get_channel_data(channel_url)
                    #if packages['total_count'] > 0:
                    releases = packages['items'][0]
                    print_releases(releases, channel, name)
                else:
                    packages = get_channel_data(channel_url)['packages']
                    # get only the releases matching the name of the package
                    releases = {k : v for k, v in packages.items() if v["name"] == str.casefold(name)}
                    print_releases(releases, channel, name)
            # key or index error means returned channel data not formatted as expected, i.e. no releases
            except KeyError as e:
                print("No releases.\n")
            except IndexError as e:
                print("No releases.\n")
    else:
        versions = {}
        for channel in fchannels.items():
            versions[channel[0]] = get_latest_release(channel, name)

        # # TODO: make table look better, perhaps use a module?
        print("Channel    |", *versions, sep="\t\t")
        print("Version    |", *list(versions.values()), sep="\t\t\t")


# prints available releases from json data, latest version first
def print_releases(releases, channel, name):
    ## TODO: print in table format

    if len(releases) > 0:
        if channel == "Pypi":
            # pypi json is formatted differently
            for release, info in sorted(releases.items(), key=lambda x: parse_version(x[0]), reverse=True):
                print("Build:     {0}\nVersion:   {1}\nFile:      {2}\n"
                        .format(name + "-" + release + "-" + info[0]['python_version'], release, info[0]['filename']))
        elif channel == "Github":
            url = releases["html_url"]
            print(f"Repo: {url}\n")
            releases = get_channel_data(releases['tags_url'])
            for release in sorted(releases, key=lambda x: parse_version(x['name']), reverse=True):
                print("Version:   {0}\nFile:      {1}\n"
                        .format(release['name'], release['tarball_url']))
        else:
            #for release in sorted(releases.items(), key=lambda k_v: k_v[1]['version'], reverse=True):
            for release in sorted(releases.items(), key=lambda x: parse_version(x[1]['version']), reverse=True):
                print("Build:     {0}\nVersion:   {1}\nFile:      {2}\n"
                        .format(release[1]['build'], release[1]['version'], release[0]))
    else:
        # releases is empty, no data for the package
        print("No releases.\n")


def get_latest_release(channel, name):
    release = 'None'
    try:
        if channel[0] == "Pypi":
            release = get_channel_data(channel[1])['info']['version']
        elif channel[0] == "Github":
            packages = get_channel_data(channel[1])['items'][0]
            releases = get_channel_data(packages['tags_url'])
            release = sorted(releases, key=lambda x: parse_version(x['name']), reverse=True)[0]['name']
        else:
            packages = get_channel_data(channel[1])['packages']
            # get only the releases matching the name of the package
            releases = {k : v for k, v in packages.items() if v["name"] == str.casefold(name)}
            if len(releases) > 0:
                release = sorted(releases.items(), key=lambda x: parse_version(x[1]['version']), reverse=True)[0][1]['version']
    # key or index error means returned channel data not formatted as expected, i.e. no releases
    except KeyError as e:
        pass
    except IndexError as e:
        pass

    return release


# gets user platform
def get_platform():
    system = systems[p.system()]
    machine = machines[p.machine()]
    return f"{system}-{machine}"


def main():
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
