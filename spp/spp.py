import conda_api as conda
import argparse


def get_package_info(name, platform=None):
    #TODO: add conda main channel, add Pypi
    channels = ("http://ssb.stsci.edu/astroconda-dev", "http://ssb.stsci.edu/astroconda")
    kwargs = { 'channel': '', "override_channels": " "}

    if platform is not None:
        kwargs.update({'platform': platform})

    print("\nPackage: {0}\n-------------------------".format(name))
    for channel in channels:
        kwargs.update({'channel': channel})
        print("\nChannel: {0}\n---------------------------------------".format(channel))
        print_packages(conda.search(name, **kwargs))


def print_packages(packages):
    from operator import itemgetter
    releases = list(packages.values())[0]
    for release in sorted(releases, key=itemgetter('version'), reverse=True):
        if isinstance(release, dict):
            print("Build:   {0}\nChannel: {1}\nFn:      {2}\nSubdir:  {3}\nVersion: {4}\n"
                    .format(release['build'], release['channel'], release['fn'], release['subdir'], release['version']))
        else:
            exit(1) #TODO: handle error parsing stdout


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('--package', '-p', action = "store", dest = 'package', help = 'Specify a package name to check.')

    parser.add_argument('--platform', '-pl', action = "store", dest = 'platform', choices=["osx-64", "linux-32", "linux-64"],
                            help = '(Optional) Specify a platform.', required=False)

    args = parser.parse_args()

    get_package_info(args.package, platform=args.platform)

if (__name__ == '__main__'):
    main()
