import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

CHROMA_API_URL = os.environ["CHROMA_API_URL"]

def get_llm(role: str = "reasoning"):

    groq = ChatGroq(
        model="llama-3.3-70b-versatile",
        api_key=os.environ["GROQ_API_KEY"],
        temperature=0.3,
    )
    gemini = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        api_key=os.environ["GOOGLE_API_KEY"],
        temperature=0.3,
    )

    primary, backup = (groq, gemini) if role == "fast" else (gemini, groq)
    return primary.with_fallbacks([backup])