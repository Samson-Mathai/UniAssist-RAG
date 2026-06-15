import streamlit as st
import os
import tempfile
import time
import pymupdf4llm
from langchain_text_splitters import MarkdownTextSplitter
from langchain_core.documents import Document
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from pymongo import MongoClient

# --- Secret Keys Management ---
# Try to load local keys. If we are on Streamlit Cloud, pull from Streamlit Secrets instead!
try:
    import key_param
    MONGODB_URI = key_param.MONGODB_URI
    GEMINI_API_KEY = key_param.GEMINI_API_KEY
except ImportError:
    MONGODB_URI = st.secrets["MONGODB_URI"]
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]

#  UI Configuration 
st.set_page_config(page_title="Campus Affairs Navigator", layout="wide")
st.title("Campus Affairs Navigator")
st.markdown("Upload multiple PDFs (like Timetables, HELB Guidelines, Student Handbooks) and ask questions! The AI will answer and cite exactly which document the answer came from.")

# Sidebar: Configuration & FAQs 
with st.sidebar:
    st.header("Settings")
    st.markdown("If you run out of tokens, you can swap your API key here without restarting or losing progress!")
    user_api_key = st.text_input("Google Gemini API Key (Optional)", type="password", help="Leave blank to use the default key in your code.")
    active_key = user_api_key if user_api_key else GEMINI_API_KEY
    
    st.divider()
    
    st.header("Frequently Asked Questions")
    with st.expander("How do I avoid losing progress?"):
        st.write("This app is incredibly smart. It checks your MongoDB database before processing a file. If it crashes on PDF #6 because you ran out of tokens, just change your API key above and upload all 16 again. It will instantly skip 1-5 because they are already saved, and resume exactly at #6!")
    with st.expander("How does it know the answer?"):
        st.write("It uses Retrieval-Augmented Generation (RAG). It mathematically searches your uploaded PDFs for the most relevant paragraphs, and hands them to Gemini to read and summarize for you.")
    with st.expander("What should I upload?"):
        st.write("Upload official HELB Manuals, Ministry of Education Funding Guidelines, University Fee Structures, or Student Rulebooks.")

#Database and AI Setup
@st.cache_resource(show_spinner=False)
def get_mongo_client():
    return MongoClient(MONGODB_URI)

# --- MongoDB Setup ---
client = get_mongo_client()
collection = client["book_mongodb_chunks"]["chunked_data"]

# --- AI Models Setup ---
embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-2", google_api_key=active_key)
vector_store = MongoDBAtlasVectorSearch(
    collection=collection,
    embedding=embeddings,
    index_name="vector_index"
)
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=active_key, temperature=0)

#  Document Ingestion 
with st.expander("Upload Campus Documents (Bulk Upload Supported)", expanded=True):
    st.info("You can drag and drop multiple PDFs here at the same time!")
    uploaded_files = st.file_uploader("Choose PDF files", type="pdf", accept_multiple_files=True)
    
    if uploaded_files:
        if st.button("Process Documents"):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            total_files = len(uploaded_files)
            
            for i, uploaded_file in enumerate(uploaded_files):
                filename = uploaded_file.name
                status_text.text(f"Checking {filename} ({i+1}/{total_files})...")
                
                # Deduplication Check: Check if this file is already in MongoDB
                existing_doc = collection.find_one({"source": filename})
                if existing_doc:
                    st.warning(f"⏩ Skipped '{filename}'. It is already in your database!")
                    progress_bar.progress((i + 1) / total_files)
                    continue # Skip to the next file!
                
                status_text.text(f"Processing {filename} ({i+1}/{total_files})...")
                
                # Save the uploaded file to a temporary location
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_file_path = tmp_file.name

                try:
                    # 1. Convert PDF to Markdown (Preserves Tables perfectly!)
                    md_text = pymupdf4llm.to_markdown(tmp_file_path)
                    
                    # Wrap the text in a Document object so LangChain can process it
                    doc = Document(page_content=md_text)
                    
                    # 2. Split the Markdown without destroying tables
                    text_splitter = MarkdownTextSplitter(
                        chunk_size=1500, # Increased chunk size to keep massive tables together
                        chunk_overlap=200
                    )
                    splits = text_splitter.split_documents([doc])
                    
                    # 3. Add metadata (CRUCIAL FOR SOURCE TRACKING)
                    for split in splits:
                        split.metadata["hasCode"] = False
                        split.metadata["source"] = filename # Track exactly which PDF this chunk came from
                    
                    if len(splits) == 0:
                        st.error(f"No text found in {filename}. It might be a scanned image.")
                        continue
                        
                    # 4. Upload to MongoDB in smaller batches to avoid rate limits
                    import time
                    batch_size = 5
                    for i in range(0, len(splits), batch_size):
                        batch = splits[i:i+batch_size]
                        status_text.text(f"Uploading batch {i//batch_size + 1} of {(len(splits)-1)//batch_size + 1} for {filename}...")
                        try:
                            MongoDBAtlasVectorSearch.from_documents(
                                documents=batch,
                                embedding=embeddings,
                                collection=collection,
                                index_name="vector_index"
                            )
                            time.sleep(8) # Much longer sleep to respect Free Tier API rate limits!
                        except Exception as e:
                            status_text.text(f"Rate limit hit! Cooling down for 30 seconds...")
                            time.sleep(30)
                            MongoDBAtlasVectorSearch.from_documents(batch, embeddings, collection=collection, index_name="vector_index")
                            
                    st.success(f"✅ Successfully embedded {filename} into MongoDB.")
                    
                except Exception as e:
                    import traceback
                    st.error(f"❌ Error processing {filename}:\n\n{traceback.format_exc()}")
                    st.stop() # Stop the loop so they can fix the error/API key
                finally:
                    os.remove(tmp_file_path)
                
                progress_bar.progress((i + 1) / total_files)
                
            status_text.text("All documents processed successfully!")

# --- Main Chat Interface ---
st.divider()
st.subheader("Ask Anything About Your Uploaded Documents")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("E.g. How do I appeal my HELB Band categorization?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Searching through your documents..."):
            
            retriever = vector_store.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 5, "pre_filter": {"hasCode": {"$eq": False}}} # Fetch top 5 paragraphs
            )
            
            # The Custom Prompt: Forcing Gemini to cite its sources!
            template = """
            You are an expert assistant helping Kenyan university students navigate complex academic and funding documents.
            
            First, attempt to answer the user's question using ONLY the provided context from their uploaded documents.
            If you find the answer in the context, you MUST explicitly cite the [Source: filename] in your answer.
            
            If the provided context does NOT contain the answer, you are allowed to fall back to your own general knowledge to answer the question. 
            However, if you do this, you MUST begin your answer with: "⚠️ Note: This information is based on general knowledge, not your uploaded documents."
            
            Context:
            {context}
            
            Question: {question}
            """
            custom_rag_prompt = PromptTemplate.from_template(template)
            
            # This function formats the text chunks AND attaches the source filename to each one
            def format_docs(docs):
                formatted = []
                for doc in docs:
                    source_name = doc.metadata.get('source', 'Unknown Document')
                    formatted.append(f"[Source: {source_name}]\n{doc.page_content}")
                return "\n\n".join(formatted)
            
            rag_chain = (
                {"context": retriever | format_docs, "question": RunnablePassthrough()}
                | custom_rag_prompt
                | llm
                | StrOutputParser()
            )
            
            try:
                response = rag_chain.invoke(prompt)
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                st.error(f"An error occurred while generating the response: {e}. If you ran out of tokens, swap your API key in the sidebar!")
