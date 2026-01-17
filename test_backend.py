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

# pydantic input validation tests with 422 errors.

def test_invalid_iban_too_short():
    """Test that invalid IBAN is rejected with 422"""
    with TestClient(app) as client:
        res = client.post(
            "/run",
            json={
                "mode": "IBAN",
                "value1": "INVALID"
            }
        )
    
    assert res.status_code == 422
    assert "detail" in res.json()
    assert "IBAN must be 22 digits" in str(res.json()["detail"])


def test_invalid_knr_length():
    """Test that KNR with wrong length is rejected with 422"""
    with TestClient(app) as client:
        res = client.post(
            "/run",
            json={
                "mode": "KNRBLZ",
                "value1": "123",
                "value2": "12345678"
            }
        )
    
    assert res.status_code == 422
    assert "detail" in res.json()
    assert "KNR must be exactly 10 digits" in str(res.json()["detail"])


def test_invalid_blz_length():
    """Test that BLZ with wrong length is rejected with 422"""
    with TestClient(app) as client:
        res = client.post(
            "/run",
            json={
                "mode": "KNRBLZ",
                "value1": "1234567890",
                "value2": "12345"
            }
        )
    
    assert res.status_code == 422
    assert "detail" in res.json()
    assert "BLZ must be exactly 8 digits" in str(res.json()["detail"])


def test_invalid_mode():
    """Test that invalid mode is rejected with 422"""
    with TestClient(app) as client:
        res = client.post(
            "/run",
            json={
                "mode": "HACKER",
                "value1": "test"
            }
        )
    
    assert res.status_code == 422
    assert "detail" in res.json()
    assert "Mode must be IBAN or KNRBLZ" in str(res.json()["detail"])


def test_sql_injection_attempt():
    """Test that SQL injection attempt is rejected with 422"""
    with TestClient(app) as client:
        res = client.post(
            "/run",
            json={
                "mode": "IBAN",
                "value1": "DE'; DROP TABLE users; --"
            }
        )
    
    assert res.status_code == 422
    assert "detail" in res.json()
    assert "IBAN must be 22 digits" in str(res.json()["detail"])


def test_missing_blz_for_knrblz_mode():
    """Test that missing BLZ for KNRBLZ mode is rejected with 400"""
    with TestClient(app) as client:
        res = client.post(
            "/run",
            json={
                "mode": "KNRBLZ",
                "value1": "1234567890"
                # value2 is missing
            }
        )
    
    #  400 (manual check)
    assert res.status_code == 400
    assert "detail" in res.json()
    assert "BLZ" in str(res.json()["detail"]) or "value2" in str(res.json()["detail"])


def test_xss_attempt():
    """Test that XSS/special characters attempt is rejected with 422"""
    with TestClient(app) as client:
        res = client.post(
            "/run",
            json={
                "mode": "IBAN",
                "value1": "DEXXX<script>alert"
            }
        )
    
    assert res.status_code == 422
    assert "detail" in res.json()
    assert "IBAN must be 22 digits" in str(res.json()["detail"])


def test_iban_with_lowercase_letters():
    """Test that IBAN with lowercase letters is rejected with 422"""
    with TestClient(app) as client:
        res = client.post(
            "/run",
            json={
                "mode": "IBAN",
                "value1": "de44500105171234567890"
            }
        )
    
    assert res.status_code == 422
    assert "detail" in res.json()


def test_knr_with_non_digits():
    """Test that KNR with non-digit characters is rejected with 422"""
    with TestClient(app) as client:
        res = client.post(
            "/run",
            json={
                "mode": "KNRBLZ",
                "value1": "1234567ABC",
                "value2": "12345678"
            }
        )
    
    assert res.status_code == 422
    assert "detail" in res.json()