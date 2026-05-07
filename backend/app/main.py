from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime
import os
import logging
import traceback
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.prompts import ChatPromptTemplate
from bs4 import BeautifulSoup
import requests
from langchain.tools import Tool
from langchain.agents import initialize_agent, AgentType

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from backend root
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

# Initialize FastAPI app
app = FastAPI(title="RGUKT ChatBot API", version="1.0.0")

# Configure CORS — allow all origins for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Cached singletons ────────────────────────────────────────────────────────
_embeddings = None
_chat_model = None
_vector_store = None
_retriever = None
_rag_chain = None
_section_agents = None

# Path to the ChromaDB — relative to this file's directory (backend/)
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "rgukt2_db")


def get_embeddings():
    global _embeddings
    if _embeddings is None:
        logger.info("Loading HuggingFace embeddings...")
        _embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    return _embeddings


def get_chat_model():
    global _chat_model
    if _chat_model is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key or api_key == "your_groq_api_key_here":
            raise ValueError("GROQ_API_KEY is not set. Please add it to backend/.env")
        logger.info(f"Initializing ChatGroq with key: {api_key[:8]}...")
        _chat_model = ChatGroq(api_key=api_key, model_name="llama-3.3-70b-versatile")
    return _chat_model


def get_vector_store():
    global _vector_store
    if _vector_store is None:
        if not os.path.exists(DB_PATH):
            raise FileNotFoundError(
                f"Vector database not found at {DB_PATH}. "
                "Please ensure the rgukt2_db folder exists inside the backend/ directory."
            )
        logger.info(f"Loading Chroma vector store from {DB_PATH}...")
        _vector_store = Chroma(
            persist_directory=DB_PATH,
            embedding_function=get_embeddings()
        )
    return _vector_store


def get_retriever():
    global _retriever
    if _retriever is None:
        _retriever = get_vector_store().as_retriever(search_kwargs={"k": 5})
    return _retriever


def get_rag_chain():
    global _rag_chain
    if _rag_chain is None:
        prompt = ChatPromptTemplate.from_template(
            """
You are a specialized assistant for RGUKT (Rajiv Gandhi University of Knowledge Technologies).
Answer questions accurately using the context provided.

Guidelines:
- Structure responses clearly with headings where appropriate
- Use bullet points for lists
- Be precise and factual
- Format responses in clean HTML with inline styles
- If the question is not about RGUKT, politely say you can only help with RGUKT queries

Context:
<context>
{context}
</context>

User Question: {input}

Provide a clear, well-structured answer:
"""
        )
        question_answer_chain = create_stuff_documents_chain(get_chat_model(), prompt)
        _rag_chain = create_retrieval_chain(get_retriever(), question_answer_chain)
    return _rag_chain


def get_section_agents():
    global _section_agents
    if _section_agents is None:
        chat_model = get_chat_model()

        url_groups = {
            "Academics": [
                "https://www.rgukt.ac.in/academicprogrammes.html",
                "https://www.rgukt.ac.in/academiccalender.html",
                "https://www.rgukt.ac.in/examination.html",
            ],
            "Departments": [
                "https://www.rgukt.ac.in/cse.html",
                "https://www.rgukt.ac.in/ece.html",
                "https://www.rgukt.ac.in/me.html",
                "https://www.rgukt.ac.in/ce.html",
            ],
            "Faculty": [
                "http://www.rgukt.ac.in/cse-faculty.html",
                "https://www.rgukt.ac.in/ece-faculty.html",
            ],
            "Facilities": [
                "https://www.rgukt.ac.in/hostels.html",
                "https://www.rgukt.ac.in/library/",
            ],
            "About": [
                "http://www.rgukt.ac.in/about-introduction.html",
                "http://www.rgukt.ac.in/vision-mission.html",
            ],
            "Placement": ["https://www.rgukt.ac.in/placement/"],
            "Contact": ["https://www.rgukt.ac.in/contactus.html"],
        }

        def create_section_tool(urls: list, section_name: str) -> Tool:
            def scrape_section(query: str) -> str:
                content = []
                for url in urls:
                    try:
                        resp = requests.get(url, timeout=10)
                        soup = BeautifulSoup(resp.content, "html.parser")
                        main = soup.find("div", class_="page-row")
                        if main:
                            for tag in main.find_all(["h1", "h2", "h3", "h4"]):
                                content.append(f"<h3>{tag.text.strip()}</h3>")
                            for p in main.find_all("p"):
                                if p.text.strip():
                                    content.append(f"<p>{p.text.strip()}</p>")
                            for lst in main.find_all(["ul", "ol"]):
                                items = lst.find_all("li")
                                if items:
                                    content.append("<ul>")
                                    for item in items:
                                        content.append(f"<li>{item.text.strip()}</li>")
                                    content.append("</ul>")
                    except Exception as e:
                        logger.warning(f"Error scraping {url}: {e}")
                return "\n".join(content) if content else f"No info found in {section_name} section."

            return Tool(
                name=f"RGUKT_{section_name}_Tool",
                func=scrape_section,
                description=f"Retrieves info from the RGUKT {section_name} section.",
            )

        section_tools = [
            create_section_tool(urls, section) for section, urls in url_groups.items()
        ]

        _section_agents = {
            section: initialize_agent(
                tools=[tool],
                llm=chat_model,
                agent_type=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
                verbose=False,
                handle_parsing_errors=True,
                max_iterations=2,
            )
            for section, tool in zip(url_groups.keys(), section_tools)
        }
    return _section_agents


# ─── Pydantic models ──────────────────────────────────────────────────────────

class ChatMessage(BaseModel):
    text: str
    chat_history: List[Dict[str, str]] = []


class ChatResponse(BaseModel):
    response: str
    timestamp: str
    chat_history: List[Dict[str, str]]


# ─── Startup ──────────────────────────────────────────────────────────────────

@app.on_event("startup")
async def startup_event():
    logger.info("Initializing RGUKT ChatBot API...")
    try:
        get_embeddings()
        get_chat_model()
        get_vector_store()
        get_retriever()
        get_rag_chain()
        get_section_agents()
        logger.info("✅ All components initialized successfully")
    except Exception as e:
        logger.error(f"❌ Startup error: {e}")
        raise


# ─── HTML response formatter ──────────────────────────────────────────────────

STYLES = {
    "container": 'font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; max-width: 800px; margin: 0 auto; line-height: 1.6;',
    "main_title": "color: #1a1a1a; font-size: 26px; font-weight: 700; margin-bottom: 20px; padding-bottom: 10px; border-bottom: 2px solid #e5e7eb;",
    "heading": "color: #1a1a1a; font-size: 20px; font-weight: 600; margin: 18px 0 10px 0; padding-bottom: 6px; border-bottom: 1px solid #e5e7eb;",
    "subheading": "color: #1a1a1a; font-size: 16px; font-weight: 600; margin: 14px 0 6px 0;",
    "paragraph": "color: #374151; margin: 10px 0; font-size: 15px; line-height: 1.7;",
    "list": "margin: 10px 0 10px 22px; padding: 0;",
    "list_item": "margin: 6px 0; color: #374151; font-size: 15px; line-height: 1.6;",
    "footer": "margin-top: 20px; padding-top: 14px; border-top: 1px solid #e5e7eb; color: #9ca3af; font-size: 13px;",
}


def format_raw_to_html(raw_text: str, topic: str) -> str:
    """Convert raw markdown-ish text to clean HTML."""

    def bold_to_strong(text: str) -> str:
        while "**" in text:
            text = text.replace("**", "<strong>", 1)
            if "**" in text:
                text = text.replace("**", "</strong>", 1)
        return text

    html = f'<div style="{STYLES["container"]}">'
    html += f'<h1 style="{STYLES["main_title"]}">{topic}</h1>'

    lines = raw_text.split("\n")
    in_list = False
    list_items: List[str] = []

    def flush_list() -> str:
        nonlocal in_list, list_items
        if not list_items:
            return ""
        result = f"<ul style='{STYLES['list']}'>""" + "".join(list_items) + "</ul>"
        list_items = []
        in_list = False
        return result

    for line in lines:
        line = line.strip()
        if not line:
            continue

        line = bold_to_strong(line)

        if line.startswith("### "):
            html += flush_list()
            html += f'<h3 style="{STYLES["subheading"]}">{line[4:]}</h3>'
        elif line.startswith("## "):
            html += flush_list()
            html += f'<h2 style="{STYLES["heading"]}">{line[3:]}</h2>'
        elif line.startswith("# "):
            html += flush_list()
            html += f'<h2 style="{STYLES["heading"]}">{line[2:]}</h2>'
        elif line.startswith(("- ", "* ", "• ")):
            in_list = True
            list_items.append(f'<li style="{STYLES["list_item"]}">{line[2:]}</li>')
        elif len(line) > 2 and line[0].isdigit() and line[1] in ".)" and line[2] == " ":
            in_list = True
            list_items.append(f'<li style="{STYLES["list_item"]}">{line[3:]}</li>')
        else:
            html += flush_list()
            html += f'<p style="{STYLES["paragraph"]}">{line}</p>'

    html += flush_list()
    html += f'<div style="{STYLES["footer"]}">Source: RGUKT Official Information</div>'
    html += "</div>"
    return html


# ─── Routes ───────────────────────────────────────────────────────────────────

@app.get("/")
async def read_root():
    return {"message": "RGUKT ChatBot API is running", "status": "healthy"}


@app.get("/health")
async def health_check():
    try:
        get_embeddings()
        get_chat_model()
        get_vector_store()
        return {
            "status": "healthy",
            "components": {
                "embeddings": "ok",
                "chat_model": "ok",
                "vector_store": "ok",
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/chat", response_model=ChatResponse)
async def chat(message: ChatMessage):
    try:
        logger.info(f"Chat request: {message.text[:60]}")

        # Build updated history
        history = list(message.chat_history) if message.chat_history else []
        history.append({"role": "user", "content": message.text})

        # Greetings shortcut
        greetings = {"hi", "hello", "hey", "good morning", "good afternoon", "good evening"}
        if message.text.lower().strip() in greetings:
            response_html = f'<div style="{STYLES["container"]}"><p style="{STYLES["paragraph"]}">Hello! 👋 I\'m the RGUKT Assistant. How can I help you today?</p></div>'
            history.append({"role": "assistant", "content": response_html})
            return ChatResponse(
                response=response_html,
                timestamp=datetime.now().isoformat(),
                chat_history=history,
            )

        raw_response = ""

        # ── FIX: only pass "input" to RAG chain ──
        try:
            logger.info("Invoking RAG chain...")
            rag = get_rag_chain()
            result = rag.invoke({"input": message.text})   # ← FIXED: removed chat_history
            answer = result.get("answer", "")
            logger.info(f"RAG answer (first 100 chars): {answer[:100]}")

            needs_fallback = (
                not answer.strip()
                or "I'm sorry" in answer
                or "cannot respond" in answer
                or "I can only assist" in answer
            )

            if not needs_fallback:
                raw_response = answer
            else:
                logger.info("RAG answer insufficient, trying section agents...")
                section_keywords = {
                    "Academics": ["course", "program", "curriculum", "academic", "study", "exam", "semester"],
                    "Departments": ["department", "cse", "ece", "mechanical", "chemical", "civil", "branch"],
                    "Faculty": ["faculty", "professor", "teacher", "staff", "lecturer"],
                    "Facilities": ["hostel", "library", "hospital", "facility", "lab", "canteen"],
                    "About": ["about", "vision", "mission", "vice chancellor", "director", "vc", "history"],
                    "Placement": ["placement", "job", "career", "recruitment", "company", "package"],
                    "Contact": ["contact", "address", "phone", "email", "location"],
                }

                agents = get_section_agents()
                query = message.text.lower()
                responses = []

                for section, keywords in section_keywords.items():
                    if any(kw in query for kw in keywords):
                        try:
                            logger.info(f"Trying section agent: {section}")
                            agent_result = agents[section].invoke(
                                {"input": message.text, "chat_history": []}
                            )
                            if agent_result.get("output"):
                                responses.append(agent_result["output"])
                        except Exception as e:
                            logger.warning(f"Section agent {section} error: {e}")

                raw_response = (
                    "\n".join(responses)
                    if responses
                    else "I'm sorry, I can only assist with RGUKT university-related queries."
                )

        except Exception as e:
            logger.error(f"RAG chain error: {e}")
            logger.error(traceback.format_exc())   # ← prints full stack trace to terminal
            raw_response = f"Error: {str(e)}"      # ← shows actual error in chat too

        topic = message.text.strip("?!.").title()
        response_html = format_raw_to_html(raw_response, topic)

        history.append({"role": "assistant", "content": response_html})

        return ChatResponse(
            response=response_html,
            timestamp=datetime.now().isoformat(),
            chat_history=history,
        )

    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/clear-history", response_model=ChatResponse)
async def clear_history():
    return ChatResponse(
        response="Chat history cleared.",
        timestamp=datetime.now().isoformat(),
        chat_history=[],
    )