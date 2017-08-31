import requests
from flask import Flask, jsonify, url_for
from flask_cache import Cache
from flask_cors import CORS

app = Flask(__name__)
app.config.from_object('dashing_issues.default_settings')
app.config.from_envvar('SETTINGS')
cache = Cache(app)
CORS(app)

session = requests.Session()
session.headers['Authorization'] = 'bearer {}'.format(app.config['GITHUB_TOKEN'])

GITHUB_ISSUES_QUERY = """
query GetIssues($owner: String!, $repository: String!) {
  repository(owner: $owner, name: $repository) {
    name
    url
    issues(first: 100, states: OPEN) {
      edges {
        node {
          title
          number
          url
          labels(first: 100) {
            edges {
              node {
                name
                color
              }
            }
          }
        }
      }
    }
    pullRequests(first: 100, states: OPEN) {
      edges {
        node {
          title
          number
          url
          labels(first: 100) {
            edges {
              node {
                name
                color
              }
            }
          }
        }
      }
    }
  }
}
"""


@cache.memoize(app.config['CACHE_TTL'])
def load_repo(owner, repository):
    data = {
            'query': GITHUB_ISSUES_QUERY,
            'variables': {
                'owner': owner,
                'repository': repository,
            },
    }
    response = session.post('https://api.github.com/graphql', json=data)
    response.raise_for_status()
    data = response.json()

    # TODO: Is this correct?
    if 'error' in data:
        raise Exception(data['error'])

    return data['data']['repository']


@app.route('/')
def index():
    return app.send_static_file('index.html')


@app.route('/repositories')
def repositories():
    result = {
            owner: {
                'url': url_for('owner', owner=owner),
                'repositories': [
                    {
                        'url': url_for('repository', owner=owner, repository=repository),
                        'name': repository,
                    } for repository in repositories
                ],
            } for owner, repositories in app.config['REPOSITORIES'].items()
    }

    return jsonify(result)


@app.route('/repositories/<owner>')
def owner(owner):
    result = [
        {
            'url': url_for('repository', owner=owner, repository=repository),
            'name': repository,
        } for repository in app.config['REPOSITORIES'].get(owner, [])
    ]

    return jsonify(result)


@app.route('/repositories/<owner>/<repository>')
def repository(owner, repository):
    if repository not in app.config['REPOSITORIES'][owner]:
        raise KeyError('Repository {} was not found'.format(owner))

    def _unpack_list(obj):
        return [item['node'] for item in obj['edges']]

    repo = load_repo(owner, repository)

    result = {
            'name': repo['name'],
            'url': repo['url'],
            'issues': [
                {
                    'title': issue['title'],
                    'number': issue['number'],
                    'url': issue['url'],
                    'labels': _unpack_list(issue['labels']),
                } for issue in (_unpack_list(repo['issues']) + _unpack_list(repo['pullRequests']))
            ],
    }
    return jsonify(result)
