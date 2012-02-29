#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import logging

charset_re = re.compile(r'\.\. charset=([\w-]+)')
continuation_re = re.compile(r'\\[ \t]*\r?\n', re.MULTILINE)
lang_re = re.compile(r'\.\. lang=([\w-]+)', re.UNICODE)
newline_re = re.compile(r'\r?\n')

variable_re = re.compile(r'(\w[\w\d]*)\s*[?+:]?=\s*(.*)', re.UNICODE)
target_re = re.compile(r'^(\.?\w[\w\d]*)\s*:\s*(.*)$', re.MULTILINE)

TYPE_VARIABLE = 1
TYPE_TARGET = 2
TYPE_UNKNOWN = -1

_log = logging.getLogger('mkdog.mkparse')

def parsestring(s):
    """
    yields 3-tuples
    (comments, name, type)
    where:
    comments - dict of comments, where keys are lang, values = list of lines
    name - name of Makefile's definition
    type - type of Makefile's definition, one of:
        1 - variable
        2 - target
        -1 - unknown
    """
    s = re.sub(continuation_re, '', s)
    lines = re.split(newline_re, s)

    name, lang = None, None
    type = TYPE_UNKNOWN
    comments = {} #

    for line in lines:
        if not line.strip():
            continue

        lang_match = lang_re.search(line)
        if lang_match:
            lang = lang_match.group(1)
            continue

        if lang:
            if line.startswith('#'):
                comments.setdefault(lang, []).append(line.lstrip('#'))
            else:
                type_match = variable_re.search(line) or target_re.match(line)
                if type_match:
                    name = type_match.group(1)
                    type = TYPE_VARIABLE if type_match.re == variable_re else TYPE_TARGET
                else:
                    _log.warn('Unknown type for expression %s' % line)

                if name:
                    # filter comments for initial whitespace
                    for lang in comments:
                        i = 0
                        while (not comments[lang][i].strip()):
                            comments[lang].pop(i)
                    yield (comments, name, type)
                # now reset
                lang, name = None, None
                comments = {}
                type = TYPE_UNKNOWN
            continue


def readmk(f, charset='utf-8'):
    for line in f:
        m = charset_re.search(line)
        if m:
            charset = m.group(1)
            break
    f.seek(0)
    return f.read().decode(charset)

if __name__ == '__main__':
    import sys
    f = open(sys.argv[1], 'rt')
    source = readmk(f)
    f.close()
    for comments, name, type in parsestring(source):
        print '%s:%d' % (name, type)
        for lang in comments:
            print "%s\n" % lang, '\n'.join(comments[lang])
