# app.py
from flask import Flask, request, jsonify, render_template_string
from utils import extract_text_from_pdf
from rag import chunk_text, embed_chunks, create_faiss_index, retrieve_top_chunks, model
from llm_response import ask_llm
import numpy as np

app = Flask(__name__)

chunks = []
faiss_index = None

HTML_PAGE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>RAG Book QA Demo</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .container { max-width: 600px; margin: auto; }
        input[type=file], input[type=text], button { width: 100%; margin: 10px 0; padding: 8px; }
        #answer { margin-top: 20px; background: #f0f0f0; padding: 10px; border-radius: 5px; }
    </style>
</head>
<body>
<div class="container">
    <h2>Upload a Book (PDF)</h2>
    <form id="uploadForm">
        <input type="file" id="pdfFile" name="file" accept="application/pdf" required />
        <button type="submit">Upload</button>
    </form>
    <div id="uploadMsg"></div>
    <hr/>
    <h2>Ask a Question</h2>
    <form id="askForm">
        <input type="text" id="question" name="question" placeholder="Type your question..." required />
        <button type="submit">Ask</button>
    </form>
    <div id="answer"></div>
</div>
<script>
// Upload PDF
const uploadForm = document.getElementById('uploadForm');
const uploadMsg = document.getElementById('uploadMsg');
uploadForm.onsubmit = async (e) => {
    e.preventDefault();
    const fileInput = document.getElementById('pdfFile');
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    uploadMsg.textContent = 'Uploading...';
    const res = await fetch('/upload', { method: 'POST', body: formData });
    const data = await res.json();
    uploadMsg.textContent = data.message || 'Upload complete.';
};
// Ask Question
const askForm = document.getElementById('askForm');
const answerDiv = document.getElementById('answer');
askForm.onsubmit = async (e) => {
    e.preventDefault();
    const question = document.getElementById('question').value;
    answerDiv.textContent = 'Thinking...';
    const res = await fetch('/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question })
    });
    const data = await res.json();
    answerDiv.innerHTML = data.answer || 'No answer.';
};
</script>
</body>
</html>
'''

@app.route('/', methods=['GET'])
def index():
    return render_template_string(HTML_PAGE)

@app.route('/upload', methods=['POST'])
def upload_book():
    file = request.files['file']
    text = extract_text_from_pdf(file)
    print(f"[DEBUG] Extracted Text Length: {len(text)}")

    global chunks, faiss_index  
    chunks = chunk_text(text)
    print(f"[DEBUG] Chunks: {len(chunks)}")

    if not chunks:
        return jsonify({'error': 'No content found in uploaded book'}), 400

    vectors = embed_chunks(chunks)
    vectors = np.array(vectors)
    if vectors.ndim != 2:
        return jsonify({'error': f'Invalid embedding shape: {vectors.shape}'}), 500

    faiss_index = create_faiss_index(vectors) 
    return jsonify({'message': 'Book uploaded and indexed successfully'})


@app.route('/ask', methods=['POST'])
def ask_question():
    data = request.get_json()
    question = data['question']
    top_chunks = retrieve_top_chunks(question, chunks, faiss_index)
    answer = ask_llm(question, top_chunks)
    return jsonify({'answer': answer})

if __name__ == '__main__':
    app.run(debug=True)
