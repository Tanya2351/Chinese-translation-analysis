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

# ฟังก์ชันแยกคำศัพท์พร้อมตัวอย่างการใช้งานและคำพ้องความหมาย
def extract_vocab_with_pinyin(text, target_language="th"):
    try:
        # แยกคำจากประโยคในภาษาจีน
        prompt = f"""
Analyze the following Chinese sentence. Break it into individual words and provide:
1. The word in Chinese.
2. The pinyin (romanized pronunciation).
3. The part of speech (e.g., noun, verb, adjective).
4. The meaning of each word in {target_language}.
5. Create a new example sentence using each word in the same context as the input sentence, written in Chinese. The new sentence should incorporate the word meaningfully and use it in a way that makes sense in context.
6. Synonyms for each word in Chinese, if available.

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
    st.title("Chinese Sentence Translation and Analysis with Pinyin")
    st.write("Easily translate Chinese sentences and learn key vocabulary with examples and synonyms.")

    # รับ Input จากผู้ใช้
    chinese_text = st.text_area("Enter a Chinese sentence:")
    target_language = st.selectbox("Select target language for translation and vocabulary:", ["", "th", "en"], index=0)

    if st.button("Translate and Analyze"):
        if api_key and chinese_text and target_language:
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
                        
                        # สร้าง DataFrame เพื่อแสดงผล
                        vocab_list = []
                        for word_data in vocab_data:
                            word = word_data['word']
                            pinyin = word_data['pinyin']
                            part_of_speech = word_data['part_of_speech']
                            meaning = word_data['meaning']
                            example = word_data['example']
                            synonyms = word_data['synonyms']
                            
                            # แปลตัวอย่างประโยคเป็นภาษาที่เลือก
                            example_translated = translate_text(example, target_language)
                            
                            # คำพ้องความหมายจะเป็นภาษาจีนเอง
                            synonyms_translated = ", ".join(synonyms) if isinstance(synonyms, list) and synonyms else "N/A"

                            vocab_list.append({
                                "Word": word,
                                "Pinyin": pinyin,
                                "Part of Speech": part_of_speech,
                                "Meaning": meaning,
                                "Example (Chinese)": example,
                                "Example (Translated)": example_translated,
                                "Synonyms (Chinese)": synonyms_translated
                            })

                        # แสดงตาราง
                        df = pd.DataFrame(vocab_list)
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
            st.error("Please provide an API key, input text, and select a target language.")

if __name__ == "__main__":
    main()

