from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(title="YouTube Shorts Analytics")

# Allow all origins for now
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "YouTube Shorts API is running!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/channels/trending")
async def get_trending_channels():
    # Mock data for testing
    return [
        {
            "channel_id": "UC123",
            "name": "Example Channel",
            "subs": 15000,
            "growth_14d": 0.25,
            "engagement_rate": 0.045,
            "TrendScore": 0.82,
            "label": "TRENDING",
            "top_keywords": ["gaming", "funny"]
        }
    ]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)