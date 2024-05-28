from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging

# Assuming you have your scraper classes implemented as follows
from Google_Image_Scraping.scraper import ImageScraper
from Google_Text_Scraping.scraper import TextScraper
from Google_Video_Scraping.scraper import VideoScraper

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Allow all origins, methods, and headers for CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api")
def root():
    return {"message": "Hello World"}

@app.get("/api/search")
def search(query: str = Query(..., description="Search query")):
    errors = []

    # Scrape images
    try:
        ImageScraper(query)
        logger.info(f"Image scraping successful for query: {query}")
    except Exception as e:
        logger.error(f"Error in Image Scraping for query: {query}, error: {str(e)}")
        errors.append(f"Image Scraping: {str(e)}")

    # Scrape videos
    try:
        VideoScraper(query)
        logger.info(f"Video scraping successful for query: {query}")
    except Exception as e:
        logger.error(f"Error in Video Scraping for query: {query}, error: {str(e)}")
        errors.append(f"Video Scraping: {str(e)}")

    # Scrape text
    try:
        TextScraper(query)
        logger.info(f"Text scraping successful for query: {query}")
    except Exception as e:
        logger.error(f"Error in Text Scraping for query: {query}, error: {str(e)}")
        errors.append(f"Text Scraping: {str(e)}")

    if errors:
        raise HTTPException(status_code=500, detail={"errors": errors})

    return {"message": "Scraping successful", "query": query}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, proxy_headers=True, log_level="debug")
