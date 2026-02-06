from app.schemas.chat import Message


class _FakeGeminiResponse:
    def __init__(self, text):
        self.text = text


class _FakeGeminiModels:
    def __init__(self, response_text):
        self._response_text = response_text

    def generate_content(self, *args, **kwargs):
        return _FakeGeminiResponse(self._response_text)


class _FakeGeminiClient:
    def __init__(self, response_text):
        self.models = _FakeGeminiModels(response_text)


class _FakeHousemdCompletions:
    def create(self, *args, **kwargs):
        message = type("Obj", (), {"content": kwargs["messages"][-1]["content"] + " <think>noise</think>"})()
        choice = type("Obj", (), {"message": message})()
        return type("Obj", (), {"choices": [choice]})()


class _FakeHousemdClient:
    def __init__(self):
        self.chat = type("Obj", (), {"completions": _FakeHousemdCompletions()})()


def test_generate_vector_query(monkeypatch):
    from app.core import llm

    fake_client = _FakeGeminiClient('{"requires_search": true, "query": "cough causes"}')
    monkeypatch.setattr(llm, "get_gemini_client", lambda: fake_client)

    data = Message(role="user", content="I have a cough", timestamp="2026-02-05T00:00:00Z")
    messages = [Message(role="model", content="Hi", timestamp="2026-02-05T00:00:00Z")]

    result = llm.generate_vector_query(data, messages)

    assert result["requires_search"] is True
    assert result["query"] == "cough causes"


def test_generate_housemd_response_strips_think(monkeypatch):
    from app.core import llm

    monkeypatch.setattr(llm, "get_housemd_client", lambda: _FakeHousemdClient())

    data = Message(role="user", content="I have a cough", timestamp="2026-02-05T00:00:00Z")
    messages = [Message(role="model", content="Hi", timestamp="2026-02-05T00:00:00Z")]

    result = llm.generate_housemd_response("db", data, messages)

    assert "<think>" not in result
    assert result.endswith("</user_question>")
