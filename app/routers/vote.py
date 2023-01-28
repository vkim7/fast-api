from fastapi import Depends, status, HTTPException, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from .. import models, schemas, oauth2
from .. database import get_db

votes_router = APIRouter(
    prefix='/votes',
    tags=['Votes']
)


@votes_router.get('/')
def get_votes(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    votes_query = db.query(models.Vote)
    return votes_query.all()


@votes_router.post('/', status_code=status.HTTP_201_CREATED)
def vote(vote: schemas.VoteBase, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

    post = db.query(models.Post).filter(
        models.Post.id == vote.post_id
    ).first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Post with id {vote.post_id} does not exist')

    vote_query = db.query(models.Vote).filter(
        models.Vote.post_id == vote.post_id,
        models.Vote.user_id == current_user.id
    )
    found_vote = vote_query.first()

    if vote.dir == 1:
        if found_vote:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail=f'User {current_user.id} has already voted on the post {vote.post_id}')
        new_vote = models.Vote(post_id=vote.post_id, user_id=current_user.id)
        db.add(new_vote)
        db.commit()

        return {'message': 'Successfully added vote'}
    else:
        if not found_vote:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail='Vote does not exist')

        vote_query.delete(synchronize_session=False)
        db.commit()

        return {'message': 'Successfully deleted vote'}
