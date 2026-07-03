# LocalGPT

A private, local AI chatbot desktop app. LocalGPT runs entirely on your own machine using [Ollama](https://ollama.com) for inference and wraps a Streamlit chat UI in a native desktop window — no data ever leaves your computer.

![LocalGPT](assets/logo.png)

## Features

- 🔒 **100% local** — chats and files never leave your machine; powered by locally-hosted Ollama models
- 💬 **Persistent chats** — create, rename, and revisit multiple chat sessions, saved to disk
- 📎 **File attachments** — drop in text/code files, PDFs, and Word docs for the model to read as context
- 🖼️ **Image support** — attach images and use them with vision-capable models
- 🧠 **Reasoning-model friendly** — automatically strips `<think>...</think>` output from models like Qwen3
- 🖥️ **Native app feel** — runs in its own window via `pywebview` instead of a browser tab
- 🔄 **Model switching** — pick from any model you've pulled into Ollama

## Requirements

- Python 3.10+
- [Ollama](https://ollama.com) installed and running
- At least one Ollama model pulled, e.g.:
  ```bash
  ollama pull qwen3:8b
  ```

## Installation

1. Clone the repo:
   ```bash
   git clone https://github.com/AmshuKM/LocalGPT.git
   cd LocalGPT
   ```
2. (Recommended) Create a virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate      # Windows
   source venv/bin/activate   # macOS/Linux
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Make sure Ollama is installed (LocalGPT will start it automatically if it isn't already running), then launch the app:

```bash
python launcher.py
```

This starts Ollama (if needed), spins up the Streamlit backend, and opens LocalGPT in its own desktop window.

Alternatively, on Windows you can run it as a plain browser app with:

```bash
start_localgpt.bat
```

or run the Streamlit app directly:

```bash
streamlit run app.py
```

## Attaching files

Use the attachment control in the chat input to add context to a conversation:

| Type | Extensions |
|---|---|
| Text / code | `.txt` `.md` `.py` `.js` `.java` `.c` `.cpp` `.cs` `.go` `.rs` `.rb` `.php` `.swift` `.kt` `.sh` `.bat` `.ps1` `.html` `.css` `.json` `.csv` `.yaml` `.toml` and more |
| Documents | `.pdf` `.docx` |
| Images (vision models) | `.png` `.jpg` `.jpeg` `.webp` `.gif` `.bmp` |

Each file is capped at ~20,000 characters of extracted text to stay within local model context limits.

## Building a standalone executable

A PyInstaller spec file is included for building a Windows desktop executable:

```bash
pip install pyinstaller
pyinstaller LocalGPT.spec
```

The bundled app will appear under `dist/LocalGPT/`.

## Project structure

```
LocalGPT/
├── app.py              # Streamlit UI and main app logic
├── launcher.py         # Desktop launcher (starts Ollama + Streamlit, opens native window)
├── chatbot.py          # Wraps Ollama chat calls, strips <think> reasoning tags
├── chat_manager.py     # Create/save/load/rename chat sessions
├── file_reader.py      # Extracts text/images from uploaded files
├── ollama_utils.py     # Lists available local Ollama models
├── config.py           # App-wide configuration (title, default model, etc.)
├── utils.py            # Small helper utilities
├── LocalGPT.spec       # PyInstaller build spec
├── start_localgpt.bat  # Windows convenience launch script
├── assets/             # App icon, logo, splash screen
└── chats/              # Saved chat history (created at runtime)
```

## Configuration

Basic settings live in `config.py`:

```python
PAGE_TITLE = "LocalGPT"
MODEL_NAME = "qwen3:8b"   # default model
CHAT_DIRECTORY = "chats"
```

## License

No license specified yet — add one if you plan to share or accept contributions.
