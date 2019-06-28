export prometheus_multiproc_dir=/tmp/game-service/prom-data
export FLASK_APP=run.py

flask db upgrade
flask run --port 8080
