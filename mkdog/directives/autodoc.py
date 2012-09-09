
import os, glob
from docutils import nodes
from docutils.statemachine import ViewList
from docutils.parsers.rst import Directive, directives
from mkdog.parser import readmk, parsestring

class MkDocumenter(object):

    objtypes = {
        1: 'var',
        2: 'target',
    }

    content_indent = u'   '

    def __init__(self, directive, indent=u''):
        self.result = directive.result
        self.indent = indent
        self.options = directive.options

    def add_line(self, line, source='<autodoc>', *lineno):
        """Append one line of generated reST to the output."""
        self.result.append(self.indent + line, source, *lineno)

    def add_directive_header(self, directive, name):
        """Add the directive header and options to the generated content."""
        domain = getattr(self, 'domain', 'make')
        self.add_line(u'.. %s:%s:: %s%s' % (domain, directive, name, ''),
                      '<autodoc>')
        if self.options.get('noindex'):
            self.add_line(u'   :noindex:', '<autodoc>')

    def generate(self, comments, name, token_type):
        directive = self.objtypes[token_type]
        self.add_line(u'', '<autodoc>')
        self.add_directive_header(directive, name)
        self.add_line(u'', '<autodoc>')

        # e.g. the module directive doesn't have content
        self.indent += self.content_indent

        if comments:
            for comment in comments:
                self.add_line(comment)

    def reset(self, indent=u''):
        self.indent = indent

class AutoFile(Directive):
    required_arguments = 1
    has_content = True
    
    def run(self):
        env = self.state.document.settings.env
        config = env.config
        self.warnings = []
        lang = config.language 
        
        mk_project_src = config['mk_project_src']
        if not mk_project_src:
            raise self.error("You must define `mk_project_src` config value!")
        
        arg0 = self.arguments[0]
        files_pattern = os.path.join(mk_project_src, arg0)
        filepaths = glob.glob(files_pattern)

        self.result = ViewList()
        documenter = MkDocumenter(self)

        for filepath in filepaths:
            self.state.document.settings.record_dependencies.add(filepath)
            
            f = open(filepath, 'rt')
            mksource = readmk(f)
            f.close()
            
            tokens = parsestring(mksource) #  [ (comments, name, type), ... ]

            for comments, name, _type in tokens:
                localized_comments = None
                if comments:
                    localized_comments = comments[lang] if lang in comments else None
                documenter.generate(localized_comments, name, _type)
                documenter.reset()

            node = nodes.paragraph()
            node.document = self.state.document
            self.state.nested_parse(self.result, 0, node)
        
        return self.warnings + node.children
        
        
        
        