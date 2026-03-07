from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import RedirectResponse
import uvicorn
import core
import models_api
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI()
db = {}

@app.post("/links/shorten", response_model=models_api.LinkCreationResponse)
def create_shorten_link(link_data: models_api.LinkCreationRequest):
    short_code = core.generate_short_code()
    data = core.add_new_link_to_db(db, link_data.url, short_code)
    logger.info(f"Created short code '{short_code}' for original URL '{link_data.url}'")
    return models_api.LinkCreationResponse(
        short_code=short_code,
        original_url=link_data.url,
        creation_date=data['creation_date']
    )

@app.get("/links/{short_code}")
def get_original_url_content(short_code: str):
    logger.info(f"Try get original URL by '{short_code}'")
    original_url = core.get_original_url_from_db(db, short_code)
    if original_url is None:
        raise HTTPException(status_code=404, detail="Short code not found")
    logger.info(f"Redirect to '{original_url}'")
    return RedirectResponse(original_url)

@app.delete("/links/{short_code}")
def delete_short_code(short_code: str):
    core.delete_short_code_from_db(db, short_code)
    return 

@app.put("/links/{short_code}", response_model=models_api.LinkCreationResponse)
def update_url_by_short_code(short_code: str, link_data: models_api.LinkCreationRequest):
    data = core.update_url_in_db(db, short_code, link_data.url)
    if data is None:
        raise HTTPException(status_code=404, detail="Short code not found")
    return models_api.LinkCreationResponse(
        short_code=short_code,
        original_url=link_data.url,
        creation_date=data['creation_date']
    )


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True, host="0.0.0.0", log_level="info")
