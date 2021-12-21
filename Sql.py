from typing import Optional
from fastapi import FastAPI, Response, status, HTTPException
from fastapi.params import Body
from pydantic import BaseModel
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time

app = FastAPI()


class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    # rating: Optional[int]= None


while True:
    try:
        conn = psycopg2.connect(host='localhost', database='fastapi', user='postgres',
                                password='1234', cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print("Connection established")
        break
    except Exception as error:
        print("Connection failed")
        print("Error", error)
        time.sleep(2)

my_posts = [{"title": "title of post 1", "content": "content of post 1", "id": 1},
            {"title": "Favorite foods", "content": "I like home cooked food", "id": 2}]


def find_post(id):
    for p in my_posts:
        if p["id"] == id:
            return p


def find_index(id):
    for i, p in enumerate(my_posts):
        if p['id'] == id:
            return i


@app.get("/")
def root():
    return {"message": "Welcome to my API"}


@app.get("/posts")
def posts():
    cursor.execute("""select * from posts""")
    posts = cursor.fetchall()
    return {"data": posts}


@app.post("/posts", status_code=status.HTTP_201_CREATED)
def createpost(post: Post):
    cursor.execute("""insert into posts (title,content,published) values (%s,%s,%s) returning *""",
                   (post.title, post.content, post.published))
    new_post = cursor.fetchone()
    conn.commit()
    return {"data ": new_post}


@app.get("/posts/{id}")
def get_post(id: int, res: Response):
    cursor.execute("""select * from posts where id = %s""", (str(id),))
    tpost = cursor.fetchone()
    print(tpost)
    post = find_post(id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id: {id} was not found")
        # res.status_code=status.HTTP_404_NOT_FOUND
        # return {"Error":f"Post with id: {id} was not found"}
    return {"Post_detail": tpost}


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    cursor.execute("""delete from posts where id=%s returning *""", (str(id),))
    dpost = cursor.fetchone()
    conn.commit()
    if dpost is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} does not exist")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/posts/{id}")
def update_post(id: int, post: Post):
    cursor.execute("""update posts set title=%s, content=%s,published=%s where id=%s returning *""",
                   (post.title, post.content, post.published, str(id)))
    upost = cursor.fetchone()
    conn.commit()
    if upost is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} does not exist")

    return {"data": upost}
