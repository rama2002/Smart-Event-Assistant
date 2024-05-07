from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import feedback, speakers, user,event,interests, user_interests, reporting
import uvicorn

app = FastAPI(debug=True)
trusted_origins = ["http://localhost:3000", "http://10.81.230.210:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=trusted_origins,
    allow_credentials=True,
    allow_methods=["POST", "GET", "PUT", "DELETE"],
    allow_headers=["*"],
)

app.include_router(user.router)
app.include_router(event.router)
app.include_router(interests.router)
app.include_router(user_interests.router)
app.include_router(speakers.router)
app.include_router(feedback.router)
app.include_router(reporting.router)

@app.get("/")
def root():
    return {"message": "Welcome"}

@app.get("/health_check")
def health_check():
    return {"health_check": True}

if __name__ == '__main__':
    uvicorn.run(app=app, host="127.0.0.1", port=8000)