def test_create_task(client, auth_headers):
    proj = client.post("/projects/", json={
        "name": "Test Project",
        "description": "For testing"
    }, headers=auth_headers)
    assert proj.status_code == 200

    response = client.post("/tasks/", json={
        "title": "Test Task",
        "description": None,
        "due_date": None,
        "assignee_id": None,
        "project_id": proj.json()["id"]
    }, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["title"] == "Test Task"


def test_get_tasks(client, auth_headers):
    # Create project + task first so list is non-empty
    proj = client.post("/projects/", json={
        "name": "Test Project",
        "description": "For testing"
    }, headers=auth_headers)

    client.post("/tasks/", json={
        "title": "Task 1",
        "description": None,
        "due_date": None,
        "assignee_id": None,
        "project_id": proj.json()["id"]
    }, headers=auth_headers)

    response = client.get("/tasks/", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0


def test_create_task_invalid_project(client, auth_headers):
    response = client.post("/tasks/", json={
        "title": "Ghost Task",
        "description": None,
        "due_date": None,
        "assignee_id": None,
        "project_id": 9999
    }, headers=auth_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Project not found or not yours"