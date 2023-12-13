#!/usr/bin/env python3

import chardet
import os
import re

# Class representing a single test.
class Test:
    UNKNOWN = 0
    PREPROCESS = 1
    COMPILE = 2
    LINK = 3
    RUN = 4

    # int, [os.path], [str], [str], bool
    def __init__(self, kind, sources, options, targets, expected_fail):
        self.kind = kind

        # The sources needed by the test. This will have at least one element.
        # The first element of the list will be the "main" file. The rest must
        # be in the order in which they should be compiled. The elements will be
        # the basename's of the file because all dependent files are in the
        # same directory, so there is no need to have the full (or relative)
        # path.
        self.sources = sources

        # The command-line options needed by the test.
        self.options = options

        # The optional targets for the test.
        self.targets = targets

        # Whether the test is expected to fail.
        self.expected_fail = expected_fail

        # Whether to use separate compilation for this test (is this even
        # necessary?)
        self.separate_compilation = False

    def __str__(self):
        m = ['', 'preprocess', 'compile', 'link', 'run']
        elems = []
        elems.append(m[self.kind])
        elems.extend(self.sources)
        if self.options:
            elems.extend(['options'])
        return ' '.join(elems)

# Checks if the basename of a file has a Fortran extension.
re_fortran = re.compile('^.+[.][Ff].*$')

# Checks if the line has a preprocess annotation.
re_preprocess = re.compile('[{][ ]*dg-do preprocess[ ]*[}]')

# Checks if the line has a compile annotation.
# FIXME: Add match for target
re_compile = re.compile('[{][ ]*dg-do[ ]*compile[ ]*(.*)[ ]*[}]')

# Checks if the line has a link annotation.
re_link = re.compile('[{][ ]*dg-do[ ]*link[ ]+(.*)[ ]*[}]')

# Checks if the line has a run annotation or lto-run annotation.
# FIXME: Add match for target
re_run = re.compile('[{][ ]*dg-(lto-)?do[ ]*run[ ]+(.*)[ ]*[}]')

# Checks if the line has an additional-sources annotation.
re_sources = re.compile('[{][ ]*dg-additional-sources[ ]*(.+)[ ]*[}]')

# Checks if the line has a dg-compile-aux-modules annotation.
re_aux_modules = re.compile('[{][ ]*dg-compile-aux-modules[ ]*(.+)[ ]*[}]')

# Checks if the line has an options or additional-options annotation. The
# option may have an optional target.
re_options = re.compile(
    '[{][ ]*dg-(additional-)?options[ ]*(.+)[ ]*[}][ ]*'
    '([{][ ]*target[ ]*(.+)?[ ]*[}])?'
)

# Checks if the line has a shouldfail annotation.
re_shouldfail = re.compile('[{][ ]*dg-shouldfail[ ]*.*[}]')

# Checks if the line has a dg-error annotation.
# TODO: There may be
re_error = re.compile('[{][ ]*dg-error[ ]*[}]')

# Get the n-th level ancestor of the given file. The 1st level ancestor is
# the directory containing the file. The 2nd level ancestor is the parent of
# that directory and so on.
# os.path, int -> os.path
def get_ancestor(f, n):
    anc = f
    for _ in range(0, n):
        anc = os.path.dirname(anc)
    return anc

# Get the encoding of the file.
# os.path -> str
def get_encoding(filepath):
    with open(filepath, 'rb') as f:
        return chardet.detect(f.read())['encoding']
    return None

# Get the lines in the file.
# os.path -> [str]
def get_lines(filepath):
    lines = []
    try:
        with open(filepath, 'r', encoding = get_encoding(filepath)) as f:
            lines = f.readlines()
    except:
        print('  WARNING: Could not open file:', os.path.basename(filepath))
    finally:
        return lines

# Collect the subdirectories of the gfortran directory which may contain tests.
# os.path -> [os.path]
def get_subdirs(gfortran):
    regression = os.path.join(gfortran, 'regression')
    torture = os.path.join(gfortran, 'torture')

    subdirs = [regression]
    for root, dirs, _ in os.walk(regression):
        subdirs.extend([os.path.join(root, d) for d in dirs])
    subdirs.append(torture)
    for root, dirs, _ in os.walk(torture):
        subdirs.extend([os.path.join(root, d) for d in dirs])
    return subdirs

# Strip any leading and trailing whitespace from the string as well as any
# optional quotes around the string. Then split the string on whitespace and
# return the resulting list.
# str -> list[str]
def qsplit(s):
    s = s.strip()
    if s.startswith('"'):
        s = s[1:]
    if s.endswith('"'):
        s = s[:-1]
    return s.split()

# Try to match the line with the regex. If the line matches, add the match
# object to the MOUT list and return True. Otherwise, leave the MOUT list
# unchanged and return False.
# re, str, [re.MATCH] -> bool
def try_match(regex, line, mout):
    m = regex.search(line)
    if m:
        mout.append(m)
        return True
    return False

# Count the number of elements in the list that match satisfy the predicate.
def count_if(l, predicate):
    return sum(1 for e in l if predicate(e))

# Count the number of tests in the list that have the given kind.
def count_if_kind(tests, kind):
    return count_if(tests, lambda t: t.kind == kind)

# () -> int
def main():
    root = get_ancestor(os.path.realpath(__file__), 4)
    gfortran = os.path.join(root, 'Fortran', 'gfortran')
    subdirs = get_subdirs(gfortran)

    all_tests = []
    for subdir in subdirs:
        files = []
        for e in os.scandir(subdir):
            if e.is_file() and re_fortran.match(e.name):
                files.append(e.path)
        if not files:
            continue

        # Find all the files that are dependencies of some file that is the
        # main file in a test.
        dependencies = set([])
        for filename in files:
            for l in get_lines(filename):
                mout = []
                if try_match(re_sources, l, mout) or \
                   try_match(re_aux_modules, l, mout):
                    for m in mout:
                        for src in qsplit(m[1]):
                            dependencies.add(src)

        print(subdir)
        tests = []
        missing_action = []
        for f in files:
            filename = os.path.basename(f)
            if filename in dependencies:
                continue

            kind = None
            sources = [filename]
            options = []
            targets = []
            expect_error = False

            for l in get_lines(f):
                mout = []
                if try_match(re_preprocess, l, mout):
                    kind = Test.PREPROCESS
                elif try_match(re_compile, l, mout):
                    kind = Test.COMPILE
                    # TODO: Handle the optional target.
                elif try_match(re_link, l, mout):
                    kind = Test.LINK
                    # TODO: Handle the optional target.
                elif try_match(re_run, l, mout):
                    kind = Test.RUN
                    # TODO: Does lto-run need to be handled differently?
                    # TODO: Handle the optional target.
                elif try_match(re_shouldfail, l, mout) or \
                     try_match(re_error, l, mout):
                    expect_error = True
                elif try_match(re_sources, l, mout) or \
                     try_match(re_aux_modules, l, mout):
                    m = mout[0]
                    sources.extend(qsplit(m[1]))
                elif try_match(re_options, l, mout):
                    m = mout[0]
                    options.extend(qsplit(m[2]))
                    # TODO: Handle the optional target.

            # If the kind is missing, assume that it is a compile test except
            # for torture/execute where it is an execute test.
            anc1 = os.path.basename(get_ancestor(f, 1))
            anc2 = os.path.basename(get_ancestor(f, 2))
            if not kind:
                if anc2 == 'torture' and anc1 == 'execute':
                    kind = Test.RUN
                else:
                    kind = Test.COMPILE

            fmt = '    WARNING: {} without action annotation: {}'
            if kind:
                test = Test(kind, sources, options, targets, expect_error)
                tests.append(test)
            elif len(sources) > 1:
                missing_action.append(filename)
                print(fmt.format('Additional sources', filename))
            elif len(options) > 1:
                missing_action.append(filename)
                print(fmt.format('Compile options', filename))
            elif expect_error:
                missing_action.append(filename)
                print(fmt.format('Expect error', filename))
            else:
                missing_action.append(filename)
                print('    WARNING: No action annotation:', filename)

        # Count the fortran files in the tests. Eventually, we want to ensure
        # that all the fortran files are accounted for
        accounted = set([])
        for test in tests:
            for s in test.sources:
                if re_fortran.match(s):
                    accounted.add(s)
        filenames = set([os.path.basename(f) for f in files])
        unaccounted = filenames - set(accounted) - set(missing_action)

        print('  files:', len(files))
        if len(unaccounted):
            print('    unaccounted:', sorted(unaccounted))
        print('  tests:', len(tests))
        print('    preprocess:', count_if_kind(tests, Test.PREPROCESS))
        print('    compile:', count_if_kind(tests, Test.COMPILE))
        print('    link:', count_if_kind(tests, Test.LINK))
        print('    run:', count_if_kind(tests, Test.RUN))
        print('    unknown:', len(missing_action))

        tests.sort(key=lambda t: (t.kind, t.sources[0].lower()))
        print()
        for test in tests:
            print(' ', test)

        all_tests.extend(tests)

    print('\nTEST SUITE')
    print('tests:', len(all_tests))
    print('  preprocess:', count_if_kind(all_tests, Test.PREPROCESS))
    print('  compile:', count_if_kind(all_tests, Test.COMPILE))
    print('  link:', count_if_kind(all_tests, Test.LINK))
    print('  run:', count_if_kind(all_tests, Test.RUN))

if __name__ == '__main__':
    exit(main())
