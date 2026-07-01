from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app import models  # noqa: F401 (registers tables with Base.metadata)
from app.database import Base, engine
from app.routers import github, mood, todos, weather

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Daily Dashboard")

app.include_router(weather.router)
app.include_router(todos.router)
app.include_router(github.router)
app.include_router(mood.router)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")


@app.get("/")
def index(request: Request):
    return templates.TemplateResponse(request, "index.html")
