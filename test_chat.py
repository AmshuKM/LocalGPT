from pprint import pprint

from chat_manager import ChatManager

manager = ChatManager()

chat = manager.create_chat()

manager.save_chat(chat)

pprint(manager.list_chats())

loaded = manager.load_chat(chat["id"])

pprint(loaded)