# 🎓 Campus AI Navigator (Multi-Document RAG)

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app-url-goes-here.streamlit.app)

A Production-Ready, Multi-Document Retrieval-Augmented Generation (RAG) Web Application built to help university students navigate dense academic policy documents, exam timetables, and government funding guidelines.

## 🚀 Live Demo
**Try the app here:** [Link to your Live Streamlit App](https://your-app-url-goes-here.streamlit.app)

## ⚙️ How the AI Pipeline Works
When a user uploads a PDF into the Web Interface, the application triggers an automated ingestion pipeline:

1. **Deduplication Check:** The system queries the MongoDB Atlas cloud database to check if the exact filename already exists, ensuring no redundant processing or wasted API tokens.
2. **Markdown Extraction:** Using `pymupdf4llm`, the application parses the uploaded document into structured Markdown, perfectly preserving the columns and rows of complex exam timetables.
3. **Semantic Chunking:** The text is passed through LangChain’s `MarkdownTextSplitter` to mathematically chop the document into smaller chunks (1,500 characters) while keeping table structures intact.
4. **Vector Embedding:** Each chunk is passed to the **Google Gemini Embedding Model**, which translates the human text into dense mathematical vectors (3,072 dimensions) representing semantic meaning.
5. **Cloud Vector Storage:** The mathematical vectors, the original text, and the source metadata (filename) are bulk-uploaded to a custom Vector Search Index hosted on **MongoDB Atlas**, making the document instantly searchable.
6. **Rate-Limit Throttling:** Built-in batching and sleep timers protect against Google API Free-Tier limits during massive multi-document uploads.

## 🛠️ Tech Stack
* **Frontend:** Python (Streamlit)
* **AI Orchestration:** LangChain
* **Database:** MongoDB Atlas (Custom Vector Search Indexing)
* **LLM & Embeddings:** Google Gemini 2.5 Flash

## ⚠️ Running Locally
If you clone this repository, you must create your own `key_param.py` file in the root directory to supply your own credentials:
```python
MONGODB_URI = "your_mongodb_connection_string"
GEMINI_API_KEY = "your_google_gemini_key"
```
