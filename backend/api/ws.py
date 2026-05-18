from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from queue_manager import QUEUE

router = APIRouter()


@router.websocket("/api/ws")
async def ws(socket: WebSocket):
    await socket.accept()
    q = QUEUE.subscribe()
    try:
        while True:
            msg = await q.get()
            await socket.send_json(msg)
    except WebSocketDisconnect:
        pass
    finally:
        QUEUE.unsubscribe(q)
