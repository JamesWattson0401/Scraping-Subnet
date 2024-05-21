from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from scraper import Scraper  # Ensure this module is correctly implemented and available

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
    Scraper(query)  # Assuming Scraper returns a result
    return "Success"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, proxy_headers=True, log_level="debug")
