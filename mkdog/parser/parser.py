#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import logging

charset_re = re.compile(r'\.\. charset=([\w-]+)')
continuation_re = re.compile(r'\\[ \t]*\r?\n', re.MULTILINE)
lang_re = re.compile(r'\s*#\s*\.\. lang=([\w-]+)', re.UNICODE)
newline_re = re.compile(r'\r?\n')
comment_re = re.compile(r'\s*#(.+)')

variable_re = re.compile(r'([\w\d]+)\s*[?+:]?=\s*(.*)', re.UNICODE)
target_re = re.compile(r'^(\.?[\w\d]+)\s*:\s*(.*)$', re.MULTILINE)

TYPE_VARIABLE = 1
TYPE_TARGET = 2
TYPE_UNKNOWN = -1

_log = logging.getLogger('mkdog.mkparse')

class MakeParser(object):

    def __init__(self):
        self._reset()

    def _reset(self):
        self.name, self.lang = None, None
        self.type = TYPE_UNKNOWN
        self.comments = {}

    def parse(self, s):
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

        self._reset()

        for line in lines:
            if not line.strip():
                continue

            lang_match = lang_re.match(line)
            if lang_match:
                self.lang = lang_match.group(1)
                continue

            if self.lang:
                comment_match = comment_re.match(line)
                if comment_match:
                    comment = comment_match.group(1)
                    self.comments.setdefault(self.lang, []).append(comment)
                else:
                    type_match = variable_re.search(line) or target_re.match(line)
                    if type_match:
                        self.name = type_match.group(1)
                        self.type = TYPE_VARIABLE if type_match.re == variable_re else TYPE_TARGET
                    else:
                        _log.warn('Unknown type for expression %s' % line)

                    if self.name:
                        # filter comments for initial whitespace
                        for lang in self.comments:
                            while (not self.comments[lang][0].strip()):
                                self.comments[lang].pop(0)
                        yield (self.comments, self.name, self.type)
                    # now reset
                    self._reset()

def parsestring(s):
    parser = MakeParser()
    return parser.parse(s)


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
