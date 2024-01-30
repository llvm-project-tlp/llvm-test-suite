#!/usr/bin/env python3
#
# Analyze the static test configurations and print some aggregate statistics
# about them.

import argparse as ap
import os
import re

# The object containing the passed command line options. This will be set when
# the command line arguments are parsed.
g_opts = None

# The known test kinds.
kinds = ['preprocess', 'compile', 'assemble', 'link', 'run']

# The reasons for disabling a test.
reasons = ['unsupported', 'unimplemented', 'skipped', 'failing']

# Regular expressions to identify the disabled lists.
re_unsupported = re.compile('file[ ]*[(][ ]*GLOB[ ]+UNSUPPORTED_FILES')
re_unimplemented = re.compile('file[ ]*[(][ ]*GLOB[ ]+UNIMPLEMENTED_FILES')
re_skipped = re.compile('file[ ]*[(][ ]*GLOB[ ]+SKIPPED_FILES')
re_failing = re.compile('file[ ]*[(][ ]*GLOB[ ]+FAILING_FILES')

# Get an empty stats object.
def get_stats():
    stats = {}
    for k in kinds:
        stats[k] = 0
    for r in reasons:
        stats[r] = set([])
    stats['tests'] = []

    return stats

# Parse a single test into a dictionary. Only the fields that we care about
# will be parsed.
def parse_test(line):
    test = {}
    fields = line.split(';')
    test['kind'] = fields[0]
    test['main'] = fields[1].split(' ')[0]

    return test

# Parse the static test configuration in the given directory and accumulate the
# stats into the provided dictionary.
def parse_test_config(filename, stats):
    with open(filename) as f:
        for l in f:
            line = l.strip()
            if line.startswith('#'):
                continue

            test = parse_test(line)
            kind = test['kind']
            stats[kind] += 1
            stats['tests'].append(test)

# Parse the disabled files file and collect the names of the disabled files.
def parse_disabled_files(filename, stats):
    def strip_comments(s):
        idx = s.find('#')
        if idx != -1:
            return s[:idx]
        return s

    with open(filename) as f:
        collect = None
        for l in f:
            line = l.strip()
            if line.startswith('#'):
                continue
            line = strip_comments(line)
            if not line:
                continue

            if re_unsupported.search(line):
                collect = 'unsupported'
            elif re_unimplemented.search(line):
                collect = 'unimplemented'
            elif re_skipped.search(line):
                collect = 'skipped'
            elif re_failing.search(line):
                collect = 'failing'
            elif line.endswith(')'):
                collect = None
            elif collect:
                for t in line.split(' '):
                    if t:
                        stats[collect].add(t)

def parse_commandline():
    parser = ap.ArgumentParser(
        description = 'Analyze the build files in the gfortran test suite and '
        'print statistics about the number of tests, their kind, and '
        'those that are disabled'
    )
    parser.add_argument(
        '-a',
        '--all',
        action = 'store_true',
        help = 'Print all fields, even if their value is 0'
    )
    parser.add_argument(
        '-d',
        '--per-directory',
        action = 'store_true',
        help = 'Print per-directory statistics as well'
    )
    parser.add_argument(
        'dir',
        nargs = '?',
        default = os.path.dirname(os.path.dirname(__file__)),
        help = 'The top-level directory containing the gfortran tests. If this '
        'is not provided, the parent of the directory containing this script '
        'used'
    )

    return parser.parse_args()

def printf(fmt, *args):
    print(fmt.format(*args))

def main():
    global g_opts

    g_opts = parse_commandline()

    root = g_opts.dir
    res = {}
    subdirs = sorted([t[0] for t in os.walk(root)])
    for d in subdirs:
        res[d] = get_stats()
        test_config = os.path.join(d, 'tests.cmake')
        if os.path.exists(test_config):
            parse_test_config(test_config, res[d])
            disabled_config = os.path.join(d, 'DisabledFiles.cmake')
            if os.path.exists(disabled_config):
                parse_disabled_files(disabled_config, res[d])

    if g_opts.per_directory:
        for d in subdirs:
            stats = res[d]
            if not stats['tests']:
                continue

            label = d.replace(root, '')
            if label.startswith('/') or label.startswith('\\'):
                label = label[1:]

            print(label)
            printf('  {:16} {}', 'tests', sum([stats[k] for k in kinds]))
            for k in kinds:
                if stats[k] or g_opts.all:
                    printf('    {:14} {}', k, stats[k])

            disabled = sum([len(stats[r]) for r in reasons])
            if disabled or g_opts.all:
                printf('  {:16} {}', 'disabled', disabled)
                for r in reasons:
                    if stats[r] or g_opts.all:
                        printf('    {:14} {}', r, len(stats[r]))

            print()

    print('Test suite')
    printf(
        '  {:16} {}',
        'tests',
        sum([len(stats['tests']) for stats in res.values()])
    )
    for k in kinds:
        val = sum([stats[k] for stats in res.values()])
        if val or g_opts.all:
            printf('    {:14} {}', k, val)
    disabled = sum(
        sum([len(stats[r]) for r in reasons]) for stats in res.values()
    )
    if disabled or g_opts.all:
        printf('  {:16} {}', 'disabled', disabled)
        for r in reasons:
            val = sum([len(stats[r]) for stats in res.values()])
            if val or g_opts.all:
                printf('    {:14} {}', r, val)

if __name__ == '__main__':
    exit(main())
