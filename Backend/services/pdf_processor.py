import os
import torch
from langchain.chains import RetrievalQA
from langchain_community.embeddings import HuggingFaceInstructEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.llms import HuggingFaceHub
from dotenv import load_dotenv
from core.config import settings

load_dotenv()
huggingface_api_token = settings.HUGGINGFACE_USER_ACCESS_TOKEN
DEVICE = "cuda:0" if torch.cuda.is_available() else "cpu"

conversation_retrieval_chain = None
chat_history = []
llm_hub = None
embeddings = None

def init_llm_for_pdf():
    global llm_hub, embeddings
    os.environ["HUGGINGFACEHUB_API_TOKEN"] = huggingface_api_token

    model_id = "tiiuae/falcon-7b-instruct"
    llm_hub = HuggingFaceHub(
        repo_id=model_id,
        model_kwargs={"temperature": 0.1, "max_new_tokens": 600, "max_length": 600}
    )

    os.environ.pop("HUGGINGFACEHUB_API_TOKEN", None)

    embeddings = HuggingFaceInstructEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2", 
        model_kwargs={"device": DEVICE}
    )

def process_pdf(document_path: str):
    global conversation_retrieval_chain
    loader = PyPDFLoader(document_path)
    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1024, chunk_overlap=64)
    texts = text_splitter.split_documents(documents)
    db = Chroma.from_documents(texts, embedding=embeddings)
    conversation_retrieval_chain = RetrievalQA.from_chain_type(
        llm=llm_hub,
        chain_type="stuff",
        retriever=db.as_retriever(search_type="mmr", search_kwargs={'k': 6, 'lambda_mult': 0.25}),
        return_source_documents=False,
        input_key="question"
    )

def process_pdf_prompt(prompt: str) -> str:
    global conversation_retrieval_chain, chat_history
    if conversation_retrieval_chain is None:
        raise ValueError("PDF document not processed. Please upload a PDF first.")
    output = conversation_retrieval_chain({"question": prompt, "chat_history": chat_history})
    answer = output["result"]
    chat_history.append((prompt, answer))
    return answer

init_llm_for_pdf()