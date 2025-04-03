# Backend/services/llm_service.py
import os
import torch
import requests
from typing import Optional, List
from langchain.chains import RetrievalQA
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain.llms.base import LLM
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from pydantic import Field
from core.config import settings
import asyncio

load_dotenv()
huggingface_api_token = settings.HUGGINGFACE_USER_ACCESS_TOKEN
DEVICE = "cuda:0" if torch.cuda.is_available() else "cpu"

conversation_retrieval_chain = None
chat_history = []
llm_hub = None
embeddings = None
pdf_docs = []

class TogetherInferenceLLM(LLM):
    model_name: str = Field(...)
    max_tokens: int = Field(default=500)
    temperature: float = Field(default=0.1)
    provider: str = Field(...)
    api_key: str = Field(...)
    system_prompt: str = Field(
        default="You are an AI assistant for a financial advisory platform. "
                "Your tasks include generating personalized financial plans, providing investment insights, "
                "and performing risk analysis based on user data and the latest market trends."
    )
    client: InferenceClient = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.client = InferenceClient(provider=self.provider, api_key=self.api_key)

    @property
    def _llm_type(self) -> str:
        return "hf_inference_llm"

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": prompt}
        ]
        completion = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            max_tokens=self.max_tokens,
        )
        msg = completion.choices[0].message
        if isinstance(msg, dict):
            return msg.get("content", "")
        else:
            return msg

    @property
    def _identifying_params(self) -> dict:
        return {
            "model_name": self.model_name,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "system_prompt": self.system_prompt
        }

def init_llm():
    global llm_hub, embeddings
    os.environ["HUGGINGFACEHUB_API_TOKEN"] = huggingface_api_token
    llm_hub = TogetherInferenceLLM(
        model_name="meta-llama/Llama-3.2-3B-Instruct",
        provider="hf-inference",
        api_key=huggingface_api_token,
        max_tokens=600,
        temperature=0.1
    )
    os.environ.pop("HUGGINGFACEHUB_API_TOKEN", None)
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": DEVICE}
    )

def fetch_latest_financial_data() -> str:
    symbol = "AAPL"
    api_url = (
        f"{settings.FINANCE_API_URL}/query?function=GLOBAL_QUOTE"
        f"&symbol={symbol}&apikey={settings.FINANCE_API_KEY}"
    )
    try:
        response = requests.get(api_url)
        if response.status_code == 200:
            data = response.json()
            global_quote = data.get("Global Quote", {})
            if global_quote:
                text = f"Market Data for {symbol}:\n"
                for key, value in global_quote.items():
                    text += f"{key}: {value}\n"
                print(text)
                return text
        return "No financial market data available."
    except Exception as e:
        return f"Error fetching financial data: {str(e)}"

async def load_db_data(db) -> list:
    corpus = []
    async for fin in db.users.find():
        text = (
            f"User ID: {fin.get('user_id', '')}\n"
            f"Income: {fin.get('income', 0)}\n"
            f"Expenses: {fin.get('expenses', 0)}\n"
            f"Investment Goals: {fin.get('investment_goals', '')}\n"
            f"Risk Tolerance: {fin.get('risk_tolerance', 'medium')}\n"
            f"User: {fin.get('username', '')}\n"
            f"Email: {fin.get('email', '')}\n"
        )
        corpus.append(text)
    market_data = fetch_latest_financial_data()
    corpus.append(market_data)
    return corpus

async def build_retrieval_chain(db):
    global conversation_retrieval_chain, pdf_docs
    docs = await load_db_data(db)
    from langchain.docstore.document import Document
    db_docs = [Document(page_content=txt) for txt in docs]
    combined_docs = db_docs + pdf_docs if pdf_docs else db_docs
    db_vector = Chroma.from_documents(combined_docs, embedding=embeddings)
    conversation_retrieval_chain = RetrievalQA.from_chain_type(
        llm=llm_hub,
        chain_type="stuff",
        retriever=db_vector.as_retriever(
            search_type="mmr", search_kwargs={'k': 6, 'lambda_mult': 0.25}
        ),
        return_source_documents=False
    )

async def process_prompt(db, prompt: str) -> str:
    global conversation_retrieval_chain, chat_history
    if conversation_retrieval_chain is None:
        await build_retrieval_chain(db)
    loop = asyncio.get_running_loop()
    output = await loop.run_in_executor(None, conversation_retrieval_chain, {"query": prompt})
    answer = output.get("result", "")
    chat_history.append((prompt, answer))
    return answer

async def process_document(document_path: str, db):
    global conversation_retrieval_chain, pdf_docs
    from langchain.document_loaders import PyPDFLoader
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    loader = PyPDFLoader(document_path)
    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1024, chunk_overlap=64)
    new_pdf_docs = text_splitter.split_documents(documents)
    pdf_docs.extend(new_pdf_docs)
    await build_retrieval_chain(db)

init_llm()
