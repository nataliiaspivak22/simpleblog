from datetime import datetime
from typing import List
from .schemas import Post, PostCreate, Comment, CommentCreate

class InMemoryDB:
    def __init__(self):
        self._posts = {}
        self._comments = {}
        self._next_post = 1
        self._next_comment = 1

    # Posts
    def create_post(self, payload: PostCreate) -> Post:
        post = Post(id=self._next_post, title=payload.title, body=payload.body, comments=[], created_at=datetime.now())
        self._posts[self._next_post] = post
        self._next_post += 1
        return post

    def get_post(self, post_id: int) -> Post | None:
        return self._posts.get(post_id)

    def update_post(self, post_id: int, payload: PostCreate) -> Post | None:
        post = self._posts.get(post_id)
        if not post:
            return None
        post.title = payload.title
        post.body = payload.body
        return post

    def delete_post(self, post_id: int) -> bool:
        if post_id in self._posts:
            # delete comments belonging to this post
            to_delete = [cid for cid, c in self._comments.items() if c.post_id == post_id]
            for cid in to_delete:
                del self._comments[cid]
            del self._posts[post_id]
            return True
        return False

    # Comments
    def list_comments(self, post_id: int) -> List[Comment]:
        return [c for c in self._comments.values() if c.post_id == post_id]

    def create_comment(self, post_id: int, payload: CommentCreate) -> Comment | None:
        if post_id not in self._posts:
            return None
        comment = Comment(id=self._next_comment, post_id=post_id, author=payload.author, content=payload.content, created_at=datetime.now())
        self._comments[self._next_comment] = comment
        self._next_comment += 1
        return comment

    def get_comment(self, post_id: int, comment_id: int) -> Comment | None:
        c = self._comments.get(comment_id)
        if not c or c.post_id != post_id:
            return None
        return c

    def update_comment(self, post_id: int, comment_id: int, payload: CommentCreate) -> Comment | None:
        c = self.get_comment(post_id, comment_id)
        if not c:
            return None
        c.author = payload.author
        c.content = payload.content
        return c

    def delete_comment(self, post_id: int, comment_id: int) -> bool:
        c = self.get_comment(post_id, comment_id)
        if not c:
            return False
        del self._comments[comment_id]
        return True

db = InMemoryDB()
