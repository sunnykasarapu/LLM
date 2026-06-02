
import asyncio

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.db import SessionLocal
from app.repositories import EvaluationRepository

router = APIRouter()


@router.websocket("/ws/evaluations")
async def evaluation_updates(websocket: WebSocket) -> None:
    await websocket.accept()
    try:
        while True:
            db = SessionLocal()
            try:
                runs = EvaluationRepository(db).list_runs()
                await websocket.send_json(
                    [
                        {
                            "id": run.id,
                            "name": run.name,
                            "status": run.status.value,
                            "progress": run.progress,
                            "aggregate_score": run.aggregate_score,
                            "provider": run.provider,
                            "model_version": run.model_version,
                        }
                        for run in runs[:20]
                    ]
                )
            finally:
                db.close()
            await asyncio.sleep(2)
    except WebSocketDisconnect:
        return

