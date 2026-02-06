from fastapi import APIRouter, WebSocket
from starlette.websockets import WebSocketState
from app.core.utils.house import random_house_thinking_reply
from app.schemas.chat import Message
from app.core.utils.datetime import now_iso
from app.core.llm import generate_vector_query, generate_housemd_response
from app.core.rag import search_vector_database
from app.core.utils.websocket_helpers import handle_websocket_exception, ValidatedWebSocket

router = APIRouter()

@router.websocket('/api/ws/chat/runpod')
async def chat_websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    ws = ValidatedWebSocket(websocket, Message)

    messages: list[Message] = []

    initialMessage: Message = Message(
        role="model",
        content="If you're here to ask for directions, you're at the wrong place. If you're here to ask me for a doctor, you're also at the wrong place.",
        timestamp=now_iso()
    )
    messages.append(initialMessage)

    try:
        while True:
            data = await ws.receive_validated()
            messages.append(data)

            # Get time now
            time_now_iso = now_iso()

            # Create good search term for RAG
            vector_query = generate_vector_query(data, messages)

            database_search_results = ''

            if vector_query['requires_search']:
                # Give the user a message, so they can wait for RAG to finish
                thinking_response = random_house_thinking_reply()

                messages.append(Message(role="model", content=thinking_response, timestamp=time_now_iso))

                await websocket.send_json(
                    {
                        "role": "model",
                        "content": thinking_response,
                        "timestamp": time_now_iso
                    }
                )

                # Actually look in RAG
                database_search_results = search_vector_database(vector_query)


            # Get House to say something
            response = generate_housemd_response(database_search_results, data, messages)

            # Add response to messages
            messages.append(Message(role="model", content=response, timestamp=time_now_iso))

            await websocket.send_json(
                {
                    "role": "model",
                    "content": response,
                    "timestamp": time_now_iso
                }
            )

    except Exception as e:
        handle_websocket_exception(ws, e)

    finally:
        if websocket.client_state != WebSocketState.DISCONNECTED:
            await ws.close()
