from fastapi import FastAPI, Form, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from google.cloud import firestore
from typing import Annotated
import datetime

app = FastAPI()

app.mount("/static", StaticFiles(directory="/app/static"), name="static")
templates = Jinja2Templates(directory="/app/template")

db = firestore.Client()
votes_collection = db.collection("votes")

@app.get("/")
async def read_root(request: Request):
   
    votes = votes_collection.stream()
    vote_data = [v.to_dict() for v in votes]
    
   
    tabs_count = sum(1 for vote in vote_data if vote.get("team") == "TABS")
    spaces_count = sum(1 for vote in vote_data if vote.get("team") == "SPACES")
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "tabs_count": tabs_count,
        "spaces_count": spaces_count,
        "recent_votes": vote_data
    })

@app.post("/")
async def create_vote(team: Annotated[str, Form()]):
    if team not in ["TABS", "SPACES"]:
        raise HTTPException(status_code=400, detail="Invalid vote")

    vote_doc = {
        "team": team,
        "time_cast": datetime.datetime.utcnow().isoformat()
    }
    votes_collection.add(vote_doc)
    
    return {"detail": "Vote recorded successfully!"}
