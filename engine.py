# engine.py
import io
import os
import traceback
import contextlib
import streamlit as st
from openai import OpenAI


# 🔑 Load OpenAI API key from environment
OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY")
DEFAULT_MODEL = "gpt-4o-mini"

# 🚫 simple forbidden patterns for safety
FORBIDDEN_PATTERNS = [
    "os.environ",
    "subprocess",
    "getenv",
    "system(",
    "popen",
]

def _strip_code_fences(text: str) -> str:
    text = (text or "").strip()
    if text.startswith("```"):
        lines = [ln for ln in text.splitlines() if not ln.strip().startswith("```")]
        text = "\n".join(lines).strip()
    return text

"""UI will first call this function when you click on the Generate button"""
def generate_code(prompt: str) -> str:
    if not OPENAI_API_KEY:
        raise RuntimeError("❌ OPENAI_API_KEY environment variable not set.")
    client = OpenAI(api_key=OPENAI_API_KEY)
    resp = client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=[
            # {"role": "system", "content": "You are a helpful assistant that outputs only safe Python code."},
            {"role": "user", "content": prompt},
        ],
    )
    return _strip_code_fences(resp.choices[0].message.content)

def validate_code(code: str) -> bool:
    """Check if code contains forbidden patterns."""
    lowered = code.lower()
    return not any(pattern in lowered for pattern in FORBIDDEN_PATTERNS)

def exec_code_simple(code: str):
    """
    Execute Python code with exec(), capturing stdout and errors.
    ⚠️ Not a sandbox — only use with trusted code.
    """
    if not validate_code(code):
        return {"stdout": "", "stderr": "❌ Code rejected: unsafe operations detected."}

    out_buf = io.StringIO()
    err_text = ""

    try:
        with contextlib.redirect_stdout(out_buf):
            exec(code, {}, {})
    except Exception:
        err_text = traceback.format_exc()

    return {"stdout": out_buf.getvalue(), "stderr": err_text}
