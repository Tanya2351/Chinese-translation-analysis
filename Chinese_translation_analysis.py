import streamlit as st
import pandas as pd
import openai

# Sidebar for API Key input
st.sidebar.title("API Key Settings")
api_key = st.sidebar.text_input("Enter your OpenAI API key:", type="password")
openai.api_key = api_key  

# Function to translate text
def translate_text(text, target_language="en"):
    try:
        prompt = f"Translate the following Chinese sentence into {target_language}: {text}"
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"Error during translation: {str(e)}"

# Function to extract vocabulary with pinyin
def extract_vocab_with_pinyin(text, target_language="en"):
    try:
        prompt = f"""
        Analyze the following Chinese sentence. Break it into individual words and provide:
        1. The word in Chinese.
        2. The pinyin (romanized pronunciation).
        3. The part of speech (e.g., noun, verb, adjective).
        4. The meaning of each word in {target_language}.
        5. Create a new example sentence using each word in the same context as the input sentence, written in Chinese.
        6. Synonyms for each word in Chinese, if available.

        Sentence: {text}
        """
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500
        )
        
        # Extracting content from the API response
        content = response.get('choices', [{}])[0].get('message', {}).get('content', '').strip()
        
        # If the content is empty, return an empty list
        if not content:
            return []
        
        # Now we need to parse the content into a structured form. 
        # If it's in plain text, we split it based on lines, and then process each line.
        vocab_list = []
        
        # Split the response by newlines and process each line
        for line in content.split("\n"):
            parts = line.split(" - ")
            if len(parts) >= 5:
                # Assign each part to corresponding variables
                word, pinyin, part_of_speech, meaning, example = parts[:5]
                synonyms = parts[5] if len(parts) > 5 else "N/A"
                
                # Append the data as a dictionary to the vocab_list
                vocab_list.append({
                    "Word": word,
                    "Pinyin": pinyin,
                    "Part of Speech": part_of_speech,
                    "Meaning": meaning,
                    "Example (Chinese)": example,
                    "Synonyms (Chinese)": synonyms
                })
        
        return vocab_list
    except Exception as e:
        st.error(f"Error during vocabulary extraction: {str(e)}")
        return []

# Main function
def main():
    st.title("Translate and Understand Chinese Sentence")
    st.write("Translate Chinese sentences and learn key vocabulary with examples and synonyms")

    # Get user input
    chinese_text = st.text_area("Enter a Chinese sentence:")
    target_language = st.selectbox("Select target language for translation and vocabulary:", ["", "en", "th"], index=0)

    if st.button("Translate and Analyze"):
        if api_key and chinese_text and target_language:
            with st.spinner("Processing..."):
                # Translate the text
                translation = translate_text(chinese_text, target_language)
                st.subheader("Translation")
                st.write(translation)

                # Analyze the vocabulary
                try:
                    vocab_data = extract_vocab_with_pinyin(chinese_text, target_language)

                    if vocab_data:
                        st.subheader("Vocabulary Analysis with Examples and Synonyms")
                        
                        vocab_list = []
                        for word_data in vocab_data:
                            word = word_data.get('word', 'N/A')
                            pinyin = word_data.get('pinyin', 'N/A')
                            part_of_speech = word_data.get('part_of_speech', 'N/A')
                            meaning = word_data.get('meaning', 'N/A')
                            example = word_data.get('example', 'N/A')
                            synonyms = word_data.get('synonyms', 'N/A')
                            
                            example_translated = translate_text(example, target_language)
                            synonyms_translated = ", ".join(synonyms) if isinstance(synonyms, list) else "N/A"

                            vocab_list.append({
                                "Word": word,
                                "Pinyin": pinyin,
                                "Part of Speech": part_of_speech,
                                "Meaning": meaning,
                                "Example (Chinese)": example,
                                "Example (Translated)": example_translated,
                                "Synonyms (Chinese)": synonyms_translated
                            })

                        # Display the dataframe
                        df = pd.DataFrame(vocab_list)
                        st.dataframe(df)

                        # Download the results as CSV
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
