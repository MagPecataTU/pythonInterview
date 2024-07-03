from fastapi import FastAPI,Depends, HTTPException
from playwright.sync_api import sync_playwright
import uuid
from sqlalchemy.orm import Session
from models import CrawlRequest,Base,Screenshot
from datetime import datetime
from db import engine, get_db
app = FastAPI()

Base.metadata.create_all(bind=engine)

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/screenshots")
def craw(request: CrawlRequest,db: Session = Depends(get_db)):
    start_url = request.start_url
    link_number = request.link_number
    screenshotID = uuid.uuid4()

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(start_url)
        screenshot_path = f'screenshots/{screenshotID}.png'
        page.screenshot(path=screenshot_path)

        db_screenshot = Screenshot(
            screenshot_id= screenshotID,
            path= screenshot_path,
            created_at=datetime.now()
        )
        db.add(db_screenshot)
        db.commit()
        db.refresh(db_screenshot)

        links = page.evaluate('''() => {
            return Array.from(document.querySelectorAll('a')).map(a => a.href);
        }''')

        for i in range(link_number):
            page.goto(links[i])
            screenshot_path = f'screenshots/{screenshotID}_{i}.png'
            page.screenshot(path=screenshot_path)
            db_screenshot = Screenshot(
                screenshot_id= screenshotID,
                path= screenshot_path,
                created_at=datetime.now()
            )
            db.add(db_screenshot)
            db.commit()
            db.refresh(db_screenshot)


        browser.close()

    return {"id": screenshotID}

@app.get("/screenshots/{screenshot_id}")
def get_screenshots(screenshot_id: str, db: Session = Depends(get_db)):
    screenshots = db.query(Screenshot).filter(Screenshot.screenshot_id == screenshot_id).all()

    if not screenshots:
        raise HTTPException(status_code=404, detail="Screenshots not found")

    paths = [s.path for s in screenshots]

    return paths

@app.get("/isalive")
def check_status():
    return {"status",200}