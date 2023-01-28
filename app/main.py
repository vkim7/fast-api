from fastapi import FastAPI
from .database import engine
from .routers import post, user, auth, vote
from . import models
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
# Limitations
# sqlalchemy - will not make changes to tables on the go, once table is created
# alembic is used for that

# REPLACED with alembic
# models.Base.metadata.create_all(bind=engine)

# allow all
# origins = ['*']

origins = [
    'http://localhost:4200'
]

# middlewares are hit before routers
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(post.posts_router)
app.include_router(user.users_router)
app.include_router(vote.votes_router)
app.include_router(auth.router)
