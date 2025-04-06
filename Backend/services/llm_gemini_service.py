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
from pydantic import Field
from core.config import settings

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")  # Ensure your .env file has GEMINI_API_KEY
DEVICE = "cuda:0" if torch.cuda.is_available() else "cpu"

# Dictionaries for per-user data:
pdf_docs_dict = {}      # key: email, value: list of processed PDF documents
retrieval_chains = {}    # key: email, value: the RetrievalQA chain for that user
vector_docs = {}         # key: email, value: the combined list of documents used for retrieval

llm_gemini = None
embeddings = None

# Import the Gemini client from google.genai
from google import genai

class GeminiLLM(LLM):
    model_name: str = Field(...)
    max_tokens: int = Field(default=500)  # This parameter may be used by the API if supported.
    temperature: float = Field(default=0.1)  # Likewise, if supported.
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
            "Use the latest market data from Alpha Vantage and historical datasets (loaded from Kaggle) as context. \n\n"
            "If the user is requesting analysis of their bank statement then look for data in 'User's Bank Account Statement Data' from the vector database. \n\n"
            "If the user asks for something irrelevant to financial advisory, such as asking for a cure for cancer, reply that you are a financial advisory chatbot and cannot answer that question. \n\n"
            "Do not include any disclaimers stating that you are not a financial advisor (e.g., 'Disclaimer: I am an AI assistant and this is not financial advice. Please consult with a qualified financial advisor before making any investment decisions.')."
        )
    )


    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        # Combine the system prompt and the user prompt.
        combined_prompt = f"{self.system_prompt}\nUser: {prompt}"
        # Initialize the Gemini client using the provided API key.
        client = genai.Client(api_key=self.api_key)
        try:
            response = client.models.generate_content(
                model=self.model_name,
                contents=combined_prompt
            )
            return response.text
        except Exception as e:
            return f"Error during Gemini API call: {str(e)}"

    @property
    def _llm_type(self) -> str:
        return "gemini_llm"

    @property
    def _identifying_params(self) -> dict:
        return {
            "model_name": self.model_name,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "system_prompt": self.system_prompt
        }

def init_llm():
    global llm_gemini, embeddings
    os.environ["GEMINI_API_KEY"] = GEMINI_API_KEY
    llm_gemini = GeminiLLM(
        model_name="gemini-2.5-pro-exp-03-25",  # gemini-2.0-flash
        api_key=GEMINI_API_KEY,
        max_tokens=1000,
        temperature=0.1
    )
    os.environ.pop("GEMINI_API_KEY", None)
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": DEVICE}
    )

def fetch_latest_financial_data() -> str:
    combined_text = "Latest Financial Market Data:\n"
    symbols = ["NSE:NIFTY50", "NSE:BANKNIFTY", "NSE:SENSEX"]
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
    return combined_text if combined_text.strip() else "No financial market data available."

def load_csv_from_dir(path: str) -> str:
    try:
        files = os.listdir(path)
        csv_files = [f for f in files if f.endswith('.csv')]
        if csv_files:
            file_path = os.path.join(path, csv_files[0])
            df = pd.read_csv(file_path)
            sample_df = df.head(50)  # Limit rows to reduce token count.
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
    # Append the latest market data (with header).
    market_data = fetch_latest_financial_data()
    corpus.append(market_data)
    # Append historical market data for each category with headers.
    historical_data = fetch_historical_data()
    for key, data in historical_data.items():
        corpus.append(f"Historical Market Data - {key.title()}:\n{data}")
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
        llm=llm_gemini,
        chain_type="stuff",
        retriever=db_vector.as_retriever(
            search_type="mmr", search_kwargs={'k': 12, 'lambda_mult': 0.25}
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
    # Prepend header indicating the document type.
    for doc in new_pdf_docs:
        doc.page_content = "User's Bank Account Statement Data\n" + doc.page_content
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

# Initialize the Gemini LLM and embeddings.
init_llm()
