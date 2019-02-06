import json
import argparse
import requests
import platform as p

# used to map system/machine info to a channel platform
systems = dict(
    Linux='linux',
    Darwin='osx',
    Windows='win'
)

machines = dict(
    i386='32',
    x86_64='64'
)

# channels to search for a package
channels = {
    'Astroconda': "http://ssb.stsci.edu/astroconda/{platform}/repodata.json",
    'Astroconda-dev': "http://ssb.stsci.edu/astroconda-dev/{platform}/repodata.json",
    'Conda main': "https://repo.continuum.io/pkgs/main/{platform}/repodata.json",
    'Pypi': "https://pypi.org/pypi/{name}/json"
}


def get_channel_data(url):
    data = {}
    try:
        r = requests.get(url)
        r.raise_for_status()
        data = json.loads(r.text)
    except requests.exceptions.HTTPError as e:
        pass
    except requests.exceptions.RequestException as e:
        print(e)

    return data


def display_package_info(name, platform=None, latest_only=False):
    name = name.lower()

    # if platform is not set, get user platform
    if platform is None:
        platform = get_platform()

    # format channels by adding platform to conda channels and package name to pypi
    #fchannels = list(map(lambda x, v: v.format(platform=platform, name=name), channels.items()))
    fchannels = {k : v.format(platform=platform, name=name) for k, v in channels.items()}
    print(f"\nPackage: {name}\nSubdir: {platform}\n" + "-" * 30)

    if latest_only:
        versions = {}
        for channel, channel_url in fchannels.items():
            versions[channel] = get_latest_release(channel_url, name)
        print("Channel\t  |", *versions, sep="\t\t")
        print("Version\t  |", *list(versions.values()), sep="\t\t")


    else:
        for channel, channel_url in fchannels.items():
            print(f"\nChannel: {channel}\n" + "-" *30)
            try:
                if not "Pypi" in channel:
                    packages = get_channel_data(channel_url)['packages']
                    # get only the releases matching the name of the package
                    releases = {k : v for k, v in packages.items() if v["name"] == str.casefold(name)}
                    print_releases(releases, channel, name)
                else:
                    packages = get_channel_data(channel_url)['releases']
                    # get only available (non-empty) releases
                    releases = {k : v for k, v in packages.items() if v}
                    print_releases(releases, channel, name)
            except Exception as e:
                # any error here is due to parsing the data returned from get_channel_data,
                # this means there are no releases or error with channel url
                print("No releases.\n")


# prints available releases from json data, latest version first
def print_releases(releases, channel, name):
    ## TODO: print in table format

    if len(releases) > 0:
        if not "Pypi" in channel:
            for release in sorted(releases.items(), key=lambda k_v: k_v[1]['version'], reverse=True):
                print("Build:     {0}\nVersion:   {1}\nFile:      {2}\n"
                        .format(release[1]['build'], release[1]['version'], release[0]))
        else:
            # pypi json is formatted differently
            for release, info in sorted(releases.items(), reverse=True):
                print("Build:     {0}\nVersion:   {1}\nFile:      {2}\n"
                        .format(name + "-" + release + "-" + info[0]['python_version'], release, info[0]['filename']))
    else:
        # releases is empty, no data for the package
        print("No releases.\n")


def get_latest_release(channel_url, name):
    release = 'None'

    try:
        if not "pypi" in channel_url:
            packages = get_channel_data(channel_url)['packages']
            # get only the releases matching the name of the package
            releases = {k : v for k, v in packages.items() if v["name"] == str.casefold(name)}
            if len(releases) > 0:
                release = sorted(releases.items(), key=lambda k_v: k_v[1]['version'], reverse=True)[0][1]['version']
        else:
            release = get_channel_data(channel_url)['info']['version']
    except KeyError as e:
        # any error here is due to parsing the data returned from get_channel_data,
        # this means there are no releases or error with channel url
        pass
    return release


# gets user platform
def get_platform():
    system = systems[p.system()]
    machine = machines[p.machine()]
    return f"{system}-{machine}"


# default, gets all available package versions
def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('--package', '-p', action = "store", dest = 'package', help = 'Specify a package name to check.', required=True)

    parser.add_argument('--platform', '-pl', action = "store", dest = 'platform', choices=["osx-64", "linux-32", "linux-64", "win-32", "win-64", "noarch"],
                            help = '(Optional) Specify a platform.', required=False)

    parser.add_argument('--latest', '-l', action = "store_true", dest = 'latest_only', help = 'Only display latest version available for each channel.', required=False)

    ## TODO: add option to output to file

    args = parser.parse_args()

    display_package_info(name=args.package, platform=args.platform, latest_only=args.latest_only)

if (__name__ == '__main__'):
    main()
