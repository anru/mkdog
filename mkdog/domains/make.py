from sphinx import addnodes
from sphinx.locale import l_, _
from sphinx.domains import Domain, ObjType
from sphinx.roles import XRefRole
from sphinx.util.nodes import make_refnode
from sphinx.directives import ObjectDescription
from mkdog.directives.autodoc import AutoFile

class MakeObject(ObjectDescription):
    def handle_signature(self, sig, signode):
        fullname = sig # now syntax is very simple - sig totally is fullname
        signode += addnodes.desc_name(fullname, fullname)
        return fullname

    def add_target_and_index(self, name, sig, signode):
        # namespace: 1 - variables and functions, 2 - targets
        fullname = name
        descname = name
        if self.objtype == 'var':
            fullname = '$' + fullname
        # note target
        if fullname not in self.state.document.ids:
            signode['names'].append(fullname)
            signode['ids'].append(fullname)
            signode['first'] = (not self.names)
            self.state.document.note_explicit_target(signode)
            objects = self.env.domaindata['make']['objects']
            if fullname in objects:
                self.state_machine.reporter.warning(
                    'duplicate object description of %s, ' % fullname +
                    'other instance in ' +
                    self.env.doc2path(objects[fullname][0]) +
                    ', use :noindex: for one of them',
                    line=self.lineno)
            objects[fullname] = (self.env.docname, self.objtype)

        indextext = self.get_index_text(descname)
        if indextext:
            self.indexnode['entries'].append(('single', indextext, fullname, ''))

    def get_index_text(self, fullname):
        if self.objtype == 'var':
            return _('%s (variable)') % (fullname)
        elif self.objtype == 'target':
            return _('%s: (target)') % (fullname)
        return ''

class MakeXRefRole(XRefRole):
    def process_link(self, env, refnode, has_explicit_title, title, target):
        if refnode['reftype'] == 'var':
            target = '$' + target
        return title, target

class MakeDomain(Domain):
    name = 'make'
    label = 'Make'

    object_types = {
        'var': ObjType(l_('variable'),  'var'),
        'target': ObjType(l_('target'), 'target'),
    }

    directives = {
        'var': MakeObject,
        'target': MakeObject,
        'autofile': AutoFile
    }

    roles = {
        'var': MakeXRefRole(),
        'target': MakeXRefRole(),
    }

    initial_data = {
        'objects': {}
    }

    def clear_doc(self, docname):
        for fullname, (fn, _) in self.data['objects'].items():
            if fn == docname:
                del self.data['objects'][fullname]

    def resolve_xref(self, env, fromdocname, builder, typ, target, node, contnode):
        objtypes = self.objtypes_for_role(typ)

        objects = self.data['objects']
        obj = None

        if target in objects and objects[target][1] in objtypes:
            obj = self.data['objects'][target]

        if obj is None:
            return None

        return make_refnode(builder, fromdocname, obj[0], target, contnode, target)

    def get_objects(self):
        for refname, (docname, type) in self.data['objects'].iteritems(): #@ReservedAssignment
            yield (refname, refname, type, docname, refname, 1)
