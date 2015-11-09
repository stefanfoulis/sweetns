# -*- coding: utf-8 -*-
from __future__ import absolute_import
from twisted.names import dns, client
from twisted.internet import defer
import txredisapi
import urlparse

from ..log import log


class RedisResolverBackend(client.Resolver):
    def __init__(self, db, servers=None, ttl=None):
        db_url = urlparse.urlparse(db)
        self.redis = txredisapi.lazyConnectionPool(
            host=db_url.hostname,
            port=int(db_url.port or 6379),
            dbid=int(db_url.path.strip('/') or 0),
            password=db_url.password or None,
        )
        self.servers = []
        if servers:
            for server in servers:
                if not isinstance(server, tuple):
                    server_url = urlparse.urlparse(server)
                    server = (server_url.hostname, int(server_url.port or 53))
                self.servers.append(server)

        client.Resolver.__init__(self, servers=servers)
        self.ttl = ttl or 10
        log.msg('init resolver')

    @defer.inlineCallbacks
    def _get_ip_addr(self, hostname, timeout):
        # to allow wildcard entries, lookup all possible wildcard versions of
        # the host
        # e.g for this.is.mysite.dev we will lookup
        #     this.is.mysite.dev
        #     .is.mysite.dev
        #     .mysite.dev
        #     .dev
        #     .
        # in that order. The first match is returned
        names = []
        parts = hostname.split('.')  # ['this', 'is', 'mysite', 'dev']
        names.append(hostname)
        while len(parts):
            parts.pop(0)
            names.append('.{0}'.format('.'.join(parts)))
        print parts
        for name in names:
            key = "dns:{0}".format(name)
            log.msg('checking {}'.format(key))
            ip = yield self.redis.get(key)
            log.msg('lookup for {0} returned {1}'.format(key, ip))
            if ip:
                defer.returnValue([
                    (
                        dns.RRHeader(
                            hostname,
                            dns.A,
                            dns.IN,
                            self.ttl,
                            dns.Record_A(ip, self.ttl),
                        ),
                    ),
                    (),
                    ()
                ])
        # so no entry was found... let's ask the google dns
        i = yield self._lookup(hostname, dns.IN, dns.A, timeout)
        defer.returnValue(i)

    def lookupAddress(self, name, timeout=None):
        return self._get_ip_addr(name, timeout)
