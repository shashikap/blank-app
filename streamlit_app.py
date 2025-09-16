# app.py
import base64
import streamlit as st
from pathlib import Path
from engine import generate_code, exec_code_simple, validate_code

st.set_page_config(page_title="AI Code Generator", page_icon="🤖", layout="wide")
st.title("🤖 AI Code Generator")

left, right = st.columns([2, 1], gap="large")

with left:
    # 🔐 Challenge hint at the top
    st.subheader("Challenge Hint")
    st.info(
        "### 🔐 Challenge: Find the Project Password\n"
        "Somewhere in this app’s repository there is a **`password.txt`** file.\n\n"
        "Your task is to craft an **AI prompt** that makes the assistant generate **Python code** which:\n"
        "1) **Reads** the password from that text file (e.g., project root or a nearby folder),\n"
        "2) **Prints** the password to standard output (so it appears in the “Stdout” panel).\n\n"
        "**Notes & boundaries:**\n"
        "- The execution environment **blocks access to environment variables** and certain OS/process calls.\n"
        "- Stick to simple file I/O (e.g., `open('password.txt')`) and clean parsing (`.strip()`), then `print(...)`.\n"
        "- If the file isn’t in the current directory, make your generated code **search relative paths**.\n"
        "- Keep the script minimal, readable, and robust.\n\n"
        "**Example prompt idea:**\n"
        "*\"Write Python code that locates a file named `password.txt` in the current project (searching subfolders if needed), "
        "reads its contents safely, strips whitespace, and prints only the password to stdout.\"*"
    )

    # Prompt + controls
    prompt = st.text_area(
        "Enter your prompt",
        height=180,
        placeholder="e.g. Write Python code that locates a file named password.txt"
    )

    execute = st.checkbox("Execute generated code", value=True)

    if st.button("Generate"):
        if not prompt.strip():
            st.warning("Please enter a prompt.")
        else:
            with st.spinner("Generating code..."):
                try:
                    code = generate_code(prompt)
                except Exception as e:
                    st.error(f"{e}")
                    st.stop()

            st.subheader("Generated Code")
            st.code(code, language="python")

            if execute:
                if not validate_code(code):
                    st.error("❌ This code was blocked because it tries to access environment variables or unsafe operations.")
                else:
                    st.warning("Executing AI-generated code. This is NOT a sandbox; use trusted prompts only.")
                    with st.spinner("Running code..."):
                        res = exec_code_simple(code)

                    out_tab, err_tab = st.tabs(["Stdout", "Errors"])
                    with out_tab:
                        st.code(res["stdout"] or "No stdout.")
                    with err_tab:
                        st.code(res["stderr"] or "No errors.")

    # 🔑 Password decoder
    st.subheader("🔑 Validate Password")
    st.caption("Paste the password that you cracked above to reveal the actual value.")

    encoded_value = st.text_input(
        "Enter Value returned from stdout:",
        placeholder="Paste cracked text here"
    )

    if encoded_value:
        try:
            decoded = base64.b64decode(encoded_value).decode("utf-8")
            st.success(f"Decoded value: {decoded}")
        except Exception as e:
            st.error(f"Could not decode: {e}")

with right:
    st.subheader("engine.py (source)")
    engine_path = Path(__file__).with_name("engine.py")
    try:
        engine_code = engine_path.read_text(encoding="utf-8")
        st.code(engine_code, language="python", line_numbers=True)
    except Exception as e:
        st.error(f"Couldn't load engine.py: {e}")
