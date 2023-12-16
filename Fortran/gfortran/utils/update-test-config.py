#!/usr/bin/env python3

import argparse
import chardet
import os
from re import compile
import shutil
from typing import List

# Class representing a single test. The fields of the test should be those that
# are eventually serialized into the test configuration. The configuration will
# only contain the test kind, the sources and flags that indicate what DejaGNU
# annotations are present in the test file.
class Test:
    # int, [os.path], [str], [str], bool
    def __init__(
        self,
        kind: str,
        sources: List[str],
        options: List[str],
        targets: List[str],
        expected_fail: bool
    ):
        # The kind of the test. This must be one of 'preprocess', 'assemble',
        # 'compile', 'link' or 'run'.
        self.kind: str = kind

        # The sources needed by the test. This will have at least one element.
        # The first element of the list will be the "main" file. The rest must
        # be in the order in which they should be compiled. The elements will be
        # the basename's of the file because all dependent files are in the
        # same directory, so there is no need to have the full (or relative)
        # path.
        self.sources: List[str] = sources

        # The command-line flags that are needed to build the test.
        #
        # FIXME: Currently, only the flags from the main file in multi-file
        # tests are recorded. This might need to be fixed.
        self.options: List[str] = options

        # The optional targets for the test. The targets annotation can be
        # fairly complex with both wildcards and conditional operations, but
        # we will probably only ever handle "simple" targets.
        #
        # FIXME: This is currently not used because we do not yet support
        # handling the target annotations.
        self.targets: List[str] = targets

        # Whether the test is expected to fail. For run tests, this indicates
        # the presence of a shouldfail annotation. For all other test kinds,
        # a dg-error annotation is present somewhere in the file. In the latter
        # case, the error may only manifest on certain targets, but that should
        # have been captured in the self.targets member of this class.
        self.xfail: bool = expected_fail

        # Whether to use separate compilation for this test (is this even
        # necessary?)
        self.separate_compilation = False

    def __eq__(self, other):
        if not isinstance(other, Test):
            return NotImplemented

        return self.kind == other.kind and \
            self.sources == other.sources and \
            self.options == other.options and \
            self.xfail == other.xfail and \
            self.targets == other.targets

    # The string-ified test is in comma-separated because that's all we need
    # from this.
    def __str__(self):
        return ';'.join([
            self.kind,
            ' '.join(self.sources),
            'xfail' if self.xfail else '',
            ' '.join(self.options),
            ' '.join(self.targets)
        ])

# The strings containing regexes which will be compiled later.
pfx = '[{][ ]*'
sfx = '[ ]*[}]'

# In DejaGNU, braces can be used instead of quotes ... I think.
res = '[{]?[ ]*(.+?)[ ]*[}]?'

# The target is always optional
tgt = f'({pfx}target[ ]*(.+){sfx})?'

re_btxt = compile('[{][ ]*(.+?)[ ]*[}]')
re_fortran = compile('^.+[.][Ff].*$')
re_assemble = compile(f'{pfx}dg-(lto-)?do[ ]*assemble{sfx}')
re_preprocess = compile(f'{pfx}dg-do[ ]*preprocess{sfx}')
re_compile = compile(f'{pfx}dg-do[ ]*compile[ ]*{tgt}{sfx}')
re_link = compile(f'{pfx}dg-(lto-)?do[ ]*link[ ]*(.*){sfx}')
re_run = compile(f'{pfx}dg-(lto-)?do[ ]*run[ ]*{tgt}{sfx}')
re_sources = compile(f'{pfx}dg-additional-sources[ ]*{res}{sfx}')
re_aux_modules = compile(f'{pfx}dg-compile-aux-modules[ ]*{res}{sfx}')
re_opts = compile(f'{pfx}dg-options[ ]*{res}[ ]*{tgt}{sfx}')
re_addnl_opts = compile(f'{pfx}dg-additional-options[ ]*{res}[ ]*{tgt}{sfx}')
re_lto_opts = compile(
    f'{pfx}dg-lto-options[ ]*'
    f'[{{][ ]*({pfx}.+?{sfx}[ ]*)[ ]*[}}][ ]*'
    f'{tgt}{sfx}'
)
re_ld_opts = compile(f'{pfx}dg-extra-ld-options[ ]*{res}{sfx}')
re_shouldfail = compile(f'{pfx}dg-shouldfail[ ]*.*{sfx}')
re_error = compile(f'{pfx}dg-error[ ]*.*{tgt}{sfx}')

# The options governing the overall behavior of this script. This will be set
# once the command line arguments have been parsed.
g_opts = None

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
        encoding = get_encoding(filepath)
        with open(filepath, 'r', encoding = encoding) as f:
            lines = f.readlines()
    except:
        warning('Could not open file: {}', os.path.basename(filepath))
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

# Print a message in verbose mode.
# str, * -> None
def message(fmt, *args):
    global g_opts
    if g_opts.verbose:
        print(fmt.format(*args))

# Print a warning message.
# str, * => None
def warning(fmt, *args):
    print('WARNING:', fmt.format(*args))

# Print an error message and exit.
# str, * => None
def error(fmt, *args):
    print('ERROR:', fmt.format(*args))
    exit(1)

# Print a message. This is only around to save a bit of typing.
# str, * => None
def printf(fmt, *args):
    print(fmt.format(*args))

# Collect the tests in a given directory.
# os.path -> [Test]
def collect_tests(d):
    global g_opts
    if not g_opts.quiet:
        print(d)

    tests = []
    files = []
    for e in os.scandir(d):
        if e.is_file() and re_fortran.match(e.name):
            files.append(e.path)
    message('Found {} Fortran files', len(files))

    if not len(files):
        if not g_opts.quiet:
            print()
        return tests

    # Some files cannot be read because they are invalid UTF-16. Just handle
    # those as a special case here. This is a really ugly way of doing things
    # but this script is only intended for occasional use, so I am not too
    # bothered about this.
    remove = []
    for f in files:
        if f.endswith('regression/bom_error.f90'):
            tests.append(Test('compile', [os.path.basename(f)], [], [], True))
            remove.append(f)
    for f in remove:
        files.remove(f)
    if len(remove):
        message(
            'Filter known problematic files: {}\n  {}',
            len(remove),
            '  \n'.join([os.path.basename(f) for f in remove])
        )

    # Find all the files that are dependencies of some file that is the
    # main file in a test.
    dependents = set([])
    for filename in files:
        for l in get_lines(filename):
            mout = []
            if try_match(re_sources, l, mout) or \
               try_match(re_aux_modules, l, mout):
                for m in mout:
                    for src in qsplit(m[1]):
                        dependents.add(src)
    message('Found {} dependent files', len(dependents))

    for f in files:
        filename = os.path.basename(f)
        if filename in dependents:
            continue

        kind = None
        sources = [filename]
        options = []
        targets = []
        xfail = False

        for l in get_lines(f):
            mout = []
            if try_match(re_assemble, l, mout):
                kind = 'assemble'
            elif try_match(re_preprocess, l, mout):
                kind = 'preprocess'
            elif try_match(re_compile, l, mout):
                kind = 'compile'
                # TODO: Handle the optional target.
            elif try_match(re_link, l, mout):
                kind = 'link'
                # TODO: Handle the optional target.
            elif try_match(re_run, l, mout):
                kind = 'run'
                # TODO: Does lto-run need to be handled differently?
                # TODO: Handle the optional target.
            elif try_match(re_shouldfail, l, mout) or \
                 try_match(re_error, l, mout):
                xfail = True
            elif try_match(re_sources, l, mout) or \
                 try_match(re_aux_modules, l, mout):
                m = mout[0]
                sources.extend(qsplit(m[1]))
            elif try_match(re_opts, l, mout) or \
                 try_match(re_addnl_opts, l, mout) or \
                 try_match(re_ld_opts, l, mout):
                m = mout[0]
                options.extend(qsplit(m[1]))
                # TODO: Handle the optional target.
            elif try_match(re_lto_opts, l, mout):
                m = mout[0]
                # FIXME: There are two sets of options in some files. It is
                # possible that an arbitrary number of these is allowed, but I
                # don't know exactly what it is for, so for now, just use the
                # first set.
                options.extend(qsplit(re_btxt.findall(m[1])[0]))
                # TODO: Handle the optional target

        # If the kind is missing, assume that it is a compile test except
        # for torture/execute where it is an execute test.
        anc1 = os.path.basename(get_ancestor(f, 1))
        anc2 = os.path.basename(get_ancestor(f, 2))
        if not kind:
            if anc2 == 'torture' and anc1 == 'execute':
                kind = 'run'
            else:
                kind = 'compile'

        tests.append(Test(kind, sources, options, targets, xfail))

    # Count the fortran files in the tests. Eventually, we want to ensure
    # that all the fortran files are accounted for
    accounted = set([])
    for test in tests:
        for s in test.sources:
            if re_fortran.match(s):
                accounted.add(s)
    filenames = set([os.path.basename(f) for f in files])
    orphans = filenames - set(accounted)
    if len(orphans):
        error('{} orphan files found\n  {}', len(orphans), '  \n'.join(orphans))

    order = {'preprocess': 0, 'assemble': 1, 'compile': 2, 'link': 3, 'run': 4}
    tests.sort(key = lambda t: (order[t.kind], t.sources[0].lower()))

    return tests

# Parse tests from the given file
# os.path -> [Test]
def parse_tests(filename):
    tests = []
    with open(filename, 'r') as f:
        for lno, l in enumerate(f.readlines()):
            line = l.strip()

            # Lines starting with a # are comment lines.
            if not line or line.startswith('#'):
                continue

            # The format of each non-comment line is specified at the start of
            # this file.
            elems = l.split(';')
            if len(elems) != 5:
                error('{}:{}: Unexpected number of elements', filename, lno + 1)
            if elems[2] not in ['', 'xfail']:
                error(
                    '{}:{}: Expected error field must be xfail or empty',
                    filename,
                    lno + 1
                )

            kind = elems[0]
            sources = elems[1].split(' ')
            xfail = True if elems[2] == 'xfail' else False
            options = elems[3].split(' ')
            targets = elems[4].split(' ')

            test = Test(kind, sources, options, targets, xfail)
            tests.append(test)

    return tests

# Setup the argument parser and return it.
def get_argument_parser():
    ap = argparse.ArgumentParser(
        description =
        'Update the static test configuration files in the gfortran tests '
        'within the LLVM test suite.',
        epilog = ' This is intended to be used to update the '
        'configuration files within the repository in which this script is '
        'contained. An optional list of directories can be provided as well '
        'which may live in a different location.'
    )

    ap.add_argument(
        '-i',
        '--inplace',
        default = False,
        action = 'store_true',
        help = 'update the test configuration in-place without backing it up '
    )

    grp = ap.add_mutually_exclusive_group()
    grp.add_argument(
        '-q',
        '--quiet',
        default = False,
        action = 'store_true',
        help = 'do not print summaries of tests found and updated'
    )
    grp.add_argument(
        '-v',
        '--verbose',
        default = False,
        action = 'store_true',
        help = 'enable verbose mode'
    )

    ap.add_argument(
        'dirs',
        metavar = 'dir',
        default = None,
        nargs = '*',
        help = 'the directories in which to update the test configuration. '
        'If not provided, all directories in the gfortran test suite will be '
        'updated.'
    )

    return ap

# () -> int
def main():
    global g_opts

    ap = get_argument_parser()
    g_opts = ap.parse_args()

    dirs = g_opts.dirs
    if not dirs:
        root = get_ancestor(os.path.realpath(__file__), 4)
        gfortran = os.path.join(root, 'Fortran', 'gfortran')
        dirs = get_subdirs(gfortran)

    all_tests = {}
    for d in dirs:
        tests = collect_tests(d)
        if not tests:
            continue

        existing = []
        config_file = os.path.join(d, 'tests.cmake')
        if os.path.exists(config_file):
            message('Backing up test configuration')
            existing = parse_tests(config_file)
            if not g_opts.inplace:
                shutil.move(config_file, config_file + '.bak')
        else:
            message('Test configuration not found')

        message('Writing test configuration')
        with open(config_file, 'w') as f:
            f.write('# This file was generated by update-test-config\n')
            f.write('#\n')
            f.write('\n'.join([str(t) for t in tests]))

        if not g_opts.quiet:
            printf('{:16}{}', 'Found tests', len(tests))
            for k in ['preprocess', 'assemble', 'compile', 'link', 'run']:
                printf('  {:14}{}', k, count_if(tests, lambda t: t.kind == k))
            printf('{:16}{}', 'Existing tests', len(existing))
            printf('')

        all_tests[d] = tests

    #
    # print()
    # for test in tests:
    #     print(' ', test)

    # all_tests.extend(tests)

    # print('\nTEST SUITE')
    # print('tests:', len(all_tests))
    # print('  preprocess:', count_if_kind(all_tests, Test.PREPROCESS))
    # print('  compile:', count_if_kind(all_tests, Test.COMPILE))
    # print('  link:', count_if_kind(all_tests, Test.LINK))
    # print('  run:', count_if_kind(all_tests, Test.RUN))

if __name__ == '__main__':
    exit(main())
