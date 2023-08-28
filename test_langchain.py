import pandas as pd
from langchain.chains import RetrievalQA
from langchain.vectorstores import Chroma
from langchain.chat_models import AzureChatOpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.document_loaders import WebBaseLoader, DataFrameLoader
from utils import download_unzip_from_google_drive, replace_non_question
from dotenv import load_dotenv
import os
import glob
load_dotenv()
os.environ["OPENAI_API_TYPE"] = "azure"
os.environ["OPENAI_API_VERSION"] = "2023-03-15-preview"

# # print('loading document')
# df = pd.read_excel("HIA-FAQ - UKR - English.xlsx", sheet_name='Q&As')
# # clean text
# df = df.rename(columns={'The Answer (can be multi-line)\n#ANSWER': 'answer'})
# df = df.rename(columns={'The Question (should be 1 line)\n#QUESTION': 'question'})
# df['question'] = df['question'].apply(replace_non_question)
# df['text'] = df['question'] + " " + df['answer']
# df['text'] = df['text'].str.replace(r'<[^<]+?>', '', regex=True)
# df = df.dropna(subset=['text'])
# df['text'] = df['text'].astype(str)
# # extra filters
# df = df[df['Visible?\n#VISIBLE'] == 'Show']  # only visible entries
# df = df[['text', 'Select Sub-Category:']]  # keep only sub-category as metadata
# # map to langchain doc
# docs = DataFrameLoader(df, page_content_column='text').load()

vs_dir = "vector-stores"
openai_embeddings = OpenAIEmbeddings(deployment="510-text-embedding", chunk_size=1)

# # print('creating vector store with embeddings')
# vector_store = Chroma.from_documents(documents=docs, embedding=openai_embeddings, persist_directory=vs_dir)

if len(os.listdir(vs_dir)) == 0:
    download_unzip_from_google_drive(os.getenv('ZIPFILE_GOOGLE_ID'), vs_dir)
vector_store = Chroma(persist_directory=vs_dir, embedding_function=openai_embeddings)

# print('initializing LLM')
llm = AzureChatOpenAI(
    openai_api_base=os.getenv("OPENAI_API_BASE"),
    openai_api_version=os.getenv("OPENAI_API_VERSION"),
    deployment_name=os.getenv("OPENAI_DEPLOYMENT"),
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    openai_api_type=os.getenv("OPENAI_API_TYPE")
)


def langchain_search(query):
    docs = vector_store.similarity_search_with_score(query)
    docs = [doc[0] for doc in docs[:3]]
    docs = [doc.page_content for doc in docs]
    return docs


def langchain_question_answering(question):
    qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=vector_store.as_retriever())
    result = qa_chain({"query": question})
    return result['result']
