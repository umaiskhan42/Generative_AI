from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.llms import ollama
from langchain.chains import create_history_aware_retriever, create_retrievel_chain
from langchain_chroma import Chroma 
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
import streamlit as st
import os
from dotenv import load_dotenv
load_dotenv()

#langsmith tracking

os.environ["HF_TOKEN"]=os.getenv("HF_TOKEN")
embeddings=HuggingFaceEmbeddings(model_name="all-MiniLLM-L6-v2")

st.title("Chatbot with RAG")

st.write("Upload PDF and Chat")

api_key=st.text_input("Enter your GROQ api key ",type="password")

if api_key:
    llm=ChatGroq(qroq_api_key=api_key,model="Gemma2-9b-It")

    session_id=st.text_input("Session ID",value="default_session")

    if "store" not in st.session_state:
        st.session_state={}
        uploaded_files=st.file_uploader("Choose a PDF file",type="pdf",accept_multiple_files=True)

        #process uploaded files

        if uploaded_files:
            documents=[]
            for uploaded_file in uploaded_files:
                temppdf=f"./temp.pdf"
                with open(temppdf,"wb") as file:
                    file.write(uploaded_file.getvalue())
                    file_name=uploaded_file.name
                loader=PyPDFLoader(temppdf)
                docs=loader.load()
                documents.extend(docs)
                

