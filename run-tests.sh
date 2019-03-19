rm -rf .pytest_cache
echo 'Checking types'
mypy --ignore-missing-imports run.py

echo 'Running tests'
pytest --cache-clear --disable-pytest-warnings