#!/usr/bin/env python

from __future__ import absolute_import, print_function

import argparse
import collections
import os
import sys
import yaml


EXTRA_CHECK_MAKERS = []
STATSD_CHECK = {
    'send': 'conncheck.test:1|c',
    'expect': '',
}


class SettingsDict(dict):
    """Wrapper for Django settings object that allows access as a dict"""

    def __init__(self, settings):
        self.settings = settings

    def __getitem__(self, name):
        return getattr(self.settings, name, None)

    def get(self, name, default):
        return getattr(self.settings, name, default)


def get_settings(settings_module):
    if settings_module:
        os.environ['DJANGO_SETTINGS_MODULE'] = settings_module

    from django.conf import settings as django_settings
    return SettingsDict(django_settings)


def make_postgres_checks(settings, options):
    checks = []
    engines = {
        'django.db.backends.postgresql_psycopg2': 'postgres',
        'django.db.backends.mysql': 'mysql',
        'django.db.backends.oracle': 'oracle',
    }
    for name, db in settings.get('DATABASES', {}).items():
        db = collections.defaultdict(lambda: None, db)
        # We exclude hosts starting with a forward slash (/) as these are
        # always socket filepaths for MySQL and PostgreSQL, see:
        # https://docs.djangoproject.com/en/dev/ref/settings/#host
        if db['ENGINE'] in engines and not str(db['HOST']).startswith('/'):
            check = {
                'type': engines[db['ENGINE']],
                'database': db.get('NAME', options.db_name),
                'host': db['HOST'],
            }

            port = db['PORT']
            if port is not None:
                check['port'] = int(port)

            username = db['USER']
            if username is not None:
                check['username'] = username

            password = db['PASSWORD']
            if password is not None:
                check['password'] = password

            checks.append(check)

    return checks


def make_oops_checks(settings, options):
    checks = []
    for key in ('OOPS', 'OOPSES'):
        oopses = settings.get(key, {})
        if oopses:
            break

    publishers = oopses.get('publishers', [])
    for publisher in publishers:
        if publisher['type'] == 'amqp':
            checks.append({
                'type': 'amqp',
                'vhost': publisher['vhost'],
                'host': publisher['host'],
                'port': publisher.get('port', 5672),
                'username': publisher['user'],
                'password': publisher['password'],
            })
    return checks


def make_celery_checks(settings, options):
    # XXX: this is the old style of celery config
    # TODO add support for new style config
    checks = []
    host = settings['BROKER_HOST']
    backend = settings['BROKER_BACKEND']
    if ((not backend and host) or backend in ('amqp', 'redis')):
        check = {
            'type': backend or 'amqp',
            'host': host,
            'port': int(settings['BROKER_PORT']),
            'username': settings['BROKER_USER'],
            'password': settings['BROKER_PASSWORD'],
        }
        if settings['BROKER_VHOST']:
            check['vhost'] = settings['BROKER_VHOST']
        checks.append(check)
    return checks


def make_memcache_checks(settings, options):
    checks = []
    caches = settings.get('CACHES', {})

    for cache in caches.values():
        backend = cache['BACKEND']
        if (not backend or backend ==
                'django.core.cache.backends.memcached.MemcachedCache'):

            locations = cache['LOCATION']
            if not isinstance(locations, collections.Iterable):
                locations = [locations]

            for location in locations:
                host, port = location.split(':')
                checks.append({
                    'type': 'memcached',
                    'host': host,
                    'port': int(port),
                })

    return checks


def make_statsd_checks(settings, options):
    # For now we just want to make sure we can reach statsd via UDP
    checks = []
    if settings['STATSD_HOST']:
        if ':' in settings['STATSD_HOST']:
            host, port = settings['STATSD_HOST'].split(':')
        else:
            host = settings['STATSD_HOST']
            port = int(settings.get('STATSD_PORT', 8125))
        checks.append({
            'type': 'udp',
            'host': host,
            'port': port,
            'send': STATSD_CHECK['send'],
            'expect': STATSD_CHECK['expect'],
        })
    return checks


def gather_checks(options):
    settings = get_settings(options.settings_module)
    checks = []
    checks.extend(make_postgres_checks(settings, options))
    checks.extend(make_oops_checks(settings, options))
    checks.extend(make_celery_checks(settings, options))
    checks.extend(make_memcache_checks(settings, options))
    checks.extend(make_statsd_checks(settings, options))

    for maker in EXTRA_CHECK_MAKERS:
        checks.extend(maker(settings, options))

    return checks


def main(*args):
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--output-file',
                              dest='output_file',
                              required=False,
                              help='File path to save YAML config to rather'
                                   ' than the default of printing to STDOUT')
    parser.add_argument('-m', '--settings-module',
                        dest="settings_module",
                        action="store",
                        help='Django Python settings module import path')
    parser.add_argument('-d', '--database-name',
                        dest="db_name",
                        action="store",
                        help='Database schema if not discoverable from '
                             'settings module')
    parser.add_argument('--statsd_send',
                        dest="statsd_send",
                        action="store",
                        help='Test string to send to StatsD server')
    parser.add_argument('--statsd_expect',
                        dest="statsd_expect",
                        action="store",
                        help='Successful response string from StatsD test')
    # Added so old reliances on -p/--print flag don't break
    parser.add_argument('-p', '--print',
                              dest='print',
                              action='store_true',
                              help='')
    opts = parser.parse_args(args)

    if opts.statsd_send:
        STATSD_CHECK['send'] = opts.statsd_send

    if opts.statsd_expect:
        STATSD_CHECK['expect'] = opts.statsd_expect

    output = yaml.dump(gather_checks(opts), default_flow_style=False)

    if opts.output_file:
        with open(opts.output_file, 'w') as f:
            f.write(output)
    else:
        print(output, file=sys.stdout)

    return 0


def run():
    exit(main(*sys.argv[1:]))


if __name__ == '__main__':
    run()
