import os
import streamlit as st
import requests
import time
from datetime import datetime

def format_datetime(dt_str: str) -> str:
    """Перетворює ISO-дату на формат DD.MM.YYYY HH:MM"""
    try:
        dt = datetime.fromisoformat(dt_str)
        return dt.strftime("%d.%m.%Y %H:%M")
    except Exception:
        return dt_str

# =========================
# Settings
# =========================
host = os.getenv("BACKEND_HOST")
port = os.getenv("BACKEND_PORT")

if not host or not port:
    raise RuntimeError("❌ Environment variables BACKEND_HOST or BACKEND_PORT are not set!")

BACKEND_URL = f"http://{host}:{port}"

st.set_page_config(page_title="📝 Simple Blog", layout="wide")
st.title("📝 Simple Blog")

# =========================
# Session state
# =========================
for key, default in {
    "refresh_counter": 0,
    "view_post": None,
    "edit_post": None,
    "edit_comment": None,
    "page": 1,
    "page_size": 5,  # скільки постів показувати на сторінці
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# =========================
# Helpers
# =========================
def trigger_refresh(delay: float = 0.9):
    """Збільшує лічильник, щоб оновити сторінку"""
    time.sleep(delay)
    st.session_state.refresh_counter += 1
    st.rerun()

def show_toast(msg, color="#4CAF50", duration=3):
    """Показує повідомлення (використовує toast якщо доступно)"""
    if hasattr(st, "toast"):
        st.toast(msg)
    else:
        toast = st.empty()
        toast.markdown(
            f"<div style='color:white; background-color:{color}; padding:10px; border-radius:5px;'>{msg}</div>",
            unsafe_allow_html=True,
        )
        time.sleep(duration)
        toast.empty()

# =========================
# Create new post
# =========================
with st.expander("➕ Create new post"):
    with st.form("new_post_form", clear_on_submit=True):
        title = st.text_input("Title")
        body = st.text_area("Body")
        submitted = st.form_submit_button("Create")
        if submitted:
            if not title or not body:
                show_toast("Title and body are required!", color="#f44336")
            else:
                r = requests.post(f"{BACKEND_URL}/posts", json={"title": title, "body": body})
                if r.status_code == 201:
                    show_toast("Post created!", color="#4CAF50")
                    trigger_refresh()
                else:
                    show_toast(f"Error: {r.status_code}", color="#f44336")

# =========================
# Posts container with pagination
# =========================
posts_container = st.container()
with posts_container:
    st.header("📚 Posts")

    page = st.session_state["page"]
    page_size = st.session_state["page_size"]

    try:
        resp = requests.get(f"{BACKEND_URL}/posts?page={page}&limit={page_size}")
        resp.raise_for_status()
        posts = resp.json()
    except Exception as e:
        st.error(f"Cannot load posts: {e}")
        posts = []

    # Відображення постів
    if posts:
        for p in posts:
            comment_count = len(p.get("comments", []))
            st.subheader(p["title"])
            st.caption(f"🕓 Created at: {format_datetime(p.get('created_at', ''))}")
            st.write(p["body"])
            cols = st.columns([1, 1, 1, 2])
            with cols[0]:
                if st.button(f"View", key=f"view-{p['id']}"):
                    st.session_state.update(view_post=p["id"], edit_post=None, edit_comment=None)
                    trigger_refresh(0)
            with cols[1]:
                if st.button(f"Edit", key=f"edit-{p['id']}"):
                    st.session_state.update(edit_post=p["id"], view_post=None, edit_comment=None)
                    trigger_refresh(0)
            with cols[2]:
                if st.button(f"Delete", key=f"del-{p['id']}"):
                    d = requests.delete(f"{BACKEND_URL}/posts/{p['id']}")
                    if d.status_code == 204:
                        show_toast("Post deleted", color="#f44336")
                        trigger_refresh()
                    else:
                        show_toast(f"Delete error: {d.status_code}", color="#f44336")
            with cols[3]:
                st.write(f"Comments ({comment_count})")
    else:
        st.info("No posts found.")

    # Pagination buttons
    col1, col2, col3 = st.columns([1, 1, 5])
    with col1:
        if page > 1 and st.button("⬅ Previous"):
            st.session_state["page"] -= 1
            trigger_refresh(0)
    with col2:
        if len(posts) == page_size:
            if st.button("Next ➡"):
             st.session_state["page"] += 1
             trigger_refresh(0)
        else:
            st.write("")

    with col3:
        st.write(f"Page {page}")

# =========================
# Edit post
# =========================
if st.session_state["edit_post"]:
    post_id = st.session_state["edit_post"]
    st.markdown("---")
    st.header("✏️ Edit Post")

    try:
        r = requests.get(f"{BACKEND_URL}/posts/{post_id}")
        r.raise_for_status()
        post = r.json()
    except Exception as e:
        st.error(f"Cannot load post: {e}")
        post = None

    if post:
        with st.form(f"edit_post_form_{post_id}"):
            new_title = st.text_input("Title", value=post["title"])
            new_body = st.text_area("Body", value=post["body"])
            submitted = st.form_submit_button("Save changes")
            if submitted:
                u = requests.put(f"{BACKEND_URL}/posts/{post_id}", json={"title": new_title, "body": new_body})
                if u.status_code == 200:
                    show_toast("Post updated!", color="#2196F3")
                    st.session_state["edit_post"] = None
                    trigger_refresh()
                else:
                    show_toast(f"Update failed: {u.status_code}", color="#f44336")

# =========================
# View post details + comments
# =========================
post_id = st.session_state.get("view_post")
if post_id:
    st.markdown("---")
    st.header("📄 Post details")
    try:
        r = requests.get(f"{BACKEND_URL}/posts/{post_id}")
        r.raise_for_status()
        pd = r.json()
    except Exception as e:
        st.error(f"Cannot load post: {e}")
        pd = None

    if pd:
        comment_count = len(pd.get("comments", []))
        st.subheader(pd["title"])
        st.caption(f"🕓 Created at: {format_datetime(p.get('created_at', ''))}")
        st.write(pd["body"])
        st.write(f"Comments ({comment_count})")

        # Edit comments
        for c in pd.get("comments", []):
            if st.session_state.get("edit_comment") == (post_id, c["id"]):
                st.markdown("---")
                st.subheader("✏️ Edit Comment")
                with st.form(f"edit_comment_form_{c['id']}"):
                    new_author = st.text_input("Author", value=c["author"])
                    new_content = st.text_area("Content", value=c["content"])
                    submitted = st.form_submit_button("Save changes")
                    if submitted:
                        u = requests.put(
                            f"{BACKEND_URL}/posts/{post_id}/comments/{c['id']}",
                            json={"author": new_author, "content": new_content},
                        )
                        if u.status_code == 200:
                            show_toast("Comment updated!", color="#2196F3")
                            st.session_state["edit_comment"] = None
                            trigger_refresh()
                        else:
                            show_toast(f"Update failed: {u.status_code}", color="#f44336")
            else:
                st.write(f"**{c['author']}**: {c['content']}")
                st.caption(f"🕓 {format_datetime(c.get('created_at', ''))}")
                ccols = st.columns([1, 1])
                with ccols[0]:
                    if st.button("Edit", key=f"editc-{c['id']}"):
                        st.session_state["edit_comment"] = (post_id, c["id"])
                        trigger_refresh(0)
                with ccols[1]:
                    if st.button("Delete", key=f"delc-{c['id']}"):
                        d = requests.delete(f"{BACKEND_URL}/posts/{post_id}/comments/{c['id']}")
                        if d.status_code == 204:
                            show_toast("Comment deleted", color="#f44336")
                            trigger_refresh()
                        else:
                            show_toast(f"Delete failed: {d.status_code}", color="#f44336")

        # Add new comment
        st.markdown("---")
        st.subheader("➕ Add Comment")
        with st.form(f"add_comment_form_{post_id}", clear_on_submit=True):
            a = st.text_input("Author")
            cont = st.text_area("Content")
            submitted = st.form_submit_button("Add comment")
            if submitted:
                if not a or not cont:
                    show_toast("Author and content required!", color="#f44336")
                else:
                    cr = requests.post(
                        f"{BACKEND_URL}/posts/{post_id}/comments",
                        json={"author": a, "content": cont},
                    )
                    if cr.status_code == 201:
                        show_toast("Comment added!", color="#4CAF50")
                        trigger_refresh()
                    else:
                        show_toast(f"Error: {cr.status_code}", color="#f44336")
