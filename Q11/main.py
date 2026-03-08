from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SentimentRequest(BaseModel):
    sentences: List[str]

class SentimentResult(BaseModel):
    sentence: str
    sentiment: str

class SentimentResponse(BaseModel):
    results: List[SentimentResult]

HAPPY_WORDS = [
    # Direct positive emotions
    "love", "loved", "loving", "like", "liked",
    "happy", "happiness", "glad", "joyful", "joy", "joyous",
    "excited", "exciting", "excitement", "thrilled", "thrill",
    "great", "greatest", "good", "better", "best",
    "amazing", "awesome", "fantastic", "wonderful", "brilliant",
    "excellent", "superb", "perfect", "outstanding", "fabulous",
    "beautiful", "gorgeous", "delightful", "pleasant", "pleasing",
    "pleased", "cheerful", "positive", "fun", "funny", "smile",
    "smiling", "laugh", "laughing", "celebrate", "celebrating",
    "win", "won", "winning", "success", "successful", "achieve",
    "achieved", "proud", "grateful", "thankful", "blessed",
    "enjoy", "enjoyed", "enjoying", "enjoyable", "nice",
    "incredible", "marvelous", "lovely", "charming", "yay",
    "hooray", "congrats", "congratulations", "recommend",
    "impressive", "satisfied", "satisfying", "content", "lucky",
    "paradise", "heaven", "dream", "hope", "hopeful", "optimistic",
    "energetic", "enthusiastic", "eager", "adore", "treasure"
]

SAD_WORDS = [
    # Direct negative emotions
    "hate", "hated", "hating", "dislike", "disliked",
    "sad", "sadness", "unhappy", "depressed", "depression",
    "miserable", "misery", "awful", "terrible", "horrible",
    "dreadful", "disgusting", "disgust", "gross", "nasty",
    "bad", "worse", "worst", "poor", "weak",
    "angry", "anger", "furious", "rage", "mad",
    "upset", "disappointed", "disappointing", "disappointment",
    "frustrated", "frustrating", "frustration", "annoyed", "annoying",
    "boring", "bored", "boredom", "dull", "tedious",
    "useless", "worthless", "pointless", "hopeless", "helpless",
    "broken", "damaged", "ruined", "destroyed", "failed",
    "fail", "failure", "lose", "lost", "losing", "loss",
    "pain", "painful", "hurt", "hurting", "ache",
    "sick", "ill", "unwell", "dying", "dead",
    "cry", "crying", "cried", "tears", "weep", "weeping",
    "regret", "regretful", "sorry", "apologize", "apology",
    "wrong", "mistake", "error", "disaster", "catastrophe",
    "problem", "trouble", "difficult", "difficulty", "struggle",
    "unfortunately", "sadly", "tragically", "never", "never again",
    "lonely", "alone", "abandoned", "rejected", "betrayed",
    "scared", "fearful", "afraid", "terrified", "anxious",
    "anxiety", "worried", "worry", "stress", "stressed",
    "exhausted", "tired", "drained", "overwhelmed", "suffocating",
    "hate it", "can't stand", "waste", "wasted", "give up"
]

# Negation words that FLIP the sentiment
NEGATIONS = ["not", "no", "never", "don't", "doesn't", "didn't",
             "isn't", "aren't", "wasn't", "weren't", "can't",
             "cannot", "couldn't", "won't", "wouldn't", "hardly",
             "barely", "neither", "nor"]

def analyze_sentiment(sentence: str) -> str:
    lower = sentence.lower()
    words = lower.split()

    happy_score = 0
    sad_score = 0

    for i, word in enumerate(words):
        # Check if there's a negation within 2 words before this word
        negated = any(words[j] in NEGATIONS for j in range(max(0, i - 2), i))

        # Check multi-word phrases first
        bigram = " ".join(words[i:i+2]) if i + 1 < len(words) else ""

        if bigram in HAPPY_WORDS or word in HAPPY_WORDS or any(hw in lower for hw in ["love", "enjoy", "happy", "great", "amazing", "awesome"]):
            matched_happy = word in HAPPY_WORDS or bigram in HAPPY_WORDS
            if matched_happy:
                if negated:
                    sad_score += 1
                else:
                    happy_score += 1

        if word in SAD_WORDS or bigram in SAD_WORDS:
            if negated:
                happy_score += 1
            else:
                sad_score += 1

    # Re-scan with full phrase matching for multi-word sad phrases
    for phrase in ["hate it", "can't stand", "give up", "never again"]:
        if phrase in lower:
            sad_score += 2

    # Fallback: check if any happy/sad word appears as substring
    if happy_score == 0 and sad_score == 0:
        for hw in HAPPY_WORDS:
            if hw in lower:
                happy_score += 1
                break
        for sw in SAD_WORDS:
            if sw in lower:
                sad_score += 1
                break

    if happy_score > sad_score:
        return "happy"
    elif sad_score > happy_score:
        return "sad"
    else:
        return "neutral"

@app.post("/sentiment", response_model=SentimentResponse)
def get_sentiment(request: SentimentRequest):
    results = []
    for sentence in request.sentences:
        sentiment = analyze_sentiment(sentence)
        results.append(SentimentResult(sentence=sentence, sentiment=sentiment))
    return SentimentResponse(results=results)
