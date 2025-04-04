import os
import torch
import requests
import asyncio
import pandas as pd
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
DEVICE = "cuda:0" if torch.cuda.is_available() else "cpu"

# Maintain per-user data in dictionaries:
pdf_docs_dict = {}      # key: email, value: list of processed PDF documents
retrieval_chains = {}    # key: email, value: the RetrievalQA chain for that user
vector_docs = {}         # key: email, value: the combined list of documents used for retrieval

llm_hub = None
embeddings = None

class TogetherInferenceLLM(LLM):
    model_name: str = Field(...)
    max_tokens: int = Field(default=500)
    temperature: float = Field(default=0.1)
    provider: str = Field(...)
    api_key: str = Field(...)
    system_prompt: str = Field(
        default=(
            "You are an AI assistant for a financial advisory platform targeting young professionals in India. "
            "You are given the user's monthly income and expenses (in INR), along with their investment goals. "
            "Planning is only supported for a maximum duration of 5 years; if a longer duration is requested, respond that it is currently not supported. \n\n"
            "Follow these risk-based asset allocation strategies:\n"
            "Low Risk: PPF 0%, National Pension Scheme 10%, Government Bonds 15%, PPF 25%.\n"
            "Medium Risk: FD 30%, Mid Cap 25%, Large Cap 20%, Small Cap 15%, PPF 10%.\n"
            "High Risk: FD 15%, Mid Cap 25%, Large Cap 10%, Small Cap 40%, PPF 10%.\n\n"
            "Additionally, if the user requests a target return (e.g., 'I have 100,000 INR and want a 14% return in 6 months' or "
            "'I want to invest for 5 years'), analyze historical data from NIFTY50, gold prices, and mutual funds to provide an estimate. "
            "For medium risk, aim for an annual compounded return between 12-15%, for low risk 8-10%, and for high risk 18-21%. "
            "If the user asks about options that are not present in the available data (e.g., company bonds, crypto), respond that you are currently not able to answer that request. \n\n"
            "Use the latest market data from Alpha Vantage and historical datasets (loaded from Kaggle) as context."
        )
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
        max_tokens=1000,
        temperature=0.05
    )
    os.environ.pop("HUGGINGFACEHUB_API_TOKEN", None)
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": DEVICE}
    )

def fetch_latest_financial_data() -> str:
    # Use popular Indian indices (adjust symbol format as needed for your Alpha Vantage subscription)
    symbols = ["NSE:NIFTY50", "NSE:BANKNIFTY", "NSE:SENSEX"]
    combined_text = ""
    for symbol in symbols:
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
                    combined_text += text + "\n"
                else:
                    combined_text += f"No Global Quote data for {symbol}\n"
            else:
                combined_text += f"No data available for {symbol} (status code {response.status_code})\n"
        except Exception as e:
            combined_text += f"Error fetching data for {symbol}: {str(e)}\n"
    print("==============================================================")
    print(combined_text)
    print("==============================================================")
    return combined_text if combined_text else "No financial market data available."

def load_csv_from_dir(path: str) -> str:
    try:
        files = os.listdir(path)
        csv_files = [f for f in files if f.endswith('.csv')]
        if csv_files:
            file_path = os.path.join(path, csv_files[0])
            df = pd.read_csv(file_path)
            # Limit to the first 100 rows to reduce token count.
            sample_df = df.head(50)
            return sample_df.to_csv(index=False)
    except Exception as e:
        return f"Error loading CSV from {path}: {str(e)}"
    return ""

def fetch_historical_data() -> dict:
    """
    Download and load historical datasets using kagglehub.
    Returns a dictionary with keys for each dataset and their CSV contents as text.
    """
    import kagglehub
    historical = {}
    try:
        nifty_path = kagglehub.dataset_download("rohanrao/nifty50-stock-market-data")
        nifty_data = load_csv_from_dir(nifty_path)
        historical["nifty50"] = nifty_data
        print("Loaded NIFTY50 dataset from:", nifty_path)
    except Exception as e:
        historical["nifty50"] = f"Error: {str(e)}"
    try:
        gold_path = kagglehub.dataset_download("sid321axn/gold-price-prediction-dataset")
        gold_data = load_csv_from_dir(gold_path)
        historical["gold"] = gold_data
        print("Loaded Gold dataset from:", gold_path)
    except Exception as e:
        historical["gold"] = f"Error: {str(e)}"
    try:
        mutual_funds_path = kagglehub.dataset_download("ravibarnawal/mutual-funds-india-detailed")
        mutual_funds_data = load_csv_from_dir(mutual_funds_path)
        historical["mutual_funds"] = mutual_funds_data
        print("Loaded Mutual Funds dataset from:", mutual_funds_path)
    except Exception as e:
        historical["mutual_funds"] = f"Error: {str(e)}"
    return historical

async def load_user_data(db, email: str) -> list:
    corpus = []
    user = await db.users.find_one({"email": email})
    if user:
        text = (
            f"User Data:\n"
            f"User ID: {user.get('user_id', '')}\n"
            f"Monthly Income: {user.get('income', 0)} INR\n"
            f"Monthly Expenses: {user.get('expenses', 0)} INR\n"
            f"Investment Goals: {user.get('investment_goals', '')}\n"
            f"Risk Tolerance: {user.get('risk_tolerance', 'medium')}\n"
            f"User: {user.get('username', '')}\n"
            f"Email: {user.get('email', '')}\n"
        )
        corpus.append(text)

        if "chat_history" in user and user["chat_history"]:
            for entry in user["chat_history"]:
                if isinstance(entry, (list, tuple)) and len(entry) == 2:
                    chat_text = f"User: {entry[0]}\nAI: {entry[1]}"
                elif isinstance(entry, dict):
                    chat_text = f"User: {entry.get('prompt', '')}\nAI: {entry.get('response', '')}"
                else:
                    chat_text = str(entry)
                corpus.append(chat_text)

    # Append latest market data
    market_data = fetch_latest_financial_data()
    corpus.append(market_data)
    # Append historical data (full CSV contents) to the corpus
    historical_data = fetch_historical_data()
    for key, data in historical_data.items():
        corpus.append(f"Historical data for {key}:\n{data}")
    return corpus

async def build_retrieval_chain(db, email: str):
    from langchain.docstore.document import Document
    docs = await load_user_data(db, email)
    db_docs = [Document(page_content=txt) for txt in docs]
    user_pdf_docs = pdf_docs_dict.get(email, [])
    combined_docs = db_docs + user_pdf_docs if user_pdf_docs else db_docs
    
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
            search_type="mmr", search_kwargs={'k': 3, 'lambda_mult': 0.25}
        ),
        return_source_documents=False
    )

async def process_document(document_path: str, db, email: str):
    from langchain.document_loaders import PyPDFLoader
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    loader = PyPDFLoader(document_path)
    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1024, chunk_overlap=64)
    new_pdf_docs = text_splitter.split_documents(documents)
    pdf_docs_dict[email] = pdf_docs_dict.get(email, []) + new_pdf_docs
    await build_retrieval_chain(db, email)

async def process_prompt(db, prompt: str, email: str) -> str:
    if email not in retrieval_chains:
        await build_retrieval_chain(db, email)
    if email in vector_docs:
        print(f"Using vector database documents for user {email}:")
        for doc in vector_docs[email]:
            print(doc.page_content)
    
    loop = asyncio.get_running_loop()
    output = await loop.run_in_executor(None, retrieval_chains[email], {"query": prompt})
    answer = output.get("result", "")
    return answer

init_llm()
