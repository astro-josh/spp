import json
import argparse
import requests


def get_package_info(name, platform=None):
    ## TODO: add pypi channel integration

    # if platform is not set, get user platform
    if platform is None:
        platform = get_platform()

    # channels to search package for
    channels = ("http://ssb.stsci.edu/astroconda-dev/", "http://ssb.stsci.edu/astroconda/", "https://repo.continuum.io/pkgs/main/")
    channels = list(map(lambda x: x + platform + "/repodata.json", channels))

    print("\nPackage: {0}\nSubdir: {1}\n-------------------------".format(name, platform))
    for channel in channels:
        print("\nChannel: {0}\n---------------------------------------".format(channel))
        try:
            r = requests.get(channel)
            r.raise_for_status()
            packages = ()
            packages = json.loads(r.text)['packages']
            releases = {k : v for k, v in packages.items() if v["name"] == str.casefold(name)}
            print_releases(releases)
        except requests.exceptions.HTTPError as e:
            print("No Packages for this channel and platform.")
            print(e)
        except requests.exceptions.RequestException as e:
            print(e)
            exit(1)


# prints available releases from json data, latest version first
def print_releases(releases):
    # sort by version number, latest first
    if len(releases) > 0:
        for release in sorted(releases.items(), key=lambda k_v: k_v[1]['version'], reverse=True):
            print("Build:     {0}\nVersion:   {1}\nFile:      {2}\n"
                    .format(release[1]['build'], release[1]['version'], release[0]))
    else:
        print("No releases.\n")


# gets user platform
def get_platform():
    return


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
