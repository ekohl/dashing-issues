# Dashing Issues

Dashing Issues attempts to give an overview of github issues. The goal is to provide easy overviews for triage.

## Running in development

```bash
cp settings.py.example settings.py
# Modify to fit your needs
pip install -e .
SETTINGS=$(pwd)/settings.py FLASK_APP=dashing_issues FLASK_DEBUG=1 flask run
```
