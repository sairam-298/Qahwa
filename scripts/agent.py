import os
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings, HuggingFaceEndpoint
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.schema import Document
from pathlib import Path

# Load environment variables
load_dotenv()
hf = os.getenv("HUGGINGFACE_API_TOKEN")
if not hf:
    raise EnvironmentError("❌ Missing Hugging Face token in .env")
os.environ["HUGGINGFACE_API_TOKEN"] = hf

# Greetings
GREETINGS = {
    "hi": "Hello! 😊 How can I help you today?",
    "hello": "Hey there! 👋 What would you like to ask?",
    "hey": "Hey! How can I assist you?",
    "hi qahwa": "Hi! Qahwa here! ☕ What’s on your mind?",
    "good morning": "Good morning! ☀️ What can I do for you?",
    "good evening": "Good evening! 🌙 How can I assist?",
}

# Prompt Template
PROMPT_TEMPLATE = """
You are an expert assistant for Qahwa, a boutique Arabic coffee brand. 
Answer clearly and concisely using only the context provided. Do NOT make up or guess missing information. 
Answer only the given question and nothing else. Avoid repeating the question.

Always present prices in rupees (e.g., '850 rupees' instead of '₹850' or 'Rs. 850'). 
Provide direct, actionable insights in short, helpful bullets.

**Context:**
{context}

---

**Question:** {question}
"""
PROMPT = PromptTemplate(
    input_variables=["context", "question"],
    template=PROMPT_TEMPLATE
)

# Load FAISS vectorstore from relative path
embedding = HuggingFaceEmbeddings(
    model_name="BAAI/bge-base-en-v1.5",
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True}
)

# Use relative path (project_root/faiss_index)
FAISS_INDEX_DIR = Path(__file__).resolve().parent.parent / "faiss_index"
if not FAISS_INDEX_DIR.exists():
    raise FileNotFoundError(f"❌ FAISS index not found at {FAISS_INDEX_DIR}")

vs = FAISS.load_local(
    str(FAISS_INDEX_DIR),
    embeddings=embedding,
    allow_dangerous_deserialization=True
)

# Load LLM
llm = HuggingFaceEndpoint(
    repo_id="mistralai/Mistral-7B-Instruct-v0.3",
    temperature=0.3,
    max_new_tokens=512,
    repetition_penalty=1.1,
    timeout=300,
    huggingfacehub_api_token=hf
)

# Build RetrievalQA with custom prompt
rag_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=vs.as_retriever(search_kwargs={"k": 4}),
    chain_type_kwargs={"prompt": PROMPT},
    input_key="question"
)
##################### I. QnA AGENT #############################

def query_agent(query: str):
    query_lower = query.strip().lower()
    if query_lower in GREETINGS:
        return GREETINGS[query_lower]

    response = rag_chain.invoke({"question": query})

    response_text = response.get("result", "") if isinstance(response, dict) else str(response)
    response_text = response_text.strip()

    while response_text.lower().startswith("**answer:**"):
        response_text = response_text[len("**Answer:**"):].strip()

    seen = set()
    unique_lines = []
    for line in response_text.split('\n'):
        clean_line = line.strip()
        if clean_line and clean_line not in seen:
            seen.add(clean_line)
            unique_lines.append(line)
    response_text = '\n'.join(unique_lines)

    memory_doc = Document(
        page_content=f"User: {query}\nAssistant: {response_text}",
        metadata={"source": "chat_memory", "id": f"conv_{hash(query)}"}
    )
    try:
        vs.add_documents([memory_doc])
    except Exception as e:
        print(f"⚠️ Could not add memory to FAISS: {e}")

    return response_text

########################## II. BOOKING AGENT #############################

def booking_agent(query: str):
    return (
        "📅 Sure! To book a workshop, please select a slot from the dropdown below. "
        "You’ll get a confirmation via email once done. ☕"
    )

########################## III. ROUTER AGENT #############################
BOOKING_KEYWORDS = ["book", "booking", "register", "slot", "workshop", "enroll", "session", "appointment"]

def is_booking_query(query: str) -> bool:
    return any(word in query.lower() for word in BOOKING_KEYWORDS)

def route_query(query: str):
    query_lower = query.strip().lower()
    
    if query_lower in GREETINGS:
        return GREETINGS[query_lower]

    if is_booking_query(query):
        return booking_agent(query)
    else:
        return query_agent(query)

# CLI loop (for local testing)
if __name__ == "__main__":
    print("🤖 Qahwa Agent is live! Ask your questions below.\n")
    while True:
        q = input("You: ")
        if q.lower() in ['exit','quit','bye']:
            print("👋 Bye! ")
            break
        answer = query_agent(q)
        print(f"\n{answer}\n")
