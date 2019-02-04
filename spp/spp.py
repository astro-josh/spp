import conda_api as conda
import argparse
import requests
import json

conda.set_root_prefix()

def get_package_info(name, platform=None):
    ## TODO: add pypi channel integration

    # channels to search package for
    channels = ("http://ssb.stsci.edu/astroconda-dev/", "http://ssb.stsci.edu/astroconda/", "https://repo.continuum.io/pkgs/main/")
    channels = list(map(lambda x: x + platform + "/repodata.json", channels))


    r = requests.get("http://ssb.stsci.edu/astroconda-dev/osx-64/repodata.json")
    r.raise_for_status
    packages = ()
    package = "astrosCrappy"
    packages = json.loads(r.text)['packages']

    new_data = {k : v for k, v in packages.items() if v["name"] == str.casefold(package)}
    print_packages2(new_data)


    # additional options for search
    kwargs = {'channel': '', "override_channels": " "}

    # if platform is set, add to kwargs
    if platform is not None:
        kwargs.update({'platform': platform})

    print("\nPackage: {0}\n-------------------------".format(name))

    # print available builds for public and dev channels
    for channel in channels:
        kwargs.update({'channel': channel})
        print("\nChannel: {0}\n---------------------------------------".format(channel))
        #print_packages(conda.search(name, **kwargs))

# prints packages from json data, latest version first
def print_packages2(packages):
    # sort by version number, latest first
    for release in sorted(packages.items(), key=lambda k_v: k_v[1]['version'], reverse=True):
        print("Build:   {0}\nFn:      {1}\nSubdir:  {2}\nVersion: {3}\n"
                .format(release[1]['build'], release[0], release[1]['subdir'], release[1]['version']))


# prints packages from json data, latest version first
def print_packages(packages):
    from operator import itemgetter

    try:
        # parsed json is a dictionary with a value of a list of dictionaries
        releases = list(packages.values())[0]
        # sort by version number, latest first
        for release in sorted(releases, key=itemgetter('version'), reverse=True):
            print("Build:   {0}\nChannel: {1}\nFn:      {2}\nSubdir:  {3}\nVersion: {4}\n"
                    .format(release['build'], release['channel'], release['fn'], release['subdir'], release['version']))
    except TypeError:
        # type error means search did not return expected json data, package was not found
        ## TODO: parse json error
        print("Package not found, please check your package name and parameters.\n")


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('--package', '-p', action = "store", dest = 'package', help = 'Specify a package name to check.')

    parser.add_argument('--platform', '-pl', action = "store", dest = 'platform', choices=["osx-64", "linux-32", "linux-64", "win-32", "win-64", "noarch"],
                            help = '(Optional) Specify a platform.', required=False)

    args = parser.parse_args()

    get_package_info(args.package, platform=args.platform)

if (__name__ == '__main__'):
    main()
