# Copyright (c) 2015 OpenStack Foundation.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import re

"""
Guidelines for writing new hacking checks

 - Use only for Searchlight-specific tests. OpenStack general tests
   should be submitted to the common 'hacking' module.
 - Pick numbers in the range SL3xx. Find the current test with
   the highest allocated number and then pick the next value.
   If nova has an N3xx code for that test, use the same number.
 - Keep the test method code in the source file ordered based
   on the SL3xx value.
 - List the new rule in the top level HACKING.rst file
 - Add test cases for each new rule to searchlight/tests/test_hacking.py

"""


asse_trueinst_re = re.compile(
    r"(.)*assertTrue\(isinstance\((\w|\.|\'|\"|\[|\])+, "
    "(\w|\.|\'|\"|\[|\])+\)\)")
asse_equal_type_re = re.compile(
    r"(.)*assertEqual\(type\((\w|\.|\'|\"|\[|\])+\), "
    "(\w|\.|\'|\"|\[|\])+\)")
asse_equal_end_with_none_re = re.compile(
    r"(.)*assertEqual\((\w|\.|\'|\"|\[|\])+, None\)")
asse_equal_start_with_none_re = re.compile(
    r"(.)*assertEqual\(None, (\w|\.|\'|\"|\[|\])+\)")
unicode_func_re = re.compile(r"(\s|\W|^)unicode\(")
log_translation = re.compile(
    r"(.)*LOG\.(audit)\(\s*('|\")")
doubled_words_re = re.compile(
    r"\b(then?|[iao]n|i[fst]|but|f?or|at|and|[dt]o)\s+\1\b")


def assert_true_instance(logical_line):
    """Check for assertTrue(isinstance(a, b)) sentences

    SL316
    """
    if asse_trueinst_re.match(logical_line):
        yield (0, "SL316: assertTrue(isinstance(a, b)) sentences not allowed")


def assert_equal_type(logical_line):
    """Check for assertEqual(type(A), B) sentences

    SL317
    """
    if asse_equal_type_re.match(logical_line):
        yield (0, "SL317: assertEqual(type(A), B) sentences not allowed")


def assert_equal_none(logical_line):
    """Check for assertEqual(A, None) or assertEqual(None, A) sentences

    SL318
    """
    res = (asse_equal_start_with_none_re.match(logical_line) or
           asse_equal_end_with_none_re.match(logical_line))
    if res:
        yield (0, "SL318: assertEqual(A, None) or assertEqual(None, A) "
               "sentences not allowed")


def no_translate_debug_logs(logical_line, filename):
    dirs = [
        "searchlight/api",
        "searchlight/cmd",
        "searchlight/common",
        "searchlight/elasticsearch",
        "searchlight/tests",
    ]

    if max([name in filename for name in dirs]):
        if logical_line.startswith("LOG.debug(_("):
            yield(0, "SL319: Don't translate debug level logs")


def no_direct_use_of_unicode_function(logical_line):
    """Check for use of unicode() builtin

    SL320
    """
    if unicode_func_re.match(logical_line):
        yield(0, "SL320: Use six.text_type() instead of unicode()")


def check_no_contextlib_nested(logical_line):
    msg = ("SL327: contextlib.nested is deprecated since Python 2.7. See "
           "https://docs.python.org/2/library/contextlib.html#contextlib."
           "nested for more information.")
    if ("with contextlib.nested(" in logical_line or
            "with nested(" in logical_line):
        yield(0, msg)


def check_doubled_words(physical_line, filename):
    """Check for the common doubled-word typos

    N343
    """
    msg = ("N343: Doubled word '%(word)s' typo found")

    match = re.search(doubled_words_re, physical_line)

    if match:
        return (0, msg % {'word': match.group(1)})


def factory(register):
    register(assert_true_instance)
    register(assert_equal_type)
    register(assert_equal_none)
    register(no_translate_debug_logs)
    register(no_direct_use_of_unicode_function)
    register(check_no_contextlib_nested)
    register(check_doubled_words)
