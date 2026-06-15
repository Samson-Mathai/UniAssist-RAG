import pymupdf4llm
from langchain_text_splitters import MarkdownTextSplitter
from langchain_core.documents import Document
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from pymongo import MongoClient
import key_param
import os
import sys

# Setup DB
client = MongoClient(key_param.MONGODB_URI)
collection = client["book_mongodb_chunks"]["chunked_data"]
embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-2", google_api_key=key_param.GEMINI_API_KEY)
vector_store = MongoDBAtlasVectorSearch(collection=collection, embedding=embeddings, index_name="vector_index")
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=key_param.GEMINI_API_KEY, temperature=0)

filename = "Adjusted-Final-Undergraduate-Examination-Timetable-January-2026.pdf"
filepath = os.path.join(os.getcwd(), filename)

print("1. Checking if file is already ingested...")
existing = collection.find_one({"source": filename})
if not existing:
    print(f"2. Ingesting {filename} using pymupdf4llm...")
    md_text = pymupdf4llm.to_markdown(filepath)
    doc = Document(page_content=md_text)
    text_splitter = MarkdownTextSplitter(chunk_size=1500, chunk_overlap=200)
    splits = text_splitter.split_documents([doc])
    
    for split in splits:
        split.metadata["hasCode"] = False
        split.metadata["source"] = filename
        
    print(f"Uploading {len(splits)} chunks to MongoDB in smaller batches to avoid rate limits...")
    import time
    batch_size = 5
    for i in range(0, len(splits), batch_size):
        batch = splits[i:i+batch_size]
        print(f"Uploading batch {i//batch_size + 1}/{(len(splits)-1)//batch_size + 1}...")
        try:
            MongoDBAtlasVectorSearch.from_documents(batch, embeddings, collection=collection, index_name="vector_index")
            time.sleep(8) # Much longer sleep to respect Free Tier API rate limits!
        except Exception as e:
            print(f"Rate limit hit! Sleeping for 30 seconds... Error: {e}")
            time.sleep(30)
            MongoDBAtlasVectorSearch.from_documents(batch, embeddings, collection=collection, index_name="vector_index")
    print("Upload complete!")
else:
    print("File already ingested.")

print("\n--- QUERYING FOR 'bdat 3.1' ---")

retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 5, "pre_filter": {"hasCode": {"$eq": False}}})

template = """
You are an expert assistant helping Kenyan university students navigate complex academic documents.

First, attempt to answer the user's question using ONLY the provided context from their uploaded documents.
If you find the answer in the context, you MUST explicitly cite the [Source: filename] in your answer.

If the provided context does NOT contain the answer, you are allowed to fall back to your own general knowledge to answer the question. 
However, if you do this, you MUST begin your answer with: "⚠️ Note: This information is based on general knowledge, not your uploaded documents."

Context:
{context}

Question: {question}
"""
custom_rag_prompt = PromptTemplate.from_template(template)

def format_docs(docs):
    return "\n\n".join([f"[Source: {doc.metadata.get('source', 'Unknown')}]\n{doc.page_content}" for doc in docs])

rag_chain = {"context": retriever | format_docs, "question": RunnablePassthrough()} | custom_rag_prompt | llm | StrOutputParser()

response = rag_chain.invoke("Give me the exam timetable for bdat 3.1")
print("\n" + response)
