import conda_api as conda
import argparse


class PackageInfo(argparse.Action):
    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        if nargs is not None:
            raise ValueError("nargs not allowed")
        super(PackageInfo, self).__init__(option_strings, dest, **kwargs)

    def __call__(self, parser, namespace, value, option_string=None):
        setattr(namespace, self.dest, value)
        get_package_info(value)


class ChannelAdd(argparse.Action):
    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        if nargs is not None:
            raise ValueError("nargs not allowed")
        super(ChannelAdd, self).__init__(option_strings, dest, **kwargs)

    def __call__(self, parser, namespace, value, option_string=None):
        setattr(namespace, self.dest, values)
        add_channels(values)


def get_package_info(name):
    #TODO: add options for specifying channel
    packages = conda.package_info(name)
    print(name)

    for package, releases in packages.items():
        for release in releases:
            print("Build:   {0}\nChannel: {1}\nFn:      {2}\nSubdir:  {3}\nURL:     {4}\nVersion: {5}\n"
                .format(release['build'], release['channel'], release['fn'], release['subdir'], release['url'], release['version']))


def add_channels(channels):
    #TODO: validate urls, add if valid
    #conda.config_add("channels", "http://ssb.stsci.edu/astroconda-dev")
    #print(conda.config_get()['channels'])
    #conda.config_remove("channels", "http://ssb.stsci.edu/astroconda-dev")
    #print(conda.config_get()['channels'])
    return


def display_channels():
    return


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('--package', '-p', action = PackageInfo, dest = 'package', help = 'Check releases of a package given a package name.')

    parser.add_argument('--channel', '-c', action = ChannelAdd, dest = 'channels', help = 'Add Conda channel')

    args = parser.parse_args()


if (__name__ == '__main__'):
    main()
