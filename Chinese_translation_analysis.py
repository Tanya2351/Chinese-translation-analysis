import streamlit as st
import pandas as pd
import openai
import json

# Sidebar สำหรับกรอก API Key
st.sidebar.title("API Key Settings")
api_key = st.sidebar.text_input("Enter your OpenAI API key:", type="password")
openai.api_key = api_key

# ฟังก์ชันแปลภาษาจีน
def translate_text(text, target_language="th"):
    try:
        prompt = f"Translate the following Chinese sentence into {target_language}: {text}"
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100
        )
        return response.choices[0].message["content"].strip()
    except Exception as e:
        return f"Error during translation: {str(e)}"

# ฟังก์ชันแปลตัวอย่างและคำพ้องความหมายตามภาษาเป้าหมาย
def translate_example_and_synonyms(example, target_language="th"):
    try:
        prompt = f"Translate the following sentence into {target_language}: {example}"
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100
        )
        return response.choices[0].message["content"].strip()
    except Exception as e:
        return f"Error during example translation: {str(e)}"

# ฟังก์ชันแยกคำศัพท์พร้อมตัวอย่างการใช้งานและคำพ้องความหมาย
def extract_vocab_with_pinyin(text, target_language="th"):
    try:
        prompt = f"""
Analyze the following Chinese sentence. Extract important words and provide:
1. The word in Chinese.
2. The pinyin (romanized pronunciation).
3. The part of speech (e.g., noun, verb, adjective).
4. The meaning in {target_language}.
5. An example sentence using the word in the same context as the input sentence in Chinese.
6. Synonyms for the word in Chinese, including their pinyin (make sure the synonyms are related to the word in context).

Return the result as a JSON array, where each element is a dictionary with keys:
"word", "pinyin", "part_of_speech", "meaning", "example", and "synonyms".

Sentence: {text}
        """
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500
        )
        return json.loads(response.choices[0].message["content"].strip())
    except json.JSONDecodeError as e:
        st.error(f"JSON Decode Error: {str(e)}")
        return []
    except Exception as e:
        st.error(f"Error during vocabulary extraction: {str(e)}")
        return []

# ฟังก์ชันหลัก
def main():
    st.title("Translate and Understand Chinese Sentences")
    st.write("Easily translate Chinese sentences and learn key vocabulary with examples and synonyms.")

    # รับ Input จากผู้ใช้
    chinese_text = st.text_area("Enter a Chinese sentence:")
    target_language = st.selectbox("Select target language for translation and vocabulary:", ["th", "en"])

    if st.button("Translate and Analyze"):
        if api_key and chinese_text:
            with st.spinner("Processing..."):
                # แปลข้อความ
                translation = translate_text(chinese_text, target_language)
                st.subheader("Translation")
                st.write(translation)

                # วิเคราะห์คำศัพท์พร้อมตัวอย่างการใช้งานและคำพ้องความหมาย
                try:
                    vocab_data = extract_vocab_with_pinyin(chinese_text, target_language)

                    if vocab_data:
                        st.subheader("Vocabulary Analysis with Examples and Synonyms")
                        
                        # แทนที่เครื่องหมาย _ ใน Part of Speech
                        for word_data in vocab_data:
                            word_data["part_of_speech"] = word_data["part_of_speech"].replace("_", "")

                            # ตัวอย่างและคำพ้องความหมายจะยังคงเป็นภาษาจีน
                            word_data["example"] = word_data["example"]  # ไม่แปลตัวอย่าง
                            word_data["synonyms"] = word_data["synonyms"] if word_data["synonyms"] != "N/A" else "N/A"

                            # ถ้าเลือกภาษาไทยให้แปลตัวอย่างเป็นภาษาไทย
                            word_data["example_translation"] = translate_example_and_synonyms(word_data["example"], target_language)

                        # จัดลำดับ DataFrame ให้ Part of Speech อยู่ก่อน Meaning
                        df = pd.DataFrame(vocab_data)
                        df = df[["word", "pinyin", "part_of_speech", "meaning", "example", "synonyms"]]
                        
                        # แสดงคำพ้องความหมายเป็นลิสต์หรือ "N/A"
                        df['synonyms'] = df['synonyms'].apply(lambda x: x if isinstance(x, str) else "N/A")

                        # เพิ่มตัวอย่างการใช้คำในช่องเดียวกันกับคำแปล
                        df["example"] = df.apply(lambda row: f'{row["example"]} ({row["example_translation"]})' if row["example_translation"] != "N/A" else row["example"], axis=1)
                        df.drop(columns=["example_translation"], inplace=True)

                        # ถ้าผู้ใช้เลือกภาษาไทย เปลี่ยนคำแปลของ "meaning" และ "example" เป็นภาษาไทย
                        if target_language == "th":
                            df["meaning"] = df["meaning"].apply(lambda x: translate_example_and_synonyms(x, "th"))
                            df["example"] = df["example"].apply(lambda x: translate_example_and_synonyms(x, "th"))

                        # แสดง DataFrame พร้อมหัวข้อที่แปลเป็นภาษาไทยหรืออังกฤษ
                        if target_language == "th":
                            df.columns = ["คำ", "พินอิน", "ประเภทของคำ", "ความหมาย", "ตัวอย่างการใช้คำ", "คำพ้องความหมาย"]
                        else:
                            df.columns = ["Word", "Pinyin", "Part of Speech", "Meaning", "Example Usage", "Synonyms"]
                        
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
                        st.error("No vocabulary data extracted. Please try again with a different sentence.")
                except Exception as e:
                    st.error(f"An error occurred during vocabulary analysis: {str(e)}")
        else:
            st.error("Please provide an API key and input text.")

if __name__ == "__main__":
    main()
