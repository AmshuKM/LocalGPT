import re

from ollama import chat


class _ThinkStripper:
    """
    Removes <think>...</think> spans from a stream of text chunks.

    Reasoning models (e.g. qwen3) emit their chain-of-thought wrapped
    in <think></think> tags. Those tags can be split across streaming
    chunks, so we buffer just enough to detect a tag that straddles a
    chunk boundary before deciding what to emit.
    """

    OPEN = "<think>"
    CLOSE = "</think>"

    def __init__(self):
        self._buf = ""
        self._in_think = False

    def feed(self, text):
        self._buf += (text or "")
        out = []

        while self._buf:

            if self._in_think:
                idx = self._buf.find(self.CLOSE)
                if idx == -1:
                    # No closing tag yet. Drop everything except a tail
                    # that might be the start of a split "</think>".
                    keep = len(self.CLOSE) - 1
                    if len(self._buf) > keep:
                        self._buf = self._buf[-keep:]
                    break
                self._buf = self._buf[idx + len(self.CLOSE):]
                self._in_think = False

            else:
                idx = self._buf.find(self.OPEN)
                if idx == -1:
                    # No opening tag. Emit everything except a tail that
                    # might be the start of a split "<think>".
                    keep = len(self.OPEN) - 1
                    if len(self._buf) > keep:
                        out.append(self._buf[:-keep])
                        self._buf = self._buf[-keep:]
                    break
                out.append(self._buf[:idx])
                self._buf = self._buf[idx + len(self.OPEN):]
                self._in_think = True

        return "".join(out)

    def flush(self):
        """Emit any buffered non-think text left at the end of the stream."""
        out = "" if self._in_think else self._buf
        self._buf = ""
        return out


class ChatBot:

    def __init__(self, model_name):
        self.model_name = model_name

    # --------------------------------------------------

    @staticmethod
    def _to_ollama(messages):
        """
        Build a clean message list for Ollama.

        Our stored messages carry extra keys (e.g. "display") that
        the model doesn't need, and user messages may include an
        "images" list (base64) for vision models. Keep only what
        Ollama expects: role, content, and images when present.
        """
        clean = []

        for message in messages:
            item = {
                "role": message["role"],
                "content": message.get("content", ""),
            }

            images = message.get("images")
            if images:
                item["images"] = images

            clean.append(item)

        return clean

    # --------------------------------------------------

    def stream_response(self, messages):
        """
        Stream the assistant's reply, with <think> reasoning removed.
        Yields cleaned text chunks. On failure, yields one error line.
        """
        stripper = _ThinkStripper()

        try:
            stream = chat(
                model=self.model_name,
                messages=self._to_ollama(messages),
                stream=True,
            )

            for chunk in stream:
                content = chunk["message"]["content"]
                cleaned = stripper.feed(content)
                if cleaned:
                    yield cleaned

            tail = stripper.flush()
            if tail:
                yield tail

        except Exception as error:
            yield f"\u26a0\ufe0f Error talking to the model: {error}"

    # --------------------------------------------------

    def generate_title(self, messages):
        """
        Ask the model for a short title based on the first user message.
        Falls back to "New Chat" if anything goes wrong.
        """
        # Find the first actual user message rather than assuming index 1.
        first_user = next(
            (m["content"] for m in messages if m.get("role") == "user"),
            None,
        )

        if not first_user:
            return "New Chat"

        prompt = (
            "Generate a short title (maximum 4 words).\n"
            "Return ONLY the title, with no quotes and no explanation.\n\n"
            "Conversation:\n"
            f"User:\n{first_user}\n"
        )

        try:
            response = chat(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
            )
            raw = response["message"]["content"]
        except Exception:
            return "New Chat"

        return self._clean_title(raw)

    # --------------------------------------------------

    @staticmethod
    def _clean_title(text):
        if not text:
            return "New Chat"

        # Remove any reasoning block.
        text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)

        # Take the first non-empty line, strip surrounding quotes.
        line = next(
            (ln.strip() for ln in text.splitlines() if ln.strip()),
            "",
        )
        line = line.strip().strip('"').strip("'").strip()

        if not line:
            return "New Chat"

        # Keep titles short.
        if len(line) > 40:
            line = line[:40].rstrip() + "..."

        return line