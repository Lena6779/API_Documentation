def test_get_task_by_id(client):
    # Arrange
    created = client.post("/tasks", json={"title": "Walk the dog"}).json()

    # Act
    response = client.get(f"/tasks/{created['id']}")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == created["id"]
    assert data["title"] == "Walk the dog"


def test_get_nonexistent_task_returns_404(client):
    # Arrange
    nonexistent_id = 999

    # Act
    response = client.get(f"/tasks/{nonexistent_id}")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"


def test_patch_task(client):
    # Arrange
    created = client.post(
        "/tasks", json={"title": "Read a book", "description": "Chapter 3"}
    ).json()

    # Act
    response = client.patch(f"/tasks/{created['id']}", json={"completed": True})

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["completed"] is True
    assert data["title"] == "Read a book"
    assert data["description"] == "Chapter 3"


def test_delete_task(client):
    # Arrange
    created = client.post("/tasks", json={"title": "Take out trash"}).json()

    # Act
    response = client.delete(f"/tasks/{created['id']}")

    # Assert
    assert response.status_code == 204
    follow_up = client.get(f"/tasks/{created['id']}")
    assert follow_up.status_code == 404


def test_create_task_invalid_data_returns_422(client):
    # Arrange
    payload = {"title": ""}

    # Act
    response = client.post("/tasks", json=payload)

    # Assert
    assert response.status_code == 422


def test_duplicate_task_title_returns_409(client):
    # Arrange
    payload = {"title": "Pay bills"}
    client.post("/tasks", json=payload)

    # Act
    response = client.post("/tasks", json=payload)

    # Assert
    assert response.status_code == 409
    assert response.json()["detail"] == "A task with this title already exists"


def test_create_task(client):
    # Arrange
    payload = {"title": "Buy groceries", "description": "Milk and eggs"}

    # Act
    response = client.post("/tasks", json=payload)

    # Assert
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Buy groceries"
    assert data["description"] == "Milk and eggs"
    assert data["completed"] is False
    assert "id" in data


def test_list_tasks(client):
    # Arrange
    client.post("/tasks", json={"title": "Task one"})
    client.post("/tasks", json={"title": "Task two"})

    # Act
    response = client.get("/tasks")

    # Assert
    assert response.status_code