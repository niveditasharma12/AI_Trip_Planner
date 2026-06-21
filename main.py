from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from Agent.agentic_workflow import GraphBuilder
from utils.save_to_document import save_document
from starlette.responses import JSONResponse
import os
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

# 1. Update your schema to receive the entire conversational array from Streamlit
class QueryRequest(BaseModel):
    messages: List[Dict[str, str]]  # Expects: [{"role": "user", "content": "..."}, ...]

@app.post("/query")
async def query_travel_agent(query: QueryRequest):
    try:
        print(f"Received conversational payload length: {len(query.messages)}")
        
        graph = GraphBuilder(model_provider="groq")
        react_app = graph() 

        # Build the exact message history array for LangGraph
        formatted_messages = []
        for msg in query.messages:
            role = msg["role"]
            content = msg["content"]
            
            # Directly append "user" or "assistant" tuples without string splitting bugs
            if role == "user":
                formatted_messages.append(("user", content))
            elif role == "assistant":
                formatted_messages.append(("assistant", content))

        # Invoke your LangGraph workflow
        input_state = {"messages": formatted_messages}
        output = react_app.invoke(input_state)

        # Safely extract the final message content string
        if isinstance(output, dict) and "messages" in output:
            final_output = output["messages"][-1].content  
        else:
            final_output = str(output)
        
        return {"answer": final_output}
        
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})