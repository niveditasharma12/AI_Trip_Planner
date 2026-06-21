from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from Agent.agentic_workflow import GraphBuilder
from utils.save_to_document import save_document
from starlette.responses import JSONResponse
import os
import json
import datetime
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import List, Dict

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    messages: List[Dict[str, str]]

@app.post("/query")
async def query_travel_agent(query: QueryRequest):
    try:
        print(f"Received conversational payload length: {len(query.messages)}")

        graph = GraphBuilder(model_provider="groq")
        react_app = graph()

        formatted_messages = []
        for msg in query.messages:
            role = msg["role"]
            content = msg["content"]
            if role == "user":
                formatted_messages.append(("user", content))
            elif role == "assistant":
                formatted_messages.append(("assistant", content))

        input_state = {"messages": formatted_messages}
        output = react_app.invoke(input_state)

        if isinstance(output, dict) and "messages" in output:
            final_output = output["messages"][-1].content
        else:
            final_output = str(output)

        # Stream word by word
        def word_streamer():
            words = final_output.split(" ")
            for i, word in enumerate(words):
                chunk = word if i == len(words) - 1 else word + " "
                yield f"data: {json.dumps({'word': chunk})}\n\n"
            yield "data: [DONE]\n\n"

        return StreamingResponse(word_streamer(), media_type="text/event-stream")

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})