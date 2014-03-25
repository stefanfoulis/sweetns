# -*- coding: utf-8 -*-
# run with twistd -ny app.py
from twisted.names import dns, server, client, cache
from twisted.application import service, internet
import txredisapi
from .redis import RedisResolverBackend


def create_application():
    rd = txredisapi.lazyConnectionPool(host="127.0.0.1", port=36379, dbid=0, password=None)
    redisBackend = RedisResolverBackend(rd, servers=[('8.8.8.8', 53)])

    application = service.Application("txdnsredis")
    srv_collection = service.IServiceCollection(application)

    dnsFactory = server.DNSServerFactory(caches=[cache.CacheResolver()], clients=[redisBackend])

    internet.TCPServer(53, dnsFactory).setServiceParent(srv_collection)
    internet.UDPServer(53, dns.DNSDatagramProtocol(dnsFactory)).setServiceParent(srv_collection)
    return application


# .tac app
application = create_application()