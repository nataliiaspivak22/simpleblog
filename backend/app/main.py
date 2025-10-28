from fastapi import FastAPI, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from .schemas import Post, PostCreate, Comment, CommentCreate
from .storage import db

app = FastAPI(
    title="Simple Blog API",
    description="A simple blog backend with posts and comments",
    version="1.0.0"
)

# -------------------------
# ✅ Enable CORS
# -------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------
# Posts endpoints
# -------------------------
@app.post("/posts", response_model=Post, status_code=status.HTTP_201_CREATED)
def create_post(payload: PostCreate):
    post = db.create_post(payload)
    return post


@app.get("/posts", response_model=list[Post])
def list_posts(page: int = Query(1, ge=1), limit: int = Query(5, ge=1, le=50)):
    """List posts with pagination"""
    posts_all = list(db._posts.values())
    total_posts = len(posts_all)

    start = (page - 1) * limit
    end = start + limit
    selected = posts_all[start:end]

    for p in selected:
        p.comments = db.list_comments(p.id)

    return selected


@app.get("/posts/{post_id}", response_model=Post)
def get_post(post_id: int):
    post = db.get_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    post.comments = db.list_comments(post.id)
    return post


@app.put("/posts/{post_id}", response_model=Post)
def update_post(post_id: int, payload: PostCreate):
    post = db.update_post(post_id, payload)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    post.comments = db.list_comments(post.id)
    return post


@app.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: int):
    ok = db.delete_post(post_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Post not found")
    return None

# -------------------------
# Comments endpoints
# -------------------------
@app.post("/posts/{post_id}/comments", response_model=Comment, status_code=status.HTTP_201_CREATED)
def create_comment(post_id: int, payload: CommentCreate):
    comment = db.create_comment(post_id, payload)
    if not comment:
        raise HTTPException(status_code=404, detail="Post not found")
    return comment


@app.get("/posts/{post_id}/comments", response_model=list[Comment])
def list_comments(post_id: int):
    if not db.get_post(post_id):
        raise HTTPException(status_code=404, detail="Post not found")
    return db.list_comments(post_id)


@app.get("/posts/{post_id}/comments/{comment_id}", response_model=Comment)
def get_comment(post_id: int, comment_id: int):
    c = db.get_comment(post_id, comment_id)
    if not c:
        raise HTTPException(status_code=404, detail="Comment not found")
    return c


@app.put("/posts/{post_id}/comments/{comment_id}", response_model=Comment)
def update_comment(post_id: int, comment_id: int, payload: CommentCreate):
    c = db.update_comment(post_id, comment_id, payload)
    if not c:
        raise HTTPException(status_code=404, detail="Comment not found")
    return c


@app.delete("/posts/{post_id}/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(post_id: int, comment_id: int):
    ok = db.delete_comment(post_id, comment_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Comment not found")
    return None
