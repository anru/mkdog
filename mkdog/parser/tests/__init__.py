
import os, sys, re
import unittest

from termcolors import make_style

sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), '..')))

expected_re = re.compile(r'\s*#\s*!expected\s*')
expected_end_re = re.compile(r'\s*#\s*!\s*')

should_re = re.compile(r'\s*#\s*([.\w\d]+):(\d+):([\w,]+)\s*')
newline_re = re.compile(r'\r?\n')

from parser import parsestring, readmk, TYPE_TARGET, TYPE_VARIABLE

makeid_ = make_style(fg='green', opts=('bold',))
comment_ = make_style(fg='green')
lang_ = make_style(fg='green', opts=('underscore',))
err_ = make_style(fg='red')

def _desc(name, type):
    type = int(type)
    if type == TYPE_TARGET:
        return "target `%s`" % name
    elif type == TYPE_VARIABLE:
        return "variable `%s`" % name
    return "Expr %s" % name

def _id(name, type):
    return "%s:%s" % (name, str(type))

class TestMakeFiles(unittest.TestCase):

    def setUp(self):
        base_dir = os.path.dirname(sys.argv[0])
        examples_dir = os.path.join(base_dir, 'examples')
        self.mk_files = []
        for filename in os.listdir(examples_dir):
            if not filename.endswith('.mk'):
                continue
            self.mk_files.append(os.path.join(examples_dir, filename))


    def test_makefiles(self):
        for mk_file in self.mk_files:
            print "Parse %s" % os.path.basename(mk_file)
            f = open(mk_file, 'rt')

            expected_block = False
            should_list = []

            # read expected block
            for line in f:
                if expected_block and expected_end_re.match(line):
                    break

                if expected_block:
                    should_match = should_re.match(line)
                    if should_match:
                        should_list.append(should_match.groups())

                if expected_re.match(line):
                    expected_block = True
                    continue

            f.seek(0)
            source = readmk(f)


            for comments, name, type in parsestring(source):
                identity = _id(name, type)
                print makeid_(identity)
                desc = _desc(name, type)
                self.assertIn(identity, (_id(x[0], x[1]) for x in should_list), err_("%s not in expected list" % desc))
                entry = filter(lambda x: _id(x[0], x[1]) == identity, should_list)[0]
                should_langs = entry[2].split(',')
                for lang in comments:
                    self.assertIn(lang, should_langs, err_("lang %s for %s should exists" % (lang, desc)))
                    print lang_(lang)
                    print comment_('\n'.join(comments[lang]))
                    should_langs.remove(lang)
                for lang in should_langs:
                    self.fail(err_("Lang %s not preset in %s" % (lang, desc)))
                print
                should_list = filter(lambda x: _id(x[0], x[1]) != identity, should_list)

            for x in should_list:
                self.fail(err_("%s not parsed in makefile" % _desc(x[0], x[1])))

if __name__ == '__main__':
    unittest.main()


