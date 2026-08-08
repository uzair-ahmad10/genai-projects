import streamlit as st
import re
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_groq import ChatGroq
from langchain_core.runnables import RunnableParallel, RunnablePassthrough, RunnableLambda
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- Page Configuration & CSS ---
st.set_page_config(page_title="AI VideoBot", layout="wide", initial_sidebar_state="collapsed")

# Custom CSS for the dark theme and orange accents (inspired by the screenshot)
st.markdown("""
    <style>
    /* Main Background */
    .stApp {
        background-color: #0b0c10;
        color: #c5c6c7;
    }
    
    /* Typography */
    h1 {
        font-family: 'Inter', sans-serif;
        font-weight: 900;
        font-size: 4rem !important;
        text-align: center;
        letter-spacing: -1.5px;
        margin-bottom: 0px !important;
        padding-bottom: 0px !important;
    }
    .title-highlight {
        color: #ff6a00;
    }
    .subtitle {
        text-align: center;
        color: #8b8d93;
        font-size: 1.1rem;
        margin-bottom: 3rem;
    }
    
    /* Inputs */
    .stTextInput>div>div>input {
        background-color: #16181f;
        color: white;
        border: 1px solid #2d303e;
        border-radius: 10px;
        padding: 15px;
    }
    
    /* Button */
    .stButton>button {
        background-color: #ff6a00;
        color: white;
        border: none;
        border-radius: 10px;
        padding: 10px 24px;
        width: 100%;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #e65f00;
        border: none;
        color: white;
    }
    
    /* Pipeline Cards */
    .pipeline-card {
        background-color: #16181f;
        border: 1px solid #2d303e;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 10px;
    }
    .pipeline-title {
        color: white;
        font-weight: bold;
        margin-bottom: 5px;
    }
    .pipeline-status {
        color: #8b8d93;
        font-size: 0.9rem;
    }
    .status-done {
        color: #4CAF50;
        float: right;
        font-size: 0.8rem;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown("""
    <h1>AI <span class='title-highlight'>VideoBot</span></h1>
    <p class='subtitle'>Your specialized AI agent for extracting insights and deep content from YouTube.</p>
""", unsafe_allow_html=True)

# --- Helper Functions ---
def extract_video_id(url):
    """Extracts the YouTube video ID from a standard URL."""
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url)
    return match.group(1) if match else None

@st.cache_resource(show_spinner=False)
def initialize_vector_store(video_id):
    """Fetches transcript and builds the FAISS index."""
    try:
        fetched_transcript = YouTubeTranscriptApi().fetch(video_id, languages=['en'])
        transcript_list = fetched_transcript.to_raw_data()
        transcript = " ".join(chunk["text"] for chunk in transcript_list)
        
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = splitter.create_documents([transcript])
        
        embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")
        vector_store = FAISS.from_documents(chunks, embeddings)
        return vector_store, None
    except TranscriptsDisabled:
        return None, "No captions available for this video."
    except Exception as e:
        return None, f"An error occurred: {e}"

def format_docs(retrieved_docs):
    return "\n\n".join(doc.page_content for doc in retrieved_docs)

# --- Main Layout ---
col1, space, col2 = st.columns([2, 0.2, 1.2])

with col1:
    st.markdown("<h4 style='color: #ff6a00; font-size: 0.9rem; letter-spacing: 1px;'>YouTube Video URL</h4>", unsafe_allow_html=True)
    video_url = st.text_input("YouTube Video URL", placeholder="Paste YouTube link here...", label_visibility="collapsed")
    
    st.markdown("<h4 style='color: #ff6a00; font-size: 0.9rem; letter-spacing: 1px; margin-top: 20px;'>User Query</h4>", unsafe_allow_html=True)
    query = st.text_input("What do you want to know?", placeholder="e.g., Can you summarize the video?", label_visibility="collapsed")
    
    run_pipeline = st.button("⚡ Run the Pipeline")

    if run_pipeline:
        if not video_url or not query:
            st.warning("Please provide both a video URL and a query.")
        else:
            video_id = extract_video_id(video_url)
            if not video_id:
                st.error("Invalid YouTube URL.")
            else:
                # Execution happens here, UI updates in col2
                pass

with col2:
    st.markdown("### Pipeline Steps", unsafe_allow_html=True)
    
    # Placeholder containers for pipeline UI
    step1_placeholder = st.empty()
    step2_placeholder = st.empty()
    step3_placeholder = st.empty()
    
    # Initial State UI
    step1_placeholder.markdown("""
        <div class="pipeline-card">
            <div class="pipeline-title">1-Fetching</div>
            <div class="pipeline-status">Waiting for input...</div>
        </div>
    """, unsafe_allow_html=True)
    step2_placeholder.markdown("""
        <div class="pipeline-card">
            <div class="pipeline-title">2-Indexing</div>
            <div class="pipeline-status">Waiting for input...</div>
        </div>
    """, unsafe_allow_html=True)
    step3_placeholder.markdown("""
        <div class="pipeline-card">
            <div class="pipeline-title">3-Synthesis</div>
            <div class="pipeline-status">Waiting for input...</div>
        </div>
    """, unsafe_allow_html=True)

# --- Execution Logic (triggered if button was pressed) ---
if run_pipeline and video_url and query and extract_video_id(video_url):
    video_id = extract_video_id(video_url)
    
    # Step 1: Fetching
    step1_placeholder.markdown("""
        <div class="pipeline-card" style="border-color: #ff6a00;">
            <div class="pipeline-title">01 Fetch Agent <span class="status-done" style="color: #ff6a00;">RUNNING...</span></div>
            <div class="pipeline-status">Downloading transcripts...</div>
        </div>
    """, unsafe_allow_html=True)
    
    vector_store, error = initialize_vector_store(video_id)
    
    if error:
        st.error(error)
        step1_placeholder.markdown(f"""
            <div class="pipeline-card" style="border-color: red;">
                <div class="pipeline-title">01 Fetch Agent <span class="status-done" style="color: red;">FAILED</span></div>
                <div class="pipeline-status">{error}</div>
            </div>
        """, unsafe_allow_html=True)
    else:
        # Step 1 Done, Step 2 visually runs (though it happened in the cache function)
        step1_placeholder.markdown("""
            <div class="pipeline-card">
                <div class="pipeline-title">01 Fetch Agent <span class="status-done">✓ DONE</span></div>
                <div class="pipeline-status">Gathered transcript data</div>
            </div>
        """, unsafe_allow_html=True)
        
        step2_placeholder.markdown("""
            <div class="pipeline-card">
                <div class="pipeline-title">02 Indexing Agent <span class="status-done">✓ DONE</span></div>
                <div class="pipeline-status">Chunked and embedded text into FAISS</div>
            </div>
        """, unsafe_allow_html=True)
        
        # Step 3: Synthesis
        step3_placeholder.markdown("""
            <div class="pipeline-card" style="border-color: #ff6a00;">
                <div class="pipeline-title">03 Synthesis Agent <span class="status-done" style="color: #ff6a00;">RUNNING...</span></div>
                <div class="pipeline-status">Querying Groq LLM...</div>
            </div>
        """, unsafe_allow_html=True)
        
        try:
            retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 4})
            llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.2)
            
            prompt = PromptTemplate(
                template="""
                You are a helpful assistant.
                Answer ONLY from the provided transcript context.
                If the context is insufficient, just say you don't know.

                {context}
                Question: {question}
                """,
                input_variables=['context', 'question']
            )
            
            parallel_chain = RunnableParallel({
                'context': retriever | RunnableLambda(format_docs),
                'question': RunnablePassthrough()
            })
            
            main_chain = parallel_chain | prompt | llm | StrOutputParser()
            
            # Generate Answer
            response = main_chain.invoke(query)
            
            step3_placeholder.markdown("""
                <div class="pipeline-card">
                    <div class="pipeline-title">03 Synthesis Agent <span class="status-done">✓ DONE</span></div>
                    <div class="pipeline-status">Generated response</div>
                </div>
            """, unsafe_allow_html=True)
            
            # Display Results back in Column 1 below inputs
            with col1:
                st.markdown("### 📝 AI Response")
                st.info(response)
                
        except Exception as e:
            st.error(f"Failed to generate response: {e}")