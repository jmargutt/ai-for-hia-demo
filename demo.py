__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
import streamlit as st
from test_langchain import langchain_search, langchain_question_answering

st.header("AI for HIA demo")
st.markdown("Showcase AI functionalities for HIA.")
st.markdown("Powered by [gpt-3.5-turbo](https://platform.openai.com/docs/guides/gpt).")
st.markdown("Based on [HIA FAQ / Vraagbaak for Ukraine (English)](https://helpfulinformation-faq.redcross.nl/ukraine).")

st.subheader("Semantic search")
query = st.text_input('Query', placeholder='e.g. "legal assistance"')
if query:
    results = langchain_search(query)
    for ix, result in enumerate(results):
        st.text_area(f'Result #{ix}', result)
    
st.subheader("Question Answering")
question = st.text_input('Question', placeholder='e.g. "where can I find shelter?"')
if question:
    answer = langchain_question_answering(question)
    st.text_area('Answer', answer)