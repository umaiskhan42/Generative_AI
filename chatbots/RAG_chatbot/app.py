from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.llms import ollama
from langchain.chains import create_history_aware_retriever, create_retrievel_chain
from langchain_chroma import Chroma 
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
## RAG Q&A Conversation With PDF Including Chat History
import streamlit as st
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_chroma import Chroma
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
import os
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

        #split and create embeddings
        text_splitter=RecursiveCharachterTextSplitter(chunk_size=5000,chunk_overlap=500)
        splits=text_splitter.split_documents(documents)
        vectorstore=Chroma.from_documents(documents=splits,embedding=embeddings)
        retriever=vectorstore.as_retriever()

        contextualize_q_system_prompt=(
            "Given a chat history and the latest user question"
            "which might reference context in the chat history, "
            "formulate a standalone question which can be understood "
            "without the chat history. Do NOT answer the question, "
            "just reformulate it if needed and otherwise return it as is."

        )
        contextualize_q_prompt = ChatPromptTemplate.from_messages(
        [
        ("system", contextualize_q_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
        ]
        )