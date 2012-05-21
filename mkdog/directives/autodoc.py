
import os
from docutils.
from docutils.parsers.rst import Directive, directives
from mkdog.parser import readmk, parsestring


class AutoFile(Directive):
    required_arguments = 1
    
    def run(self):
        env = self.state.document.settings.env
        config = env.config
        
        mk_project_src = config['mk_project_src']
        if not mk_project_src:
            raise self.error("You must define `mk_project_src` config value!")
        
        filename = self.arguments[0]
        filepath = os.path.join(mk_project_src, filename)
        
        if not os.path.exists(filepath):
            raise self.error("File %s not exist" % filepath)
        
        self.state.document.settings.record_dependencies.add(filepath)
        
        f = open(filepath, 'rt')
        mksource = readmk(f)
        f.close()
        
        tokens = parsestring(mksource) #  [ (comments, name, type), ... ]
        
        ret = []
        return ret
        
        
        
        