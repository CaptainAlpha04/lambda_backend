import json
import re

#* cleans and parses the response to json, or returns plain text if not JSON

def clean_markdown(text):
    # Remove bold (**text**) and italics (*text*)
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # Remove bold
    text = re.sub(r'\*([^*]+)\*', r'\1', text)        # Remove italics
    # Remove leading * or - or whitespace at line start
    text = re.sub(r'^[\*\-]\s*', '', text, flags=re.MULTILINE)
    # Remove extra backticks
    text = text.replace('`', '')
    # Optionally, remove extra blank lines
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def clean_content(response):
    content = response.strip('```').replace('json', '').replace('`','')
    try:
        return json.loads(content)
    except Exception:
        return clean_markdown(content.strip())

