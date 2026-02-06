def test_chat_websocket_flow(client, monkeypatch):

    def fake_now_iso():
        return "2026-02-05T12:00:00Z"

    def fake_generate_vector_query(data, messages):
        return {"requires_search": True, "query": "cough causes"}

    def fake_search_vector_database(vector_query):
        return "Title: Example\nSnippet: Example snippet\nURL: https://example.com"

    def fake_generate_housemd_response(database_search_results, data, messages):
        return "It's probably lupus. It's never lupus."

    monkeypatch.setattr("app.api.websocket.now_iso", fake_now_iso)
    monkeypatch.setattr("app.api.websocket.generate_vector_query", fake_generate_vector_query)
    monkeypatch.setattr("app.api.websocket.search_vector_database", fake_search_vector_database)
    monkeypatch.setattr("app.api.websocket.generate_housemd_response", fake_generate_housemd_response)

    with client.websocket_connect("/api/ws/chat/runpod") as websocket:
        websocket.send_json(
            {
                "role": "user",
                "content": "I have a cough.",
                "timestamp": "2026-02-05T12:00:00Z",
            }
        )
        data = websocket.receive_json()

    assert data["role"] == "model"
    assert data["content"] == "It's probably lupus. It's never lupus."
    assert data["timestamp"] == "2026-02-05T12:00:00Z"
