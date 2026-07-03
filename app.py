import os

import streamlit as st

from chat_manager import ChatManager
from chatbot import ChatBot
from ollama_utils import get_models
from utils import format_date
from file_reader import (
    build_context,
    encode_images,
    partition_uploads,
    ALLOWED_UPLOAD_TYPES,
)

import base64

from config import (
    PAGE_TITLE,
    PAGE_ICON,
    WELCOME_MESSAGE
)

# ======================================================
# Page Configuration
# ======================================================

st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON,
    layout="wide"
)

# ======================================================
# Managers
# ======================================================

manager = ChatManager()

# --------------------------------------------------
# Load available models (guard against Ollama being
# down or having no models pulled)
# --------------------------------------------------

try:
    available_models = get_models()
except Exception:
    available_models = []

if not available_models:
    st.error(
        "No Ollama models found. Make sure Ollama is running, "
        "then pull a model, e.g.:  ollama pull qwen3:8b"
    )
    st.stop()

# ======================================================
# Session State
# ======================================================

if "rename_chat_id" not in st.session_state:
    st.session_state.rename_chat_id = None

if "rename_title" not in st.session_state:
    st.session_state.rename_title = ""

if "selected_model" not in st.session_state:
    st.session_state.selected_model = available_models[0]

# If the previously selected model is no longer available
# (removed from Ollama), fall back to the first one.
if st.session_state.selected_model not in available_models:
    st.session_state.selected_model = available_models[0]

if "current_chat" not in st.session_state:

    chat = manager.create_chat()

    manager.save_chat(chat)

    st.session_state.current_chat = chat

if "search_query" not in st.session_state:
    st.session_state.search_query = ""

if "delete_chat_id" not in st.session_state:
    st.session_state.delete_chat_id = None


# ======================================================
# Sidebar
# ======================================================

with st.sidebar:

    logo_path = os.path.join("assets", "logo.png")

    st.image(
        logo_path,
        use_container_width=True
    )

    st.markdown("---")

    # --------------------------------------------------
    # Model Selection
    # --------------------------------------------------

    model = st.selectbox(
        "Model",
        available_models,
        index=available_models.index(
            st.session_state.selected_model
        )
    )

    if model != st.session_state.selected_model:

        st.session_state.selected_model = model

        st.rerun()

    # --------------------------------------------------
    # New Chat
    # --------------------------------------------------

    if st.button(
        "🆕 New Chat",
        use_container_width=True
    ):

        chat = manager.create_chat()

        manager.save_chat(chat)

        st.session_state.current_chat = chat

        st.rerun()

    st.divider()

    # --------------------------------------------------
    # Search
    # --------------------------------------------------

    search = st.text_input(
        "🔍 Search Chats",
        value=st.session_state.search_query,
        placeholder="Search..."
    )

    st.session_state.search_query = search

    st.divider()

    # --------------------------------------------------
    # Saved Chats
    # --------------------------------------------------

    st.subheader("💬 Saved Chats")

    saved_chats = manager.search_chats(
        st.session_state.search_query
    )

    for chat in saved_chats:

        is_current = (
            chat["id"] ==
            st.session_state.current_chat["id"]
        )

        icon = "🟢" if is_current else "⚪"

        col1, col2, col3 = st.columns([5, 1, 1])

        # -------------------------
        # Open Chat
        # -------------------------

        with col1:

            if st.button(
                f"{icon} {chat['title']}",
                key=f"open_{chat['id']}",
                use_container_width=True
            ):

                st.session_state.current_chat = manager.load_chat(
                    chat["id"]
                )

                st.rerun()

            if chat["preview"]:
                st.caption(chat["preview"])

            st.caption(
                format_date(chat["updated_at"])
            )

        # -------------------------
        # Rename
        # -------------------------

        with col2:

            if st.button(
                "✏️",
                key=f"rename_{chat['id']}"
            ):

                st.session_state.rename_chat_id = chat["id"]

                st.session_state.rename_title = chat["title"]

        # -------------------------
        # Delete
        # -------------------------

        with col3:

            if st.button(
                "🗑",
                key=f"delete_{chat['id']}"
            ):

                st.session_state.delete_chat_id = chat["id"]

    # --------------------------------------------------
    # Delete Confirmation
    # --------------------------------------------------

    if st.session_state.delete_chat_id:

        st.warning("Delete this chat?")

        col1, col2 = st.columns(2)

        with col1:

            if st.button(
                "Yes",
                use_container_width=True,
                key="confirm_delete_yes"
            ):

                manager.delete_chat(
                    st.session_state.delete_chat_id
                )

                chats = manager.list_chats()

                if chats:

                    st.session_state.current_chat = manager.load_chat(
                        chats[0]["id"]
                    )

                else:

                    chat = manager.create_chat()

                    manager.save_chat(chat)

                    st.session_state.current_chat = chat

                st.session_state.delete_chat_id = None

                st.rerun()

        with col2:

            if st.button(
                "Cancel",
                use_container_width=True,
                key="confirm_delete_cancel"
            ):

                st.session_state.delete_chat_id = None

                st.rerun()

    st.divider()

    # --------------------------------------------------
    # Rename Chat
    # --------------------------------------------------

    if st.session_state.rename_chat_id:

        st.info("Rename Chat")

        new_title = st.text_input(
            "Title",
            value=st.session_state.rename_title,
            key="rename_input"
        )

        col1, col2 = st.columns(2)

        with col1:

            if st.button(
                "Save",
                use_container_width=True,
                key="rename_save"
            ):

                manager.rename_chat(
                    st.session_state.rename_chat_id,
                    new_title
                )

                if (
                    st.session_state.current_chat["id"]
                    ==
                    st.session_state.rename_chat_id
                ):

                    st.session_state.current_chat[
                        "title"
                    ] = new_title

                st.session_state.rename_chat_id = None

                st.rerun()

        with col2:

            if st.button(
                "Cancel",
                use_container_width=True,
                key="rename_cancel"
            ):

                st.session_state.rename_chat_id = None

                st.rerun()

        st.divider()

    # --------------------------------------------------
    # Statistics
    # --------------------------------------------------

    st.metric(
        "Messages",
        len(
            st.session_state.current_chat["messages"]
        )
    )

    st.metric(
        "Chats",
        manager.chat_count()
    )

    st.divider()

    st.caption("LocalGPT v1.1")

    st.caption("Powered by Ollama")

    # --------------------------------------------------
    # Clear Current Chat
    # --------------------------------------------------

    if st.button(
        "🗑 Clear Current Chat",
        use_container_width=True
    ):

        st.session_state.current_chat["messages"] = [

            {
                "role": "assistant",
                "content": WELCOME_MESSAGE
            }

        ]

        st.session_state.current_chat["title"] = "New Chat"

        manager.save_chat(
            st.session_state.current_chat
        )

        st.rerun()

# ======================================================
# Main Page
# ======================================================

st.title(f"{PAGE_ICON} {PAGE_TITLE}")

st.caption(
    f"Running locally • {st.session_state.selected_model}"
)

st.divider()

# ======================================================
# Display Chat Messages
# ======================================================

messages = st.session_state.current_chat["messages"]

for message in messages:

    with st.chat_message(message["role"]):

        # User messages that carried a file attachment store a
        # clean "display" version (without the raw file dump).
        # Fall back to "content" for older chats / assistant msgs.
        st.markdown(
            message.get("display", message["content"])
        )

        # Re-render any attached images from their stored base64.
        for encoded in message.get("images", []):
            try:
                st.image(base64.b64decode(encoded), width=280)
            except Exception:
                pass

# ======================================================
# Chat Input
# ======================================================

user_input = st.chat_input(
    "Type your message...",
    accept_file="multiple",
    file_type=ALLOWED_UPLOAD_TYPES,
)

if user_input:

    # --------------------------------------------------
    # Unpack text + attachments
    # --------------------------------------------------
    # With file uploads enabled, st.chat_input returns an
    # object with .text and .files instead of a plain string.

    prompt = (user_input.text or "").strip()

    uploaded_files = user_input.files or []

    # Ignore truly empty submissions.
    if not prompt and not uploaded_files:
        st.stop()

    # --------------------------------------------------
    # Split attachments: text-like files vs images
    # --------------------------------------------------
    # Text/PDF/Word  -> extracted and added as text context.
    # Images         -> base64, sent to a VISION model via the
    #                   message "images" field.

    text_files, image_files = partition_uploads(uploaded_files)

    file_context = build_context(text_files)
    images = encode_images(image_files)

    # --------------------------------------------------
    # Build the user message
    # --------------------------------------------------
    # model_content   -> what the model reads (text + file text)
    # display_content -> what you see in the chat (text + a small
    #                    "attached" note; images render separately)

    if file_context:
        model_content = (
            f"{prompt}\n\n"
            "The user attached the following file(s). "
            "Use them as context when answering:\n\n"
            f"{file_context}"
        ).strip()
    else:
        model_content = prompt

    # If only an image was sent with no text, give the model a nudge.
    if not model_content and images:
        model_content = "Look at the attached image(s) and describe them."

    if uploaded_files:
        names = ", ".join(f.name for f in uploaded_files)
        display_content = f"{prompt}\n\n📎 *Attached: {names}*".strip()
    else:
        display_content = prompt

    # --------------------------------------------------
    # Add User Message
    # --------------------------------------------------

    user_message = {
        "role": "user",
        "content": model_content,
        "display": display_content,
    }

    if images:
        user_message["images"] = images

    st.session_state.current_chat["messages"].append(user_message)

    with st.chat_message("user"):
        st.markdown(display_content)
        for uploaded_file in image_files:
            st.image(uploaded_file, width=280)

    # --------------------------------------------------
    # Create Bot
    # --------------------------------------------------

    bot = ChatBot(
        st.session_state.selected_model
    )

    # --------------------------------------------------
    # Stream Assistant Response
    # --------------------------------------------------

    with st.chat_message("assistant"):

        placeholder = st.empty()

        full_response = ""

        try:

            for chunk in bot.stream_response(
                st.session_state.current_chat["messages"]
            ):

                full_response += chunk

                placeholder.markdown(
                    full_response + "▌"
                )

            placeholder.markdown(full_response)

        except Exception as error:

            full_response = f"⚠️ Error talking to the model: {error}"

            placeholder.markdown(full_response)

    # --------------------------------------------------
    # Save Assistant Message
    # --------------------------------------------------

    st.session_state.current_chat["messages"].append(
        {
            "role": "assistant",
            "content": full_response
        }
    )

    # --------------------------------------------------
    # Generate Title
    # --------------------------------------------------

    if (
        st.session_state.current_chat["title"]
        == "New Chat"
    ):

        try:

            title = bot.generate_title(
                st.session_state.current_chat["messages"]
            )

            if title:

                st.session_state.current_chat["title"] = title

        except Exception:

            # Ignore title generation errors
            pass

    # --------------------------------------------------
    # Save Chat
    # --------------------------------------------------

    manager.save_chat(
        st.session_state.current_chat
    )

    st.rerun()