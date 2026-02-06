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

    called = {"deepinfra": False, "pinecone": False}

    def fake_deepinfra_client():
        called["deepinfra"] = True
        return _FakeDeepInfraClient()

    def fake_pinecone_index():
        called["pinecone"] = True
        return _FakePineconeIndex()

    monkeypatch.setattr(rag, "get_deepinfra_client", fake_deepinfra_client)
    monkeypatch.setattr(rag, "get_pinecone_index", fake_pinecone_index)

    result = rag.search_vector_database({"requires_search": False, "query": ""})
    assert result == ""
    assert called["deepinfra"] is True
    assert called["pinecone"] is True


def test_search_vector_database_with_results(monkeypatch):
    from app.core import rag

    fake_deepinfra = _FakeDeepInfraClient()
    fake_pinecone = _FakePineconeIndex()

    monkeypatch.setattr(rag, "get_deepinfra_client", lambda: fake_deepinfra)
    monkeypatch.setattr(rag, "get_pinecone_index", lambda: fake_pinecone)

    result = rag.search_vector_database({"requires_search": True, "query": "cough causes"})

    assert "Title: Foo" in result
    assert "Snippet: Bar" in result
    assert "URL: https://example.com/foo" in result
    assert fake_deepinfra.embeddings.calls
    assert fake_pinecone.calls
