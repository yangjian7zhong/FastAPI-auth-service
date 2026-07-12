from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from app.agent.graph import graph
from app.agent.state import AgentState
from app.api.v1.endpoints.auth import get_current_user
from app.models.user import User
from pydantic import BaseModel
import json
import asyncio

router = APIRouter()

class AgentRequest(BaseModel):
    query: str
    stream: bool = True

@router.post("/agent")
async def agent_run(req: AgentRequest, current_user: User = Depends(get_current_user)):
    initial_state = {
        "messages": [{"role": "user", "content": req.query}],
        "current_task": "",
        "tool_results": [],
        "next_agent": "",
        "iteration": 0,
        "final_answer": ""
    }

    if req.stream:
        async def event_stream():
            final_answer = ""
            async for event in graph.astream(initial_state):
                for node, data in event.items():
                    if node == "final_answer":
                        final_answer = data.get("final_answer", "")
                    yield f"data: {json.dumps({'node': node, 'data': data}, ensure_ascii=False)}\n\n"
                await asyncio.sleep(0.01)
            yield f"data: {json.dumps({'node': 'done', 'final_answer': final_answer})}\n\n"
        return StreamingResponse(event_stream(), media_type="text/event-stream")
    else:
        result = await graph.ainvoke(initial_state)
        return {"final_answer": result.get("final_answer", "")}