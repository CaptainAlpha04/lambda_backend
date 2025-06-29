import google.generativeai as genai
import os
import markdown2

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def ask_llm(prompt, context_chunks):
    model = genai.GenerativeModel('gemini-2.5-flash') 
    context = "\n\n".join(context_chunks)
    final_prompt = f"Context:\n{context}\n\nQuestion: {prompt}"
    response = model.generate_content(final_prompt)

    html = markdown2.markdown(response.text)
    return html 