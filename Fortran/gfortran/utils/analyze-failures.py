#!/usr/bin/env python3

import argparse
import json
import os
import re
import subprocess

def parse_test_name(s: str) -> str:
    # The test name is expected to start with Fortran/gfortran and end with
    # .test
    # FIXME: This probably depends on how the test suite is run. There might
    # be more text before Fortran/gfortran in which case we must get rid of
    # that as well.
    s = s.replace('test-suite :: Fortran/gfortran/', '')
    s = s.replace('.test', '')

    # This will be followed by the subdirectory in which the actual test is
    # The file name will be some mangled name dependent on the subdirectory
    # path.
    filename = os.path.basename(s)
    subdirs = s.replace(filename, '')

    # The filename starts with gfortran-$1-$2- where $1 \in
    # {regression,torture} and $2 \in {compile,execute}.
    for prefix in [
        'gfortran-regression-compile-',
        'gfortran-regression-execute-',
        'gfortran-torture-compile-',
        'gfortran-torture-execute-'
    ]:
        filename = filename.replace(prefix, '', 1)

    # The path separators in the subdirs are replaced with __ in the mangled
    # filename. Undo that to get the relative path to the failing test.
    filename = filename.replace(subdirs.replace('/', '__'), subdirs, 1)

    # The last underscore in the filename will be that of the extension of the
    # source file.
    left, _, right = filename.rpartition('_')
    filename = '.'.join([left, right])

    # Some files regression/gomp/appendix-a use dots in the filename which are
    # replaced with underscores in the mangled name. Special case those.
    if filename.startswith('regression/gomp/appendix-a'):
        filename = filename.replace('_', '.')

    return filename

def parse_test_config(root, filename):
    dirname = os.path.dirname(root).replace('Fortran/gfortran/', '')
    tests = []
    with open(os.path.join(source, filename)) as f:
        for line in f:
            l = line.strip()
            if not l or l.startswith('#'):
                continue

            # The line consists of fields separated by semicolons. The second
            # field is a space separated list of files that constitute a single
            # test. If there is more than one file in the list, the first
            # file is the main test file from which the name of the test will
            # be derived.
            fields = l.split(';')
            main = fields[1].split(' ')[0]
            tests.append(os.path.join(dirname, main))

    return sorted(tests)

def parse_test_configs(root):
    configs = glob.glob(
        'Fortran/gfortran/**/tests.cmake', root_dir = root, recursive = True
    )
    tests = []
    for config in configs:
        tests.extend(parse_test_config(source, config))

    return sorted(tests)

# Try to clean up as much "noise" as possible.
def filter(lines):
    out = []
    for l in lines:
        line = l.strip()
        # The 'no such file or directory error occurs because linking was
        # forced even if the object files could not be built for whatever
        # reason. An error will have been obtained during compilation of the
        # object file which is much more useful in general.
        if not line:
            continue
        elif 'error: no such file or directory' in line or \
           'No such file or directory' in line or \
           'no input files' in line:
            continue
        elif 'No newline at end of file' in line:
            continue
        else:
            out.append(line)
    return out

def parse_report_into(reportfile, log):
    def get_test_name(t):
        # The test name ends with the path to the test script. The test script
        # ends with a '.test' extension. Just force the line to be treated as a
        # path in which case the basename will be the test script name. Then,
        # skip the extension.
        return os.path.basename(t['name'])[:-5]

    passing = []
    failing = []
    with open(reportfile) as f:
        # FIXME: Maybe filter this so we only return the tests from the gfortran
        # test suite since the report (particularly the default) may have been
        # run for all the Fortran tests.
        j = json.load(f)
        for t in j['tests']:
            if t['code'] == 'FAIL':
                test = get_test_name(t)
                # In some cases, a compile-time failure will have resulted in
                # an executable not being built, but at test time, it will not
                # be reported as "executable missing" because the test is an
                # XFAIL and will be run with `not --crash`. In this case, the
                # runtime error is "no such file or directory". Don't bother
                # logging that error.
                filt = filter(t['output'].replace('\\n', '\n').split('\n'))

                # The first line will be the test run command. We don't care
                # about it.
                out = '\n'.join(filt[1:])
                if "No such file or directory" in t['output']:
                    log[test] = ''
                else:
                    log[test] = out

            elif t['code'] == 'NOEXE':
                # The missing executable error is unlikely to tell us anything
                # useful. The reason the executable is missing is because of a
                # compile-time failure which will have been captured in the
                # build log which will be parsed later.
                test = get_test_name(t)
                log[test] = ''

pfx = '[\[][ ]*[0-9]+[%][\]][ ]+'
re_target = re.compile('^gfortran-[A-Za-z0-9_-]+$')
re_entry = re.compile(f'^{pfx}.+$')
re_built = re.compile(f'^{pfx}Built target (.+)$')

# When all tests are forcibly built, all the targets will be declared as "built"
# in the log even if there were errors building them. This associates all the
# lines in the log with its corresponding target.
def parse_log_into(logfile, log):
    with open(logfile) as f:
        lines = []
        for l in f:
            line = l.strip()
            m = re_built.match(line)
            if m:
                target = m[1]
                # By parsing the test report, we know which targets failed and
                # we are only interested in those.
                if target in log:
                    out = '\n'.join(filter(lines))
                    if out and log[target]:
                        log[target] = '{}\n{}'.format(out, log[target])
                    elif out:
                        log[target] = out
                lines = []
            elif re_entry.match(line):
                # These are essentially just status lines indicating what
                # operation is taking place. They could be useful in some
                # cases, but generally not, so just ignore them.
                pass
            else:
                lines.append(line)

# Get the nth ancestor of the path. If n is 0, the path is returned unmodified.
def ancestor(n, p):
    if n:
        ancestor(n - 1, os.path.dirname(p))
    return p

def parse_commandline_args():
    ap = argparse.ArgumentParser(
        description =
        'Analyze the test suite report and the build log to characterize the '\
        'test failures.'
    )

    ap.add_argument('report', help = 'The report generated by lit.')

    ap.add_argument('log', help = 'The build log')

    return ap.parse_args()

def main():
    args = parse_commandline_args()
    root = ancestor(4, __file__)

    log = {}
    parse_report_into(args.report, log)
    parse_log_into(args.log, log)

    nyi = []
    segfault = []
    stop = []
    undecl = []
    undef = []
    scan = []
    parse = []
    sema = []
    linker = []
    runtime = []
    signal = []
    mismatch = []
    arg = []
    diff = []
    remaining = set(log.keys())
    for k, text in log.items():
        if not text:
            mismatch.append(k)
            remaining.remove(k)
        elif 'not yet implemented' in text:
            nyi.append(k)
            remaining.remove(k)
        elif 'Stack dump' in text:
            segfault.append(k)
            remaining.remove(k)
        elif 'Fortran STOP' in text:
            stop.append(k)
            remaining.remove(k)
        elif 'undeclared identifier' in text:
            undecl.append(k)
            remaining.remove(k)
        elif 'undefined reference' in text:
            undef.append(k)
            remaining.remove(k)
        elif 'Could not scan' in text:
            scan.append(k)
            remaining.remove(k)
        elif 'Could not parse' in text:
            parse.append(k)
            remaining.remove(k)
        elif 'linker command failed' in text:
            linker.append(k)
            remaining.remove(k)
        elif 'Semantic errors' in text:
            sema.append(k)
            remaining.remove(k)
        elif 'Fortran runtime error' in text:
            runtime.append(k)
            remaining.remove(k)
        elif 'child terminated by signal' in text:
            signal.append(k)
            remaining.remove(k)
        elif 'unknown argument' in text:
            arg.append(k)
            remaining.remove(k)
        elif '/diff' in text:
            diff.append(k)
            remaining.remove(k)
        print(k)
        print()
        print(text)
        print()
        print()
    print('not yet implemented', len(nyi))
    print('segfault', len(segfault))
    print('stop', len(stop))
    print('undeclared identifier', len(undecl))
    print('undefined reference', len(undef))
    print('could not scan', len(scan))
    print('could not parse', len(parse))
    print('linker command failed', len(linker))
    print('semantic errors', len(sema))
    print('runtime', len(runtime))
    print('terminated by signal', len(signal))
    print('mismatch', len(mismatch))
    print('unknown argument', len(arg))
    print('diff', len(diff))
    print(
        len(nyi) + len(segfault) + len(stop) + len(undecl) + len(undef) +
        len(scan) + len(parse) + len(linker) + len(sema) + len(runtime) +
        len(signal) + len(mismatch) + len(arg) + len(diff),
        len(log)
    )
    print(sorted(list(remaining)))

    return 0

if __name__ == '__main__':
    exit(main())
