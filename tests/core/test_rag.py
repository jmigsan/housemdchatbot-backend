class _FakeEmbeddings:
    def __init__(self):
        self.calls = []

    def create(self, model, input, encoding_format):
        self.calls.append((model, input, encoding_format))
        return type("Obj", (), {"data": [type("Obj", (), {"embedding": [0.1, 0.2, 0.3]})()]})()


class _FakeDeepInfraClient:
    def __init__(self):
        self.embeddings = _FakeEmbeddings()


class _FakePineconeIndex:
    def __init__(self):
        self.calls = []

    def query(self, **kwargs):
        self.calls.append(kwargs)
        return {
            "matches": [
                {
                    "metadata": {
                        "title": "Foo",
                        "text": "Bar",
                        "source_url": "https://example.com/foo",
                    }
                }
            ]
        }


def test_search_vector_database_no_search(monkeypatch):
    from app.core import rag

    called = {"pinecone": False}

    def fake_pinecone_index():
        called["pinecone"] = True
        return _FakePineconeIndex()

    monkeypatch.setattr(rag, "get_pinecone_index", fake_pinecone_index)

    result = rag.search_vector_database({"requires_search": False, "query": ""})
    assert result == ""
    assert called["pinecone"] is True


def test_search_vector_database_with_results(monkeypatch):
    from app.core import rag

    fake_deepinfra = _FakeDeepInfraClient()
    fake_pinecone = _FakePineconeIndex()

    class FakeAgent:
        def invoke(self, *args, **kwargs):
            return {
                "messages": [
                    type(
                        "Obj",
                        (),
                        {
                            "content": [
                                {
                                    "text": "Title: Foo\nSnippet: Bar\nURL: https://example.com/foo\n"
                                }
                            ]
                        },
                    )()
                ]
            }

    monkeypatch.setattr(rag, "get_deepinfra_client", lambda: fake_deepinfra)
    monkeypatch.setattr(rag, "get_pinecone_index", lambda: fake_pinecone)
    monkeypatch.setattr(
        rag, "get_langgraph_google_gen_ai_model", lambda **kwargs: "fake_model"
    )
    monkeypatch.setattr(rag, "create_agent", lambda *args, **kwargs: FakeAgent())

    result = rag.search_vector_database({"requires_search": True, "query": "cough causes"})

    assert "Title: Foo" in result
    assert "Snippet: Bar" in result
    assert "URL: https://example.com/foo" in result
