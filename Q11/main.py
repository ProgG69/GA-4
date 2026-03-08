from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

app = FastAPI()
This is almost certainly a CORS error in disguise — the assignment's evaluation tool (running in a browser) is being blocked from calling your Render API. Here's exactly how to fix it.
The Root Cause

When a browser (or browser-based evaluator) sends a request to your API from a different origin (a different website/domain), it first sends a "preflight" check. Without CORS headers in your FastAPI app, Render rejects it and the browser reports it as a NetworkError.
The Fix: Add CORS Middleware

Update your main.py to include CORSMiddleware with allow_origins=["*"]. This tells the browser "yes, anyone can call this API."​

Replace your entire main.py with this:

python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

app = FastAPI()

# ✅ ADD THIS BLOCK — fixes the NetworkError
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],        # Allow POST, GET, OPTIONS, etc.
    allow_headers=["*"],        # Allow all headers
)

# --- Step A: Define what the INPUT looks like ---
class SentimentRequest(BaseModel):
    sentences: List[str]

# --- Step B: Define what ONE result looks like ---
class SentimentResult(BaseModel):
    sentence: str
    sentiment: str

# --- Step C: Define what the OUTPUT looks like ---
class SentimentResponse(BaseModel):
    results: List[SentimentResult]

# --- Step D: Keyword lists for rule-based analysis ---
HAPPY_WORDS = [
    "love", "great", "amazing", "awesome", "excellent", "good", "happy",
    "fantastic", "wonderful", "best", "beautiful", "joy", "excited",
    "glad", "pleased", "enjoy", "like", "brilliant", "superb", "perfect",
    "delightful", "grateful", "thankful", "positive", "fun", "nice"
]

SAD_WORDS = [
    "hate", "terrible", "awful", "bad", "sad", "horrible", "worst",
    "disgusting", "ugly", "angry", "upset", "disappoint", "disappoint",
    "frustrated", "miserable", "dreadful", "annoying", "boring", "fail",
    "failure", "poor", "useless", "broken", "wrong", "unhappy", "depressed",
    "hurt", "painful", "loss", "unfortunately", "regret", "sorry"
]

# --- Step E: The function that decides the sentiment ---
def analyze_sentiment(sentence: str) -> str:
    lower = sentence.lower()  # Make it lowercase so "LOVE" matches "love"
    
    happy_score = sum(1 for word in HAPPY_WORDS if word in lower)
    sad_score = sum(1 for word in SAD_WORDS if word in lower)
    
    if happy_score > sad_score:
        return "happy"
    elif sad_score > happy_score:
        return "sad"
    else:
        return "neutral"

# --- Step F: The actual API endpoint ---
@app.post("/sentiment", response_model=SentimentResponse)
def get_sentiment(request: SentimentRequest):
    results = []
    for sentence in request.sentences:
        sentiment = analyze_sentiment(sentence)
        results.append(SentimentResult(sentence=sentence, sentiment=sentiment))
    return SentimentResponse(results=results)

