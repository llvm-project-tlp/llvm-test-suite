#!/usr/bin/env python3
#
# Run all the disabled tests in the gfortran test suite and re-enable those that
# pass.
#
# USAGE
#
#     update-disabled-tests [options] <path>
#
# ARGUMENTS
#
#     <path>    Path to the top-level directory of the LLVM test suite.
#

import argparse
import glob
import json
import os
import re
import shutil
import subprocess
import tempfile

def parse_cmdline_args():
    ap = argparse.ArgumentParser(
        prog = 'update-disabled-tests',
        description =
        'Run all disabled tests in the gfortran test suite and remove any that '
        'pass from the list of disabled tests',
    )
    ap.add_argument(
        '-b',
        '--build-dir',
        metavar = '<dir>',
        help = 'The build directory to use'
    )
    ap.add_argument(
        '-c',
        '--clean',
        default = False,
        action = 'store_true',
        help = 'If a build directory has been specified, delete everything in '
        'it. If this option is not provided, and the build directory is not '
        'empty, an error will be raised.'
    )
    ap.add_argument(
        '-e',
        '--existing',
        default = False,
        action = 'store_true',
        help = 'Don\'t run the tests. Only process existing test results.'
    )
    ap.add_argument(
        '-i',
        '--inplace',
        default = False,
        action = 'store_true',
        help = 'Rewrite all DisabledFiles.cmake files. The original files will '
        'be saved as DisabledFiles.cmake.bak'
    )
    ap.add_argument(
        '-j',
        '--parallel',
        metavar = 'N',
        type = int,
        default = 1,
        help = 'The number of parallel threads to use when running the tests'
    )
    ap.add_argument(
        '--keep',
        default = False,
        action = 'store_true',
        help = 'Do not delete the build directory after building and running '
        'the tests'
    )
    ap.add_argument(
        '-n',
        '--dry-run',
        default = False,
        action = 'store_true',
        help = 'Only print the commands that will be executed. Do not make any '
        'directories or build/run any tests'
    )
    ap.add_argument(
        '-v',
        '--verbose',
        default = False,
        action = 'store_true',
        help = 'Enable verbose mode'
    )
    ap.add_argument(
        '--with-cmake',
        metavar = '<path>',
        type = str,
        default = 'cmake',
        dest = 'cmake',
        help = 'Path to cmake'
    )
    ap.add_argument(
        '--with-clang',
        metavar = '<path>',
        type = str,
        default = 'clang',
        dest = 'clang',
        help = 'Path to clang'
    )
    ap.add_argument(
        '--with-flang',
        metavar = '<path>',
        type = str,
        default = 'flang',
        dest = 'flang',
        help = 'Path to flang'
    )
    ap.add_argument(
        '--with-make',
        metavar = '<path>',
        type = str,
        default = 'make',
        dest = 'make',
        help = 'Path to make'
    )
    ap.add_argument(
        '--with-lit',
        metavar = '<path>',
        type = str,
        default = 'lit',
        dest = 'lit',
        help = 'Path to LLVM lit'
    )
    ap.add_argument(
        'source',
        metavar = '<source>',
        help = 'Path to the top-level source directory of the LLVM test suite',
    )

    return ap.parse_args()

# Parse a file containing the disabled tests. For now, we only care about
# the unimplemented (tests that are disabled because they trigger a "not yet
# implemented" assertion), and skipped (tests that are skipped because they
# fail without hitting any todo's or other assertions) list. The unsupported
# list is irrelevant and the failing list needs a lot of additional processing
# since the tests in that list fail for a variety of reasons.
# { str : *}, os.path -> [str]
def parse_disabled_file(args, filename):
    if args.verbose or args.dry_run:
        print('Parsing disabled tests file:', filename)
    if args.dry_run:
        return []

    re_unimplemented = re.compile('^[ ]*file[ ]*[(][ ]*GLOB[ ]+UNIMPLEMENTED.+$')
    re_skipped = re.compile('^[ ]*file[ ]*[(][ ]*GLOB[ ]+SKIPPED.+$')
    re_comment = re.compile('^[ ]*#.*$')
    re_close = re.compile('^[ ]*[)][ ]*$')

    record = False
    tests = []
    with open(filename) as f:
        for line in f:
            if re_comment.match(line):
                pass
            elif re_unimplemented.match(line):
                record = True
            elif re_skipped.match(line):
                record = True
            elif re_close.match(line):
                record = False
            elif line.endswith(')'):
                tests.append(line[:-1].strip())
                record = False
            elif record:
                tests.append(line.strip())
    return tests

# Build the cmake command for the given configuration. config must be either
# 'default' or 'all'. build_dir must be build directory for the configuration.
# { str : * }, os.path, str -> str
def get_configure_command(args, build_dir, config):
    return f'{args.cmake} ' \
        f'-B "{build_dir}" ' \
        f'-S "{args.source}" ' \
        f'-DCMAKE_C_COMPILER="{args.clang}" ' \
        f'-DCMAKE_CXX_COMPILER="{args.clang}++" ' \
        f'-DCMAKE_Fortran_COMPILER="{args.flang}" ' \
        f'-DTEST_SUITE_FORTRAN=ON ' \
        f'-DTEST_SUITE_SUBDIRS=Fortran/gfortran ' \
        f'-DTEST_SUITE_FORTRAN_FORCE_ALL_TESTS={"OFF" if config == "default" else "ON"}'

# Build the make command. build_dir must be the build directory for a specific
# configuration. config must be either 'default' or 'all'.
# { str: * }, os.path, str -> str
def get_build_command(args, build_dir, config):
    cmd = [args.make, '-C', build_dir, '-j', str(args.parallel)]
    # When building all tests, some may fail at build time because the flang may
    # crash. We want to keep going in this case.
    if config == 'all':
        cmd.append('--ignore-errors')

    return ' '.join(cmd)

# Build the run command for the given configuration. config must be either
# 'default' or 'all'. build_dir must be the build directory for the
# configuration.
# { str : * }, os.path -> str
def get_run_command(args, build_dir, config):
    build_root = os.path.dirname(build_dir)
    # Write the report to the top-level build directory.
    return f'{args.lit}' \
        f' -j {args.parallel} ' \
        f' -o "{build_root}/{config}.json" '\
        f' {build_dir}/Fortran/gfortran'

# Create a subdirectory within the build directory for the specified
# configuration. config must be either 'default' or 'all'. The subdirectory must
# not already exist.
# { str : * }, os.path, str -> os.path
def setup_build_dir_for_configuration(args, build_dir, config):
    if args.verbose or args.dry_run:
        print('Making build directory for configuration:', config)

    d = os.path.join(build_dir, config)
    if not args.dry_run:
        if os.path.exists(d):
            print(
                f'ERROR: Build directory for configuration \'{config}\' exists'
            )
            exit(1)
        if not args.dry_run:
            os.mkdir(d)

    if args.verbose or args.dry_run:
        print('Using build directory:', d)
    return d

# Check if the build directory is empty. Empty it if so instructed, raise an
# error and exit otherwise.
# { str : * }, os.path -> None
def prepare_build_dir(args, build_dir):
    contents = os.listdir(build_dir)
    if len(contents) == 0:
        return

    if not args.clean:
        print('ERROR: Build directory is not empty:', build_dir)
        exit(1)

    if args.verbose or args.dry_run:
        print('Deleting contents of build directory:', build_dir)

    if not args.dry_run:
        for f in contents:
            shutil.rmtree(f)

# Setup the build directory. This will create a temporary build directory if
# a build directory was not explicitly specified. If a build directory was
# explicitly specified, it is expected to exist.
# { str : * } -> os.path
def setup_build_dir(args):
    if args.build_dir:
        d = os.path.abspath(args.build_dir)
        if not os.path.exists(d):
            print('ERROR: Build directory does not exist:', d)
            exit(1)
        prepare_build_dir(args, d)
    else:
        d = tempfile.mkdtemp()
        if not os.path.exists(d):
            if args.verbose or args.dry_run:
                print('Making temporary build directory:', d)
            if not args.dry_run:
                os.mkdir(d)

    if args.verbose or args.dry_run:
        print('Using build directory:', d)

    return d

# Teardown the build directory if necessary. If the --keep option was not
# specified and a temporary build directory was created, it will be deleted
# along with all its contents. If an explicit build directory was specified, it
# will not be deleted.
# { str : * } -> None
def teardown_build_dir(args, d):
    if not args.build_dir and not args.keep:
        if args.verbose or args.dry_run:
            print('Removing build directory:', d)
        if not args.dry_run:
            shutil.rmtree(d)

# Build and run the tests using the given commands. Return the process' return
# code. build_root is the top-level build directory. config must be either
# 'default' or 'all'.
# { str : * }, os.path, str -> None
def build_and_run_tests(args, build_root, config):
    build_dir = setup_build_dir_for_configuration(args, build_root, config)
    configure = get_configure_command(args, build_dir, config)
    build = get_build_command(args, build_dir, config)
    run = get_run_command(args, build_dir, config)

    if args.verbose or args.dry_run:
        print(configure)
    if not args.dry_run:
        if subprocess.run(configure, shell = True).returncode != 0:
            print('ERROR: Error configuring test suite')
            exit(1)

    if args.verbose or args.dry_run:
        print(build)
    if not args.dry_run:
        if subprocess.run(build, shell = True).returncode != 0:
            # When building all the tests, we may encounter errors because flang
            # may crash. We want to keep going regardless.
            if config != 'all':
                print('ERROR: Error building test suite')
                exit(1)

    if args.verbose or args.dry_run:
        print(run)
    if not args.dry_run:
        ret = subprocess.run(run, cwd = build_dir, shell = True)
        # The default configuration is expected to pass. If it doesn't,
        # something is wrong. Don't proceed any further. The 'all' configuration
        # is expected to fail, so just ignore the return code there.
        if ret.returncode != 0 and config != 'all':
            print(
                'ERROR: Some test(s) in the default configuration failed. '
                'This is not expected'
            )
            exit(1)

# Parse the test results. The result is a map whose key is the absolute path
# to the main test file and the value is a boolean indicating whether the test
# passed or failed. build_root is the root of the build directory. config must
# be either 'default' or 'all'.
# { str : * }, os.path, str -> { os.path : bool }
def parse_test_results(args, build_root, config):
    if args.verbose or args.dry_run:
        print(f'Parsing test results for ${config} configuration')
    if args.dry_run:
        return {}

    j = None
    with open(os.path.join(build_root, config + '.json')) as f:
        j = json.load(f)

    results = {}
    for tj in j['tests']:
        name = tj['name'].split('::')[1].strip()
        elems = name.split('/')
        dirs = elems[:-1]
        filename = elems[-1]

        filename = filename.replace('gfortran-regression-', '')
        filename = filename.replace('gfortran-torture-', '')
        if dirs[2] == 'regression':
            filename = filename.replace('compile-regression', '')
            filename = filename.replace('execute-regression', '')
        elif dirs[2] == 'torture':
            filename = filename.replace('compile-torture', '')
            filename = filename.replace('execute-torture', '')
        for d in dirs[3:]:
            filename = filename.replace('__' + d, '', 1)
        filename = filename[2:-5]

        base, _, ext = filename.rpartition('_')
        fname = '.'.join([base, ext])
        # The tests in regression/gomp/appendix-a contain .'s in the name which
        # are replaced with _'s in the test name.
        if dirs[-1] == 'appendix-a':
            fname = fname.replace('_', '.')

        f = os.path.join(args.source, *dirs, fname)
        if os.path.exists(f):
            results[fname] = tj['code'] == 'PASS'

    return results

# Compare the test results and get the list of tests to be enabled. The result
# will be a list of paths to tests that should be enabled. build_root is the
# root of the build directory.
# { str : * }, os.path -> [os.path]
def get_tests_to_be_enabled(args, build_root):
    results_def = parse_test_results(args, build_root, 'default')
    results_all = parse_test_results(args, build_root, 'all')
    # TODO: Implement this.
    return []

# Update the DisabledFiles.cmake files based on the tests that were disabled
# but should now be enabled.
# { str : * }, [os.path] -> None
def update_disabled_lists(args, enabled_tests):
    # TODO: Implement this.
    pass

def main():
    args = parse_cmdline_args()

    # Parse disabled files lists.
    check_disabled = {}
    pattern = os.path.join(args.source, '**/DisabledFiles.cmake')
    for filename in glob.iglob(pattern, recursive=True):
        d = os.path.dirname(filename)
        check_disabled[d] = []
        for test in parse_disabled_file(args, filename):
            check_disabled[d].append(os.path.join(d, test))

    build_dir = setup_build_dir(args)

    if not args.existing:
        build_and_run_tests(args, build_dir, 'default')
        build_and_run_tests(args, build_dir, 'all')

    enabled = get_tests_to_be_enabled(build_dir)
    if args.verbose or args.dry_run:
        print(f'Enabling {len(enabled)} tests')
        for test in enabled:
            print('   ', test)
    if not args.dry_run:
        update_disabled_lists(args, enabled)

    # Cleanup, if necessary.
    teardown_build_dir(args, build_dir)

if __name__ == '__main__':
    main()
