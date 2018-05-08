from collections import defaultdict

import requests

from flask import Flask, jsonify

app = Flask(__name__)


class Plugin(object):
    def __init__(self, name, url=None, yum=None, deb=None):
        self.name = name
        self.url = url or 'https://github.com/theforeman/' + name
        self.yum = yum or 'tfm-rubygem-' + name
        self.deb = deb or 'ruby-' + name.replace('_', '-')
        self.versions = {}


@app.route('/')
def index():
    return app.send_static_file('plugins.html')


@app.route('/plugins')
def plugins():

    releases = defaultdict(dict)

    for release in ('1.15', '1.16', '1.17', 'nightly'):
        response = requests.get('http://localhost:5001/' + release)
        response.raise_for_status()

        for name, package in response.json().items():
            releases[name][release] = package['version']

    names = [
            'foreman-tasks',
            'foreman_abrt',
            'foreman_ansible',
            'foreman_chef',
            'foreman_custom_parameters',
            'foreman_dhcp_browser',
            'foreman_docker',
            'foreman_expire_hosts',
            'foreman_graphite',
            'foreman_hooks',
            'foreman_host_extra_validator',
            'foreman_memcache',
            'foreman_monitoring',
            'foreman_omaha',
            'foreman_openscap',
            'foreman_remote_execution',
            'foreman_salt',
            'foreman_templates',
            'puppetdb_foreman',
    ]

    plugins = []

    for name in names:
        plugin = Plugin(name)
        plugin.versions = releases[plugin.yum]
        plugins.append(plugin)

    return jsonify([plugin.__dict__ for plugin in plugins])
