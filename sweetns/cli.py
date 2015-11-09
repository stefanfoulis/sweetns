# -*- coding: utf-8 -*-
from __future__ import absolute_import
import click
from twisted.internet.defer import inlineCallbacks

from . import app, config


@click.group()
def main():
    pass


@main.command()
@click.option(
    '--db',
    help=(
        'Connection url for the db in the format '
        'redis://:password@127.0.0.1:6379/0 '
        'defaults to the SWEETNS_DB environment variable.'
    ),
)
@click.option(
    '--ip',
    default='0.0.0.0',
    help='server ip. defaults to the SWEETNS_IP environment variable.',
)
@click.option(
    '--port',
    default='53',
    help='port to listen for dns queries. defautls to the SWEETNS_PORT'
         'environment variable.',
)
def server(**kwargs):
    cfg = config.load()
    cfg.update(**{key: value for key, value in kwargs.items() if value})
    for key, value in cfg.items():
        click.secho('{}: {}'.format(key, value), color='green')
    click.secho('starting sweetns...')
    reactor = app.create_reactor(**cfg)
    reactor.run()


@main.command()
@click.option(
    '--db',
    help=(
        'Connection url for the db in the format '
        'redis://:password@127.0.0.1:6379/0 '
        'defaults to the SWEETNS_DB environment variable.'
    ),
)
def doctor(**kwargs):
    cfg = config.load()
    cfg.update(**{key: value for key, value in kwargs.items() if value})
    for key, value in cfg.items():
        click.secho('{}: {}'.format(key, value), color='green')
    click.secho('doctoring...')

    @inlineCallbacks
    def get_some_keys():
        from .backends.redis import RedisResolverBackend
        rrb = RedisResolverBackend(db=cfg['db'], servers=cfg['servers'])
        value = yield rrb.redis.get('dns:my.aldryn.net')
        click.echo('test: {}'.format(value))


if __name__ == '__main__':
    main()
