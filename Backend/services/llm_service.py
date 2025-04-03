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

# Load environment variables
load_dotenv()
huggingface_api_token = settings.HUGGINGFACE_USER_ACCESS_TOKEN

# Check for GPU availability
DEVICE = "cuda:0" if torch.cuda.is_available() else "cpu"

# Global variables
conversation_retrieval_chain = None
chat_history = []
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
    """
    Initialize the custom LLM and its embeddings.
    """
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
    """
    Fetch the latest financial market data using a free API (e.g., Alpha Vantage)
    and return it as a text string.
    """
    symbol = "AAPL"  # Default symbol; you may extend this to multiple symbols or other endpoints.
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
                return text
        return "No financial market data available."
    except Exception as e:
        return f"Error fetching financial data: {str(e)}"

def load_db_data(db) -> list:
    """
    Fetch user-related data from the database (financial_info and user profiles)
    and combine it with the latest financial market data to build a text corpus.
    Returns a list of document strings.
    """
    corpus = []

    # Fetch user financial info from the "financial_info" collection.
    financial_cursor = db.financial_info.find()
    for fin in financial_cursor:
        text = (
            f"User ID: {fin.get('user_id', '')}\n"
            f"Income: {fin.get('income', 0)}\n"
            f"Expenses: {fin.get('expenses', 0)}\n"
            f"Investment Goals: {fin.get('investment_goals', '')}\n"
            f"Risk Tolerance: {fin.get('risk_tolerance', 'medium')}\n"
        )
        corpus.append(text)

    # Fetch user profiles from the "users" collection.
    users_cursor = db.users.find()
    for usr in users_cursor:
        text = (
            f"User: {usr.get('username', '')}\n"
            f"Email: {usr.get('email', '')}\n"
        )
        corpus.append(text)

    # Fetch the latest financial market data.
    market_data = fetch_latest_financial_data()
    corpus.append(market_data)

    return corpus

def build_retrieval_chain(db):
    """
    Build (or rebuild) the retrieval chain from the combined data
    gathered from MongoDB and the financial API.
    """
    global conversation_retrieval_chain
    docs = load_db_data(db)
    # Convert each text document to a Document object.
    from langchain.docstore.document import Document
    doc_objects = [Document(page_content=txt) for txt in docs]
    db_vector = Chroma.from_documents(doc_objects, embedding=embeddings)
    conversation_retrieval_chain = RetrievalQA.from_chain_type(
        llm=llm_hub,
        chain_type="stuff",
        retriever=db_vector.as_retriever(
            search_type="mmr", search_kwargs={'k': 6, 'lambda_mult': 0.25}
        ),
        return_source_documents=False
    )

def process_prompt(db, prompt: str) -> str:
    """
    Process a user prompt using the retrieval chain.
    If the chain has not yet been built, build it from the latest DB and financial data.
    """
    global conversation_retrieval_chain, chat_history
    if conversation_retrieval_chain is None:
        build_retrieval_chain(db)
    output = conversation_retrieval_chain({"query": prompt})
    answer = output.get("result", "")
    chat_history.append((prompt, answer))
    return answer

def process_document(document_path: str):
    """
    Process a PDF document (e.g., a user's financial statement) and update the vector store.
    This adds the PDF content to the retrieval chain.
    """
    global conversation_retrieval_chain
    from langchain.document_loaders import PyPDFLoader
    from langchain.text_splitter import RecursiveCharacterTextSplitter

    loader = PyPDFLoader(document_path)
    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1024, chunk_overlap=64)
    texts = text_splitter.split_documents(documents)
    db_vector = Chroma.from_documents(texts, embedding=embeddings)
    conversation_retrieval_chain = RetrievalQA.from_chain_type(
        llm=llm_hub,
        chain_type="stuff",
        retriever=db_vector.as_retriever(
            search_type="mmr", search_kwargs={'k': 6, 'lambda_mult': 0.25}
        ),
        return_source_documents=False,
        input_key="question"
    )

# Initialize the LLM and embeddings at module load.
init_llm()