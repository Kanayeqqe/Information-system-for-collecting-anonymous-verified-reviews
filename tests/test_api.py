import os
import importlib
from fastapi.testclient import TestClient

os.environ["DATABASE_URL"] = "sqlite:///:memory:"
import src.db.database as database
importlib.reload(database)
database.init_db()

from src.main import app

client = TestClient(app)


def test_full_box_lifecycle():
    response = client.post("/box")
    assert response.status_code == 200
    data = response.json()
    assert data["uuid"]
    assert data["owner_token"]

    uuid = data["uuid"]
    token = data["owner_token"]

    invalid_feedback = client.post(f"/box/{uuid}/feedback", json={"text": "badword content"})
    assert invalid_feedback.status_code == 400

    feedback = client.post(f"/box/{uuid}/feedback", json={"text": "Normal feedback text"})
    assert feedback.status_code == 200
    fb_data = feedback.json()
    assert fb_data["text"] == "Normal feedback text"
    assert fb_data["status"] == "approved"

    unauthorized = client.get(f"/box/{uuid}")
    assert unauthorized.status_code == 403

    owner_view = client.get(f"/box/{uuid}", params={"token": token})
    assert owner_view.status_code == 200
    assert len(owner_view.json()["feedbacks"]) == 1

    reply_fail = client.post(f"/feedback/{fb_data['id']}/reply", json={"text": "Owner reply"}, params={"token": "wrong"})
    assert reply_fail.status_code == 403

    reply_ok = client.post(f"/feedback/{fb_data['id']}/reply", json={"text": "Owner reply"}, params={"token": token})
    assert reply_ok.status_code == 200

    owner_view_after = client.get(f"/box/{uuid}", params={"token": token})
    assert len(owner_view_after.json()["feedbacks"][0]["replies"]) == 1
