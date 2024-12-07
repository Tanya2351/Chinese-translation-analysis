import streamlit as st
import pandas as pd
import openai


# Sidebar สำหรับกรอก API Key
st.sidebar.title("API Key Settings")
api_key = st.sidebar.text_input("Enter your OpenAI API key:", type="password")
openai.api_key = api_key



# ฟังก์ชันแปลภาษาจีน
def translate_text(text, target_language="th"):
    prompt = f"Translate the following Chinese sentence into {target_language}: {text}"
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # ใช้โมเดล gpt-3.5-turbo
        messages=[{"role": "user", "content": prompt}],
        #max_tokens=100
    )
    return response.choices[0].message["content"].strip()

# ฟังก์ชันแยกคำศัพท์พร้อมพินอิน
def extract_vocab_with_pinyin(text):
    prompt = f"""
Analyze the following Chinese sentence. Extract all words and provide:
1. The word in Chinese.
2. The pinyin (romanized pronunciation).
3. The meaning in English.
4. The part of speech (e.g., noun, verb, adjective).
5. An example usage of the word.

Sentence: {text}
    """
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # ใช้โมเดล gpt-3.5-turbo
        messages=[{"role": "user", "content": prompt}],
        #max_tokens=300
    )
    return response.choices[0].message["content"].strip()

# ฟังก์ชันหลัก
def main():
    st.title("Translate and Understand Chinese Sentence")
    st.write("Easily translate and analyze Chinese text")

    # รับ Input จากผู้ใช้
    chinese_text = st.text_area("Enter a Chinese sentence:")
    target_language = st.selectbox("Select target language:", ["th", "en"])
    
    if st.button("Translate and Analyze"):
        if api_key and chinese_text:
            with st.spinner("Processing..."):
                # แปลข้อความ
                translation = translate_text(chinese_text, target_language)
                st.subheader("Translation")
                st.write(translation)
                
                # วิเคราะห์คำศัพท์พร้อมพินอิน
                vocab_analysis = extract_vocab_with_pinyin(chinese_text)
                st.subheader("Vocabulary Analysis with Pinyin")
                st.text(vocab_analysis)

                aText = vocab_analysis.split("\n")

                sWord =[]
                sPinyin = []
                sMeaning = []
                sPart = []
                sExample = []
                for x in range(len(aText)):
                    if aText[x][:1] == "1":
                        aTextSP = aText[x].split(" ")
                        sWord.append(aTextSP[1])
                    elif aText[x][:1] == "2":
                        sPinyin.append(aText[x][3:])
                    elif aText[x][:1] == "3":
                        sMeaning.append(aText[x][3:])
                    elif aText[x][:1] == "4":
                        sPart.append(aText[x][3:])
                    elif aText[x][:1] == "5":
                        sExample.append(aText[x][3:])                        


                
                # ตัวอย่างตารางคำศัพท์
                st.subheader("Vocabulary Table")
                vocab_data = {
                    "Word": sWord,
                    "Pinyin": sPinyin,
                    "Meaning": sMeaning,
                    "Part of Speech": sPart,
                    "Example": sExample
                }
                df = pd.DataFrame(vocab_data)
                st.dataframe(df)

                # ดาวน์โหลดผลลัพธ์
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
