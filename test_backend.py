import subprocess
import json
from fastapi.testclient import TestClient
from backend.main import app

#MIPS mocked output for testing the rest of everything

def mars_iban_ok(*args, **kwargs):
    return subprocess.CompletedProcess(
        args=[],
        returncode=0,
        stdout=(
            "OK\n"
            "MSG=Valid checksum! This is a valid IBAN!\n"
            "BLZ=50010517\n"
            "KNR=1234567890\n"
        ),
        stderr=""
    )

def mars_prefix_error(*args, **kwargs):
    return subprocess.CompletedProcess(
        args=[],
        returncode=0,
        stdout=(
            "ERR\n"
            "MSG=No german IBAN prefix!\n"
        ),
        stderr=""
    )

def mars_checksum_error(*args, **kwargs):
    return subprocess.CompletedProcess(
        args=[],
        returncode=0,
        stdout=(
            "ERR\n"
            "MSG=Invalid checksum, this is not a valid IBAN!\n"
        ),
        stderr=""
    )

def mars_knrblz_ok(*args, **kwargs):
    return subprocess.CompletedProcess(
        args=[],
        returncode=0,
        stdout=(
            "OK\n"
            "IBAN=DE44500105171234567890\n"
        ),
        stderr=""
    )

#Tests

def test_iban_to_knr_success(monkeypatch):
    monkeypatch.setattr(subprocess, "run", mars_iban_ok)

    with TestClient(app) as client:
        res = client.post(
            "/run",
            json={
                "mode": "IBAN",
                "value1": "DE44500105171234567890"
            }
        )

    assert res.status_code == 200
    data = res.json()
    assert data["result"]["BLZ"] == "50010517"
    assert data["result"]["KNR"] == "1234567890"


def test_iban_prefix_error(monkeypatch):
    monkeypatch.setattr(subprocess, "run", mars_prefix_error)

    with TestClient(app) as client:
        res = client.post(
            "/run",
            json={
                "mode": "IBAN",
                "value1": "FR44500105171234567890"
            }
        )

    assert res.status_code == 400
    assert "No german IBAN prefix!" in res.json()["detail"]


def test_iban_checksum_error(monkeypatch):
    monkeypatch.setattr(subprocess, "run", mars_checksum_error)

    with TestClient(app) as client:
        res = client.post(
            "/run",
            json={
                "mode": "IBAN",
                "value1": "DE00123456781234567890"
            }
        )

    assert res.status_code == 400
    assert "Invalid checksum" in res.json()["detail"]


def test_knrblz_to_iban(monkeypatch):
    monkeypatch.setattr(subprocess, "run", mars_knrblz_ok)

    with TestClient(app) as client:
        res = client.post(
            "/run",
            json={
                "mode": "KNRBLZ",
                "value1": "1234567890",
                "value2": "50010517"
            }
        )

    assert res.status_code == 200
    assert res.json()["result"]["IBAN"].startswith("DE")


def test_history_endpoint(monkeypatch):
    monkeypatch.setattr(subprocess, "run", mars_iban_ok)

    with TestClient(app) as client:
        res = client.get("/history")

    assert res.status_code == 200
    assert isinstance(res.json(), list)
