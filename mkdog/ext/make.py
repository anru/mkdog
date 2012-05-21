
from mkdog.domains.make import MakeDomain

def setup(app):
    app.add_domain(MakeDomain)
    app.add_config_value('mk_project_src', None, True)