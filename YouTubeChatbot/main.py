#Install libraries

from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.runnables import RunnableParallel, RunnablePassthrough, RunnableLambda
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_huggingface import ChatHuggingFace,HuggingFaceEmbeddings
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

# Indexing (Document Ingestion)
video_id = "8IU7YBgpQxg"
try:
    fetched_transcript = YouTubeTranscriptApi().fetch(video_id, languages=['en'])
    transcript_list = fetched_transcript.to_raw_data()
    transcript = " ".join(chunk["text"] for chunk in transcript_list)
    print(transcript)
    
except TranscriptsDisabled:
    print("No captions available for this video.")
except Exception as e:
    print(f"An error occurred: {e}")

# Indexing (Text Splitting)
splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
chunks = splitter.create_documents([transcript])

#  Indexing (Embedding Generation and Storing in Vector Store)
embeddings = HuggingFaceEmbeddings(model="sentence-transformers/all-MiniLM-L6-v2")
vector_store = FAISS.from_documents(chunks, embeddings)

# Retrieval
retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 4})

# Augmentation
llm = ChatGroq(model="llama-3.3-70b-versatile",temperature=0.2)

# Making the Prompt Ready
prompt = PromptTemplate(
    template="""
      You are a helpful assistant.
      Answer ONLY from the provided transcript context.
      If the context is insufficient, just say you don't know.

      {context}
      Question: {question}
    """,
    input_variables = ['context', 'question']
)

def format_docs(retrieved_docs):
  context_text = "\n\n".join(doc.page_content for doc in retrieved_docs)
  return context_text

parallel_chain = RunnableParallel({
    'context': retriever | RunnableLambda(format_docs),
    'question': RunnablePassthrough()
})

parser = StrOutputParser()
main_chain = parallel_chain | prompt | llm | parser

main_chain.invoke('Can you summarize the video')