# 3rd party modules
from crazerace.http import status

# Intenal modules
from tests import TestEnvironment, JSON


def test_get_health():
    with TestEnvironment() as client:
        res = client.get("/health", content_type=JSON)
        body = res.get_json()
        assert res.status_code == status.HTTP_200_OK
        assert res.get_json()["status"] == "UP"
        assert res.get_json()["db"] == "UP"
