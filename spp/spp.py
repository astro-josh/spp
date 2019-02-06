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
channels = (
    "http://ssb.stsci.edu/astroconda-dev/{platform}/repodata.json",
    "http://ssb.stsci.edu/astroconda/{platform}/repodata.json",
    "https://repo.continuum.io/pkgs/main/{platform}/repodata.json",
    "https://pypi.org/pypi/{name}/json"
)

def get_pypi():
    r = requests.get("https://pypi.org/pypi/numpy/json")
    r.raise_for_status()
    packages = ()
    packages = json.loads(r.text)['releases']
    latest_version = json.loads(r.text)['info']['version']
    releases = {k : v for k, v in packages.items() if v is not None}
    #print(releases.keys())
    print_releases(releases)
    print(latest_version)


def get_channel_data(url):
    data = {}
    try:
        r = requests.get(url)
        r.raise_for_status()
        data = json.loads(r.text)
    except requests.exceptions.HTTPError as e:
        print(e)
    except requests.exceptions.RequestException as e:
        print(e)

    return data

def get_package_info(name, platform=None):
    # if platform is not set, get user platform

    name = name.lower()

    if platform is None:
        platform = get_platform()

    # format channels by adding platform to conda channels and package name to pypi
    fchannels = list(map(lambda x: x.format(platform=platform, name=name), channels))

    print("\nPackage: {0}\nSubdir: {1}\n-------------------------".format(name, platform))

    for channel in fchannels:
        print("\nChannel: {0}\n---------------------------------------".format(channel))
        try:
            if not "pypi" in channel:
                packages = get_channel_data(channel)['packages']
                releases = {k : v for k, v in packages.items() if v["name"] == str.casefold(name)}
                print_releases(releases, channel, name)
            else:
                packages = get_channel_data(channel)['releases']
                releases = {k : v for k, v in packages.items() if v}
                print_releases(releases, channel, name)
        except Exception as e:
            # any error here is due to parsing the data returned from get_channel_data,
            # this means there are no releases or error with channel url
            print("No releases.", e)


# prints available releases from json data, latest version first
def print_releases(releases, channel, name):
    ## TODO: print in table format

    if len(releases) > 0:
        if not "pypi" in channel:
            for release in sorted(releases.items(), key=lambda k_v: k_v[1]['version'], reverse=True):
                print("Build:     {0}\nVersion:   {1}\nFile:      {2}\n"
                        .format(release[1]['build'], release[1]['version'], release[0]))
        else:
            for release, info in sorted(releases.items(), reverse=True):
                print("Build:     {0}\nVersion:   {1}\nFile:      {2}\n"
                        .format(name + "-" + release + "-" + info[0]['python_version'], release, info[0]['filename']))
    else:
        print("No releases.\n")


# gets user platform
def get_platform():
    system = systems[p.system()]
    machine = machines[p.machine()]
    return f"{system}-{machine}"


def get_latest_package():
    parser = argparse.ArgumentParser()

    parser.add_argument('--package', '-p', action = "store", dest = 'package', help = 'Specify a package name to check.')

    parser.add_argument('--platform', '-pl', action = "store", dest = 'platform', choices=["osx-64", "linux-32", "linux-64", "win-32", "win-64", "noarch"],
                            help = '(Optional) Specify a platform.', required=False)

    args = parser.parse_args()

    get_package_info(name=args.package, platform=args.platform)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('--package', '-p', action = "store", dest = 'package', help = 'Specify a package name to check.')

    parser.add_argument('--platform', '-pl', action = "store", dest = 'platform', choices=["osx-64", "linux-32", "linux-64", "win-32", "win-64", "noarch"],
                            help = '(Optional) Specify a platform.', required=False)

    ## TODO: add option to output to file

    args = parser.parse_args()

    get_package_info(name=args.package, platform=args.platform)

if (__name__ == '__main__'):
    main()
