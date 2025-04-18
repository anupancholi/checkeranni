from fastapi import FastAPI, Request
from pydantic import BaseModel
import uvicorn
from examples.storm_examples.run_storm_wiki_ollama import main as run_storm_script

import argparse

app = FastAPI()

class PromptInput(BaseModel):
    prompt: str

@app.post("/generate")
async def generate_from_storm(input_data: PromptInput):
    # Use prompt to dynamically run STORMWiki
    # For now we'll just call the `main` with hardcoded args
    args = argparse.Namespace(
        url="http://localhost",
        port=11434,
        model="llama3:latest",
        output_dir="./results/ollama",
        max_thread_num=3,
        retriever="you",
        do_research=True,
        do_generate_outline=True,
        do_generate_article=True,
        do_polish_article=True,
        max_conv_turn=3,
        max_perspective=3,
        search_top_k=3,
        retrieve_top_k=3,
        remove_duplicate=False,
    )
    
    # Pass topic via stdin
    import sys
    from io import StringIO

    sys.stdin = StringIO(input_data.prompt)

    try:
        run_storm_script(args)
        return {"response": f"Article on '{input_data.prompt}' generated successfully."}
    except Exception as e:
        return {"response": f"Error: {str(e)}"}

if __name__ == "__main__":
    uvicorn.run("storm_api:app", host="0.0.0.0", port=11434, reload=True)
