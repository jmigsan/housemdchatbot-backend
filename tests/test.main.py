def test_app_creation(app):
    assert app.title == "House MD Chatbot API"

def test_health_endpoint(client):
    response = client.get("/health") 
    assert response.status_code == 200

def test_websocket_connection(client):
    with client.websocket_connect("/api/ws/chat/runpod") as websocket:
        data = websocket.receive_json()
        assert data is not None