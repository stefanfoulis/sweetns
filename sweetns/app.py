# -*- coding: utf-8 -*-
from __future__ import absolute_import
from twisted.internet import reactor
from twisted.names import dns, server, cache
from twisted.application import service, internet
import urlparse
from . import backends
from .log import log


def create_factory(db, servers=None):
    log.msg('creating factory...')
    db_url = urlparse.urlparse(db)
    servers = servers or ['dns://8.8.8.8:53', 'dns://8.8.4.4:53']
    if db_url.scheme == 'redis':
        backend = backends.RedisResolverBackend(
            db=db,
            servers=servers,
        )
    else:
        raise RuntimeError('invalid db backend "{}" in {}'.format(
            db_url.scheme,
            db,
        ))
    factory = server.DNSServerFactory(
        caches=[
            cache.CacheResolver(),
        ],
        clients=[
            backend,
        ],
    )
    print 'create factory: ', factory
    return factory


def create_application(db, ip, port, name):
    log.msg('creating app...')
    port = int(port)
    app = service.Application(name)
    factory = create_factory(db=db)
    serviceCollection = service.IServiceCollection(app)
    internet\
        .TCPServer(port, factory)\
        .setServiceParent(serviceCollection)
    internet\
        .UDPServer(port, dns.DNSDatagramProtocol(factory))\
        .setServiceParent(serviceCollection)
    return app


def create_reactor(db, ip, port):
    log.msg('creating reactor...')
    port = int(port)
    factory = create_factory(db=db)
    reactor.listenTCP(port, factory)
    reactor.listenUDP(port, dns.DNSDatagramProtocol(factory))
    return reactor
