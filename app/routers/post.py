from fastapi import Depends, status, HTTPException, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from .. import models, schemas, oauth2
from .. database import get_db

posts_router = APIRouter(
    prefix='/posts',
    tags=['Posts']
)


@posts_router.get('/', response_model=List[schemas.PostOut])
# dependency needed to make any db operations
def get_posts(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user), limit: int = 10, offset: int = 0, search: Optional[str] = ""):
    # db.query(models.Post) - behind the scenes this is an SQL query

    # posts_query = db.query(models.Post).filter(
    #     models.Post.user_id == current_user.id,
    #     models.Post.title.ilike(f'%{search}%')
    # ).limit(limit).offset(offset)
    # posts = posts_query.all()

    # by default "join" is an inner join
    # add isouter=True to make it left outer join

    # SQL Query: SELECT posts.*, COUNT(votes.post_id) AS likes FROM posts LEFT JOIN votes ON posts.id = votes.post_id WHERE post.id = 9 GROUP BY posts.id;
    posts_query = db.query(models.Post, func.count(models.Vote.post_id).label('votes')).join(
        models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(
            models.Post.id).filter(
                models.Post.title.ilike(f'%{search}%')).limit(limit).offset(offset)
    posts = posts_query.all()

    return posts


@posts_router.get('/{id}', response_model=schemas.PostOut)
def get_post_details(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # post = db.query(models.Post).filter(models.Post.id == id).first()

    post_query = db.query(models.Post, func.count(models.Vote.post_id).label('votes')).join(
        models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(
            models.Post.id).filter(models.Post.id == id)
    post = post_query.first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Post with id {id} does not exist')

    if post.Post.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='Not authorized to perform requested action')

    return post


@posts_router.post('/', status_code=status.HTTP_201_CREATED, response_model=schemas.PostResponse)
def create_post(post: schemas.PostCreate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # new_post = models.Post(
    #     title=post.title, content=post.content, published=post.published)

    # will destructure/unpack based on the "Post" model from models
    new_post = models.Post(user_id=current_user.id, **post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post


@posts_router.put('/{id}', status_code=status.HTTP_205_RESET_CONTENT, response_model=schemas.PostResponse)
def update_post(id: int, updated_post: schemas.PostCreate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()

    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Post with id {id} does not exist')

    if post_query.first().user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='Not authorized to perform requested action')

    # Hard coded
    # post_query.update({'title': 'updated title',
    #                   'content': 'updated content'}, synchronize_session=False)

    post_query.update(updated_post.dict(), synchronize_session=False)

    db.commit()

    return post_query.first()


@posts_router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    post_query = db.query(models.Post).filter(models.Post.id == id)

    if post_query.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Post with id {id} does not exist')

    if post_query.first().user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='Not authorized to perform requested action')

    post_query.delete(synchronize_session=False)
    db.commit()
