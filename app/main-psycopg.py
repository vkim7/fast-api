from . import models
import time
from psycopg2.extras import RealDictCursor
import psycopg2
from random import randrange
from typing import Optional
from pydantic import BaseModel
from fastapi.params import Body
from fastapi import FastAPI, Response, status, HTTPException

# # Execute a query
# cursor.execute("SELECT * FROM post")
# # Retrieve query results
# records = cursor.fetchall()

app = FastAPI()

# cursor.execute - all changes are staged changed, not committed to db
# conn.commit()  - commits changes to db
# assigning int values to SQL query wouldn't work, convert them into strings
while True:
    try:
        # Connect to your postgres DB
        conn = psycopg2.connect(host='localhost', database='db_name',
                                user='vladimirkim', cursor_factory=RealDictCursor)
        # Open a cursor to perform database operations
        cursor = conn.cursor()
        print('Database connection was successfull')
        break
    except Exception as error:
        time.sleep(2)
        print('Connecting to database failed', error)


# pydantic can be used with any other python application
# Schema defines what the data should look like

class Post(BaseModel):
    title: str
    content: str
    published: bool = True


local_db = [
    {'id': 1, 'title': 'Title one', 'content': 'Content One'},
    {'id': 2, 'title': 'Title two', 'content': 'Content Two'}
]


def find_post(id):
    for post in local_db:
        if post['id'] == id:
            return post


@app.get("/")
async def root():
    return {'message': 'Welcome to my API'}


# Get List
@app.get('/posts')
def get_posts():
    cursor.execute('''SELECT * FROM post''')
    posts = cursor.fetchall()
    return {'data': posts}

# Get Details


@app.get('/posts/{id}')  # {id} - path parameter
def get_post(id: int, response: Response):  # providing :int - automatically converts str to int
    cursor.execute('''SELECT * FROM post WHERE id=%s''', (str(id)))
    post = cursor.fetchone()

    # updating response's status code
    if not post:
        # option 1
        # response.status_code = status.HTTP_404_NOT_FOUND
        # return {'message': f'Post with id {id} was not found.'}

        # option 2
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Post with id {id} was not found.')

    return {'data': post}

# Create Post


@app.post('/posts', status_code=status.HTTP_201_CREATED)
# def create_post(payload: dict = Body(...)):
def create_post(payload: Post):
    cursor.execute('''INSERT INTO post(title, content, published) VALUES(%s, %s, %s) RETURNING*''',
                   (payload.title, payload.content, payload.published))
    new_post = cursor.fetchone()
    conn.commit()
    # post_dict = payload.dict()
    # post_dict['id'] = randrange(3, 100000)  # from inclusive, to exclusive
    # local_db.append(post_dict)
    return {'data': new_post}


# Update post
@app.put('/posts/{id}', status_code=status.HTTP_205_RESET_CONTENT)
def update_post(id: int, payload: Post):
    cursor.execute('''UPDATE post SET title=%s, content=%s, published=%s WHERE id=%s RETURNING *''',
                   (payload.title, payload.content, payload.published, str(id)))
    updated_post = cursor.fetchone()
    conn.commit()

    if updated_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Post with id {id} does not exist')

    return {'data': updated_post}


def find_index(id: int):
    for idx, post in enumerate(local_db):
        if post['id'] == id:
            return idx
    return None


# Delete
@app.delete('/posts/{id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):

    cursor.execute('''DELETE FROM post WHERE id=%s RETURNING *''', (str(id),))
    deleted_post = cursor.fetchone()
    conn.commit()

    if deleted_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Post with id {id} does not exist')
