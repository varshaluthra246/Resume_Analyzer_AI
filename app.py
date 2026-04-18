import streamlit as st
from google import genai
import os
from PyPDF2 import PdfReader
from dotenv import load_dotenv
import re
import pandas as pd

load_dotenv()
# client = OpenAI(api_key = os.getenv("OPEN_API_KEY"))
client = genai.Client()

st.set_page_config(page_title = "Resume Analyzer", 
                   page_icon ="RA",
                   layout="wide")

st.title("Resume Analyzer")

st.markdown("Upload your resume and get a **summary, key skills score and improvement suggestions**")

uploaded_file = st.file_uploader("Upload your resume: ", type=["pdf"])

if uploaded_file:
    pdf = PdfReader(uploaded_file)
    text = ""
    for page in pdf.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "/n"

    text_clean = re.sub(r"(?<!\n)\n(?!\n)", " ", text)

    col1, col2 = st.columns([1,1])

    with col1:
        st.subheader("Resume Preview")
        st.text_area("Resume Text", value = text_clean, height = 400)
    
    with col2:
        st.subheader("AI Analysis")
        if st.button("Analyze Resume"):
            with st.spinner("Analyzing Resume..."):
                prompt = f"""
                    You are a resume expert.
                    Analyze the following resume provide:
                    1. Summary
                    2. List of Key Skills
                    3. Suggestions for Improvement
                    4. A score out of 100 based on 
                    - skills match (30 points)
                    - experience and achievement (30 points)
                    - clarity and formatting (20 points)
                    - overall impression (20 points)
                    Also provide the individual category score in JSON
                    Resume:
                    {text_clean}
                    """
                
                '''response = client.chat.completions.create(
                    model = "",
                    messages = [{"role":"user","content":prompt}]
                    max_tokens=700
                )
                result = response.choices[0].message.content
                '''

                response = client.models.generate_content(
                    model="gemini-3-flash-preview", 
                    contents=[
                        {
                            "role": "user",
                            "parts": [{"text": prompt}]
                        }
                    ]
                )
                result = response.text
                print(result)
                parts = result.split("Score JSON:")
                analysis_text = parts[0]
                st.write(analysis_text)
                if len(parts) > 1:
                    try:
                        import json
                        score_data = json.loads(parts[1].strip())
                        st.subheader("score breakdown")
                        df = pd.DataFrame({
                            "Category":list(score_data.keys()),
                            "Score":list(score_data.values())
                        })
                        st.bar_chart(df.set_index("Category"))
                        st.subheader("Overall Score")
                        total_score = sum(score_data.values())
                        st.progress(min(total_score/100),1.0)
                    except:
                        st.warning("Cound not parse score JSON")
