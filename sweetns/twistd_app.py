# -*- coding: utf-8 -*-
from __future__ import absolute_import

from . import app as theapp
from . import config

# .tac app
# start with: SWEETNS_DB="redis://127.0.0.1:6379/0" twistd -ny sweetns/twistd_app.py
cfg = config.load()
cfg['name'] = "twistd_app"
print cfg
application = theapp.create_application(**cfg)
