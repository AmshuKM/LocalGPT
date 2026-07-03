import json
import os
import uuid

from datetime import datetime

from config import (
    CHAT_DIRECTORY,
    MODEL_NAME,
    WELCOME_MESSAGE
)


class ChatManager:

    # ======================================================
    # Initialization
    # ======================================================

    def __init__(self):
        os.makedirs(CHAT_DIRECTORY, exist_ok=True)

    # ======================================================
    # Time
    # ======================================================

    def current_time(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M")

    # ======================================================
    # Create Chat
    # ======================================================

    def create_chat(self):
        return {
            "id": uuid.uuid4().hex,
            "title": "New Chat",
            "created_at": self.current_time(),
            "updated_at": self.current_time(),
            "model": MODEL_NAME,
            "messages": [
                {
                    "role": "assistant",
                    "content": WELCOME_MESSAGE
                }
            ]
        }

    # ======================================================
    # Save Chat
    # ======================================================

    def save_chat(self, chat):
        chat["updated_at"] = self.current_time()

        filepath = os.path.join(
            CHAT_DIRECTORY,
            f"{chat['id']}.json"
        )

        with open(filepath, "w", encoding="utf-8") as file:
            json.dump(chat, file, indent=4, ensure_ascii=False)

    # ======================================================
    # Load Chat
    # ======================================================

    def load_chat(self, chat_id):
        filepath = os.path.join(
            CHAT_DIRECTORY,
            f"{chat_id}.json"
        )

        with open(filepath, "r", encoding="utf-8") as file:
            return json.load(file)

    # ======================================================
    # List Chats
    # ======================================================

    def list_chats(self):
        """
        Returns metadata for all chats.
        """
        chats = []

        for filename in os.listdir(CHAT_DIRECTORY):

            if not filename.endswith(".json"):
                continue

            filepath = os.path.join(CHAT_DIRECTORY, filename)

            with open(filepath, "r", encoding="utf-8") as file:
                chat = json.load(file)

            if "id" not in chat:
                continue

            # --------------------------
            # Get preview text
            # --------------------------

            preview = ""

            for message in chat["messages"]:
                if message["role"] == "user":
                    preview = message["content"]
                    break

            if len(preview) > 45:
                preview = preview[:45] + "..."

            chats.append(
                {
                    "id": chat["id"],
                    "title": chat["title"],
                    "preview": preview,
                    "created_at": chat["created_at"],
                    "updated_at": chat["updated_at"]
                }
            )

        chats.sort(
            key=lambda chat: chat["updated_at"],
            reverse=True
        )

        return chats

    # ======================================================
    # Search Chats
    # ======================================================

    def search_chats(self, query):
        chats = self.list_chats()

        if not query:
            return chats

        query = query.lower()

        return [
            chat
            for chat in chats
            if (
                query in chat["title"].lower()
                or query in chat["preview"].lower()
            )
        ]

    # ======================================================
    # Rename Chat
    # ======================================================

    def rename_chat(self, chat_id, new_title):
        chat = self.load_chat(chat_id)
        chat["title"] = new_title.strip()
        self.save_chat(chat)

    # ======================================================
    # Delete Chat
    # ======================================================

    def delete_chat(self, chat_id):
        filepath = os.path.join(
            CHAT_DIRECTORY,
            f"{chat_id}.json"
        )

        if os.path.exists(filepath):
            os.remove(filepath)
            return True

        return False

    # ======================================================
    # Chat Exists
    # ======================================================

    def chat_exists(self, chat_id):
        filepath = os.path.join(
            CHAT_DIRECTORY,
            f"{chat_id}.json"
        )

        return os.path.exists(filepath)

    # ======================================================
    # Chat Count
    # ======================================================

    def chat_count(self):
        return len(self.list_chats())