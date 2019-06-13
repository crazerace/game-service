export FLASK_APP=run.py

flask db upgrade
uwsgi uwsgi.ini
