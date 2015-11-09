# -*- coding: utf-8 -*-
import os


def load():
    servers = []
    for key, value in os.environ.items():
        if key.startswith('SWEETNS_SERVER'):
            servers.append(
                os.path.expandvars(value)
            )
    return {
        'db': os.path.expandvars(
            os.environ.get('SWEETNS_DB', 'redis://localhost:6379/')
        ),
        'ip': os.path.expandvars(
            os.environ.get('SWEETNS_IP', '0.0.0.0')
        ),
        'port': os.path.expandvars(
            os.environ.get('SWEETNS_PORT', '53')
        ),
        'servers': servers,
    }
