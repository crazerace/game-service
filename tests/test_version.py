# Standard library
import json

# Internal modules
from app.config import SERVICE_VERSION, SERVICE_NAME


def test_version():
    with open("./package.json", "r") as f:
        package = json.load(f)
        assert SERVICE_VERSION == package["version"]
        assert SERVICE_NAME == package["name"]

