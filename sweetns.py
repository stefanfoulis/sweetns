# original code stolen from https://gist.github.com/gleicon/1074124
# Python/Twisted/Redis backed DNS server - resolves from NAME to IP addrs
# fallback to google or any other DNS server to resolv domains not present on Redis
# to set a new domain on redis, just issue a SET domain.tld ip_addr
# run with twistd -ny txredns.tac
# gleicon 2011
from twisted.names import dns, server, client, cache
from twisted.application import service, internet
from twisted.internet import defer
from twisted.python import log
import txredisapi


class RedisResolverBackend(client.Resolver):
    def __init__(self, redis, servers=None):
        self.redis = redis
        client.Resolver.__init__(self, servers=servers)
        self.ttl = 5

    @defer.inlineCallbacks
    def _get_ip_addr(self, hostname, timeout):
        # to allow wildcard entries, lookup all possible wildcard versions of the host
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
        # ['this.is.my.site.dev', '.is.my.site.dev', '.my.site.dev', '.site.dev', '.dev', '.']
        for name in names:
            key = "dns:{0}".format(name)
            ip = yield self.redis.get(key)
            log.msg('lookup for {0} returned {1}'.format(key, ip))
            if ip:
                defer.returnValue([(dns.RRHeader(hostname, dns.A, dns.IN, self.ttl, dns.Record_A(ip, self.ttl)),), (), ()])
        # so no entry was found... let's ask googles dns
        i = yield self._lookup(hostname, dns.IN, dns.A, timeout)
        defer.returnValue(i)

    def lookupAddress(self, name, timeout = None):
        return self._get_ip_addr(name, timeout)


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