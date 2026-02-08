import json
import sys


def build_client(tmp_path, monkeypatch):
    data_path = tmp_path / "data.json"
    data_path.write_text(json.dumps([{"text": "Test message", "label": "legit"}]))
    feedback_dir = tmp_path / "feedback"

    monkeypatch.setenv("PHISHGUARD_DATA_PATH", str(data_path))
    monkeypatch.setenv("PHISHGUARD_FEEDBACK_DIR", str(feedback_dir))

    if "app" in sys.modules:
        del sys.modules["app"]

    import app as app_module

    return app_module.app.test_client(), feedback_dir


def test_homepage_loads(tmp_path, monkeypatch):
    client, _ = build_client(tmp_path, monkeypatch)
    response = client.get("/")
    assert response.status_code == 200
    assert "PhishGuard" in response.get_data(as_text=True)


def test_get_email_returns_payload(tmp_path, monkeypatch):
    client, _ = build_client(tmp_path, monkeypatch)
    response = client.get("/get-email")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["text"]
    assert payload["label"] in {"phishing", "legit"}


def test_submit_feedback_persists_file(tmp_path, monkeypatch):
    client, feedback_dir = build_client(tmp_path, monkeypatch)
    response = client.post("/submit-feedback", json={"feedback": "Great flow"})
    assert response.status_code == 200
    assert feedback_dir.exists()
    assert any(feedback_dir.iterdir())


def test_health_endpoint(tmp_path, monkeypatch):
    client, _ = build_client(tmp_path, monkeypatch)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}
