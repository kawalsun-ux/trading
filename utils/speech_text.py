"""Zero-dep speech text shaping (ingested from Herald-OS voice/speech-text.ts)."""
import re

_SENTENCE_END = re.compile(r"([.!?…]+[\"')\]]*)(\s+|$)")

def sanitize_for_speech(text):
    text = re.sub(r"<think>.*?</think>", " ", text, flags=re.I | re.S)
    text = re.sub(r"```.*?```", " code omitted. ", text, flags=re.S)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"https?://\S+", "a link", text, flags=re.I)
    text = re.sub(r"^\s{0,3}#{1,6}\s+", "", text, flags=re.M)
    text = re.sub(r"^\s*[-*+]\s+", "", text, flags=re.M)
    text = re.sub(r"^\s*\d+[.)]\s+", "", text, flags=re.M)
    text = re.sub(r"^\s*>\s?", "", text, flags=re.M)
    text = text.replace("|", " ")
    text = re.sub(r"(\*\*|__)(.*?)\1", r"\2", text)
    text = re.sub(r"(\*|_)(.*?)\1", r"\2", text)
    text = re.sub(r"~~(.*?)~~", r"\1", text)
    text = re.sub(r"^-{3,}\s*$", " ", text, flags=re.M)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{2,}", "\n", text)
    return text.strip()

class SentenceChunker:
    def __init__(self):
        self.buffer = ""
    @property
    def pending(self):
        return self.buffer
    def feed(self, delta):
        self.buffer += delta
        out = []
        while True:
            paragraph = self.buffer.find("\n\n")
            m = _SENTENCE_END.search(self.buffer)
            sentence_end = (m.start() + len(m.group(1))) if (m and m.group(2)) else -1
            if paragraph == -1 and sentence_end == -1:
                break
            if paragraph != -1 and (sentence_end == -1 or paragraph < sentence_end):
                cut = paragraph
            else:
                cut = sentence_end
            sentence = self.buffer[:cut].strip()
            self.buffer = self.buffer[cut:].lstrip()
            if sentence:
                out.append(sentence)
        return out
    def flush(self):
        rest = self.buffer.strip()
        self.buffer = ""
        return [rest] if rest else []
    def reset(self):
        self.buffer = ""

COMMENTARY_MAX_CHARS = 1400
SYSTEM_VOICE_MAX_CHARS = 5000

def chunk_for_commentary(text, max_chars=COMMENTARY_MAX_CHARS):
    cleaned = sanitize_for_speech(text)
    if not cleaned:
        return []
    if len(cleaned) <= max_chars:
        return [cleaned]
    chunker = SentenceChunker()
    sentences = chunker.feed(cleaned) + chunker.flush()
    out = []
    current = ""
    for sentence in sentences:
        if len(sentence) > max_chars:
            if current:
                out.append(current); current = ""
            for i in range(0, len(sentence), max_chars):
                out.append(sentence[i:i+max_chars])
            continue
        joined = (current + " " + sentence).strip()
        if current and len(joined) > max_chars:
            out.append(current); current = sentence
        else:
            current = joined
    if current:
        out.append(current)
    return out

def _pieces_up_to(sentence, max_chars):
    out = []
    rest = sentence.strip()
    while len(rest) > max_chars:
        head = rest[:max_chars+1]
        pause = max(head.rfind(", "), head.rfind("; "), head.rfind(": "))
        space = head.rfind(" ")
        cut = pause + 1 if pause > max_chars // 2 else (space if space > max_chars // 2 else max_chars)
        out.append(rest[:cut].strip())
        rest = rest[cut:].strip()
    return out + ([rest] if rest else [])

def chunk_for_system_voice(text, first_max=200, rest_max=600):
    chunker = SentenceChunker()
    sentences = [s.replace("\n", " ") for s in (chunker.feed(text.strip()) + chunker.flush())]
    # normalize whitespace
    sentences = [re.sub(r"\s+", " ", s) for s in sentences]
    pieces = []
    for idx, sent in enumerate(sentences):
        mx = first_max if idx == 0 else rest_max
        pieces.extend(_pieces_up_to(sent, mx))
    out = []
    current = ""
    total = 0
    for piece in pieces:
        total += len(piece) + 1
        if total > SYSTEM_VOICE_MAX_CHARS + 1:
            break
        mx = first_max if not out and not current else rest_max
        joined = (current + " " + piece).strip() if current else piece
        if current and len(joined) > mx:
            out.append(current); current = piece
        else:
            current = joined
    if current:
        out.append(current)
    return out

DEFAULT_STOP_PHRASES = ['stop', 'stop listening', "that's all", 'that is all', 'thanks hermes', 'thank you hermes', 'goodbye', 'never mind', 'nevermind', 'cancel']

def is_stop_phrase(text, phrases=DEFAULT_STOP_PHRASES):
    normalized = re.sub(r"[^\w' ]+", " ", text.lower())
    normalized = re.sub(r"\s+", " ", normalized).strip()
    if not normalized:
        return False
    for phrase in phrases:
        p = phrase.lower().strip()
        if normalized in (p, f"{p} hermes", f"hermes {p}", f"okay {p}", f"ok {p}"):
            return True
    return False

_NOISE = {'', 'you', 'thank you', 'thanks for watching', 'bye', '.', 'the', 'uh', 'um', 'hmm', 'mm'}

def is_noise_transcript(text):
    normalized = re.sub(r"[^\w' ]+", " ", text.lower())
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized in _NOISE or len(normalized) < 2