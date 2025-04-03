import os
import torch
import requests
import asyncio
from typing import Optional, List
from langchain.chains import RetrievalQA
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain.llms.base import LLM
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from pydantic import Field
from core.config import settings

load_dotenv()
huggingface_api_token = settings.HUGGINGFACE_USER_ACCESS_TOKEN
DEVICE = "cuda:0" if torch.cuda.is_available() else "cpu"

# Maintain per-user data in dictionaries:
pdf_docs_dict = {}        # key: email, value: list of processed PDF documents
retrieval_chains = {}     # key: email, value: the RetrievalQA chain for that user
vector_docs = {}          # key: email, value: the combined list of documents used for retrieval

llm_hub = None
embeddings = None

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

async def load_user_data(db, email: str) -> list:
    """
    Load only the data for the specified user.
    """
    corpus = []
    user = await db.users.find_one({"email": email})
    if user:
        text = (
            f"User ID: {user.get('user_id', '')}\n"
            f"Income: {user.get('income', 0)}\n"
            f"Expenses: {user.get('expenses', 0)}\n"
            f"Investment Goals: {user.get('investment_goals', '')}\n"
            f"Risk Tolerance: {user.get('risk_tolerance', 'medium')}\n"
            f"User: {user.get('username', '')}\n"
            f"Email: {user.get('email', '')}\n"
        )
        corpus.append(text)
    # Optionally, you may still want to append global market data.
    market_data = fetch_latest_financial_data()
    corpus.append(market_data)
    return corpus

async def build_retrieval_chain(db, email: str):
    """
    Build the retrieval chain for a specific user using their data and any uploaded PDFs.
    """
    from langchain.docstore.document import Document
    docs = await load_user_data(db, email)
    db_docs = [Document(page_content=txt) for txt in docs]
    user_pdf_docs = pdf_docs_dict.get(email, [])
    combined_docs = db_docs + user_pdf_docs if user_pdf_docs else db_docs
    
    # Save the combined documents so we can print them later for debugging.
    vector_docs[email] = combined_docs
    
    # Debug print: show all documents being used in the vector store for this user.
    print(f"Combined documents for user {email}:")
    for doc in combined_docs:
        print(doc.page_content)
    
    db_vector = Chroma.from_documents(combined_docs, embedding=embeddings)
    retrieval_chains[email] = RetrievalQA.from_chain_type(
        llm=llm_hub,
        chain_type="stuff",
        retriever=db_vector.as_retriever(
            search_type="mmr", search_kwargs={'k': 6, 'lambda_mult': 0.25}
        ),
        return_source_documents=False
    )

async def process_document(document_path: str, db, email: str):
    """
    Process the uploaded PDF for the given user and rebuild their retrieval chain.
    """
    from langchain.document_loaders import PyPDFLoader
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    loader = PyPDFLoader(document_path)
    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1024, chunk_overlap=64)
    new_pdf_docs = text_splitter.split_documents(documents)
    pdf_docs_dict[email] = pdf_docs_dict.get(email, []) + new_pdf_docs
    # Rebuild the retrieval chain for this user so that the PDF data is included.
    await build_retrieval_chain(db, email)

async def process_prompt(db, prompt: str, email: str) -> str:
    """
    Process a prompt for a given user using their retrieval chain.
    """
    if email not in retrieval_chains:
        await build_retrieval_chain(db, email)
    # Debug print: show the vector documents for the user before processing the prompt.
    if email in vector_docs:
        print(f"Using vector database documents for user {email}:")
        for doc in vector_docs[email]:
            print(doc.page_content)
    
    loop = asyncio.get_running_loop()
    output = await loop.run_in_executor(None, retrieval_chains[email], {"query": prompt})
    answer = output.get("result", "")
    return answer

init_llm()
