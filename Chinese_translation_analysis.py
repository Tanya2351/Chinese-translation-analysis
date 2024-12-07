import streamlit as st
import pandas as pd
import openai
import re

# Sidebar สำหรับกรอก API Key
st.sidebar.title("API Key Settings")
api_key = st.sidebar.text_input("Enter your OpenAI API key:", type="password")
openai.api_key = api_key

# ฟังก์ชันแปลภาษาจีน
def translate_text(text, target_language="Thai"):
    prompt = f"Translate the following Chinese sentence into {target_language}: {text}"
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  
        messages=[{"role": "user", "content": prompt}],
        max_tokens=100
    )
    return response.choices[0].message["content"].strip()

# ฟังก์ชันแยกคำศัพท์พร้อมพินอิน
def extract_vocab_with_pinyin(text, target_language="Thai"):
    prompt = f"""
Analyze the following Chinese sentence. Extract important words and provide:
1. The word in Chinese.
2. The pinyin (romanized pronunciation).
3. The part of speech (e.g., noun, verb, adjective).
4. The meaning in {target_language}.
5. An example sentence using the word in the same context as the input sentence in Chinese.
6. Provide synonyms for each word.

Sentence: {text}

give feedback in this pattern :
        1. Word : (Word)
        2. Pinyin : (Pinyin)
        3. Part of Speech : (Part of Speech)
        4. Meaning : (Meaning)
        5. Example Usage : (Example Usage)
        6. Synonyms : (Synonyms)
    """
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300
    )
    return response.choices[0].message["content"].strip()

# ฟังก์ชันหลัก
def main():
    st.title("Translate and Analyze Chinese Sentences")
    st.write("Translate and analyze Chinese sentences with vocabulary breakdown!")

    # รับ Input จากผู้ใช้
    chinese_text = st.text_area("Enter a Chinese sentence:")
    target_language = st.selectbox("Select target language:", ["Thai", "English"])
    
    if st.button("Translate and Analyze"):
        if api_key and chinese_text:
            with st.spinner("Processing..."):
                # แปลข้อความ
                translation = translate_text(chinese_text, target_language)
                st.subheader("Translation")
                st.write(translation)
                
                # วิเคราะห์คำศัพท์พร้อมพินอิน
                vocab_analysis = extract_vocab_with_pinyin(chinese_text, target_language)
                st.subheader("Vocabulary Analysis with Pinyin")
                st.text(vocab_analysis)

                def process_vocab_data(vocab_analysis):
                    pattern = r"1\.\s*Word\s*:\s*(\S+)\s*2\.\s*Pinyin\s*:\s*(\S+)\s*3\.\s*Part of Speech\s*:\s*(\S+)\s*4\.\s*Meaning\s*:\s*([^\n]+)\s*5\.\s*Example Usage\s*:\s*([^\n]+)\s*6\.\s*Synonyms\s*:\s*([^\n]+)"
                    matches = re.findall(pattern, vocab_analysis, re.DOTALL)
                    word_data = []
                    for match in matches:
                        word_info = {
                            "Word": match[0],
                            "Pinyin": match[1],
                            "Part of Speech": match[2],
                            "Meaning": match[3].strip(),
                            "Example Usage": match[4].strip(),
                            "Synonyms": match[5].strip()
                        }
                        word_data.append(word_info)
                    return word_data
                    
                word_data = process_vocab_data(vocab_analysis)

                st.write("Word data after processing:")
                
                if word_data:
                    df = pd.DataFrame(word_data, columns=["Word", "Pinyin", "Part of Speech", "Meaning", "Example Usage", "Synonyms"], index=range(1, len(word_data) + 1))
                    st.dataframe(df)
                    
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="Download results as CSV",
                        data=csv,
                        file_name="chinese_analysis_with_pinyin.csv",
                        mime="text/csv",
                    )
        else:
            st.error("Please provide an API key and input text.")

if __name__ == "__main__":
    main()

if __name__ == "__main__":
    main()
