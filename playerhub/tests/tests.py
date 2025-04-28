import pytest
from playerhub.models import Run
from playerhub.factories import UserFactory


@pytest.mark.django_db
def test_add_run(client):
    runs_count = Run.objects.count()
    user = UserFactory()
    client.force_authenticate(user=user)
    data = {
        "name": "Test Run",
        "game": "Test Game",
        "mode": "SPEEDRUN",
        "is_finished": False,
        "session_code": "223"
    }
    response = client.post('/runs/', data, format='json')
    assert response.status_code == 201, "Run was not created"
    assert Run.objects.count() == runs_count + 1, "Run was not created"

@pytest.mark.django_db
def test_not_logged_user_add_run(client):
    data = {
        "name": "Test Run",
        "game": "Test Game",
        "mode": "SPEEDRUN",
        "is_finished": False,
        "session_code": "223"
    }
    response = client.post('/runs/', data, format='json')
    assert response.status_code == 403