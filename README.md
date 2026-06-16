<div align="center">

# Campus Assist - RAG
AI-powered document intelligence helping Kenyan university students navigate HELB funding, clearance, campus policy, class timetables, and exam schedules — instantly.

### AI That Actually Understands Your University Documents
![Python](https://img.shields.io/badge/Python-3.11-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-UI-red)
![LangChain](https://img.shields.io/badge/LangChain-Orchestration-green)
![MongoDB Atlas](https://img.shields.io/badge/MongoDB-Atlas_Vector_Search-brightgreen)
![Gemini](https://img.shields.io/badge/Google-Gemini_2.5_Flash-orange)
![RAG](https://img.shields.io/badge/Architecture-Hybrid_RAG-purple)
![Use Case](https://img.shields.io/badge/Use_Case-EdTech_Kenya-blue)

</div>

---

## The Problem

Kenyan university students lose hundreds of hours every year to bureaucratic 
confusion and scheduling chaos.

They chase HELB loan status across offices. They decode clearance requirements 
from outdated notice boards. They hunt for answers buried in 80-page policy PDFs 
that nobody reads. They download exam timetables as dense tables and still miss 
clashes. They get wrong advice from fellow students and miss deadlines that cost 
them entire semesters.

The information exists. It is just completely inaccessible.

**CampusAssist-RAG fixes that.**

Upload your university's official documents once. Ask any question in plain 
English. Get a precise, cited answer in seconds — 24 hours a day, 7 days a week, 
with no queue, no office visit, and no guesswork.

---

## Real World Problems It Solves

Kenyan university students lose hours every year to problems that should not exist. HELB requirements change quietly and first-years miss funding they qualified for. Clearance offices run queues that stretch across entire afternoons. Policy documents are 100 pages long and nobody reads them. Exam timetables drop as dense PDFs and clashes go unnoticed until it is too late. Venue changes get announced on a noticeboard nobody checks.
CampusAssist-RAG eliminates every one of these friction points. Upload your university's official documents once — handbooks, HELB guides, class schedules, exam timetables — and any student can ask a question in plain English and get a precise, cited answer in seconds. No queue. No office visit. No advice from a coursemate who got it wrong. Every answer traces directly back to the source document it came from.This could come in very handy for new students.

---

## Deployable Use Cases

**HELB Funding Navigator**
Upload HELB's official guidelines PDF. Students ask questions like "What documents 
do I need to apply as a continuing student?" or "What is the income threshold for 
maximum funding?" and receive direct, cited answers pulled from the official source.

**Clearance Assistant**
Upload the university's clearance checklist and department requirements. Students 
confirm exactly which departments they need to visit, in what order, and what they 
need to bring — without calling anyone.

**Student Policy Bot**
Upload the student handbook. Instant answers on exam regulations, fee structures, 
disciplinary policies, academic appeals, and grading criteria.

**Class Timetable Q&A**
Upload the semester timetable PDF. Students ask "What time is my Monday BBA 204 
lecture and which room?" and receive an answer in seconds with the exact source row 
cited. The system uses table-aware extraction that preserves row and column 
structure — not flat text dumps.

**Exam Timetable Navigator**
Upload the official exam timetable. Students ask "Do I have any exam clashes?" or 
"Where and when is my CIT 312 paper?" The AI parses across the full table, 
identifies conflicts, and responds with precision including hall, date, and time.

**Academic Calendar Q&A**
"When does supplementary exam registration close?" Answered in under two seconds 
from the uploaded academic calendar PDF.

---

## Technical Architecture

CampusAssist-RAG is built on a Hybrid RAG (Retrieval-Augmented 
Generation) architecture. Every component was chosen deliberately for performance, 
cost-efficiency, and reliability at scale.

**Frontend — Streamlit**
Clean, minimal web interface. Students upload PDFs via drag-and-drop and ask 
questions in a chat-style input. No installation required on the student side.

**Orchestration — LangChain**
Manages the full pipeline: document loading, chunking, retrieval chain construction, 
prompt injection, and response generation.

**Vector Database — MongoDB Atlas Vector Search**
Custom vector search index stores and retrieves 3072-dimension semantic embeddings. 
Chosen for its managed infrastructure, horizontal scalability, and native support 
for metadata filtering — enabling strict per-source citation.

**Embeddings — Google Gemini Embedding 2**
Generates 3072-dimension mathematical vectors for every document chunk. At this 
dimension, semantic similarity search finds meaning — not just keywords. A student 
asking "when do I sit for my software paper?" correctly retrieves chunks about the 
"CIT 312 Software Engineering exam" even though none of those exact words appeared 
in the question.

**Generation — Gemini 2.5 Flash**
Fast, accurate, and cost-efficient at scale. Chosen specifically for its strong 
instruction-following capability — critical for enforcing strict citation rules and 
the hybrid fallback warning system.

**Table-Aware Timetable Extraction — pdfplumber**
Standard PDF loaders extract timetables as flat, unstructured text — destroying 
the row-column relationships that make timetable data queryable. CampusAssist-RAG uses 
a custom pdfplumber pipeline that detects tables automatically, preserves their 
structure, and converts every row into a rich natural-language sentence before 
embedding. This means a student asking "Where is my Monday 8am lecture?" gets 
an accurate answer instead of a hallucinated one.

**Hybrid RAG Fallback System**
The AI is strictly instructed to search uploaded documents first and cite every 
answer with its source filename. If the documents do not contain the answer, it 
falls back to general knowledge but MUST display:
NB: This information is based on general knowledge, not your uploaded documents.
This design eliminates silent hallucination — the most dangerous failure mode in 
student-facing AI.

---

## Production-Grade Pipeline Features

**Deduplication** — Before processing any file, the system queries MongoDB to 
check whether that filename already exists. Duplicate uploads are skipped 
silently, keeping the vector store clean.

**Smart File Routing** — Uploaded files are automatically classified at ingestion 
time. Timetable PDFs (detected by filename keywords) are routed to the 
table-aware pdfplumber pipeline. All other documents go through the standard 
RecursiveCharacterTextSplitter pipeline. No manual tagging required.

**Rate-Limit-Safe Ingestion** — Built-in time.sleep throttling between embedding 
API calls protects against Google API rate limits during bulk uploads of large 
document libraries.

**Strict Source Citation** — Every document chunk carries source metadata 
(filename, page number, table index) that is injected into every retrieval result 
and enforced at the prompt level. Students always know exactly which document 
their answer came from.

**Chunk Overlap** — RecursiveCharacterTextSplitter uses chunk_size=1000 and 
chunk_overlap=150, ensuring that answers that span paragraph boundaries are never 
lost due to arbitrary chunking cuts.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Python / Streamlit |
| Orchestration | LangChain |
| Vector Database | MongoDB Atlas Vector Search |
| Embeddings | Google Gemini Embedding 2 (3072 dimensions) |
| Generation | Google Gemini 2.5 Flash |
| Table Extraction | pdfplumber (custom pipeline) |
| Standard PDF Loader | PyMuPDF / PyMuPDFLoader |
| Text Splitting | RecursiveCharacterTextSplitter |

---

## Get Started Yourself

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/CampusIQ-KE.git
cd CampusIQ-KE

# Install dependencies
pip install -r requirements.txt

# Add your secrets to .streamlit/secrets.toml
MONGO_URI = "your_mongodb_atlas_connection_string"
GEMINI_API_KEY = "your_google_gemini_api_key"

# Run the app
streamlit run app.py
```

---

## Example Questions Students Ask

- "What documents do I need to apply for HELB as a continuing student?"
- "When is my CSC 301 lecture on Monday and which room is it in?"
- "Do I have any exam clashes this semester?"
- "Where and when is the CIT 312 Software Engineering exam?"
- "What are the clearance steps for final year students?"
- "What is the penalty for exam cheating according to university policy?"
- "When does fee payment for Semester 2 close?"
- "Who is the lecturer for BBA 204 on Thursday afternoons?"

---

## Roadmap

- [x] Multi-document PDF ingestion pipeline
- [x] Hybrid RAG with source citation and fallback warning
- [x] Table-aware timetable extraction (class and exam)
- [x] Deduplication and rate-limit-safe bulk ingestion
- [ ] Conversation memory (multi-turn follow-up questions)
- [ ] User authentication (student login per institution)
- [ ] Admin dashboard (upload documents, monitor usage)
- [ ] Multi-university deployment support
- [ ] Mobile-optimised interface
- [ ] WhatsApp bot integration for feature phone access

---

## Contributing and Deployment Interest

CampusAssist-RAG is actively being developed into a deployable SaaS tool for Kenyan 
universities — covering everything from HELB funding guidance to real-time 
timetable queries and clearance navigation.

If you are a university administrator, student union leader, developer, or EdTech 
investor interested in deploying or contributing — open an issue or reach out 
directly.

⭐ Star this repo if you believe every Kenyan student deserves faster, smarter answers.

---

## License

MIT License — see LICENSE file for details.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

GITHUB TOPICS (paste all of these into your repo's Topics field):

rag retrieval-augmented-generation langchain mongodb-atlas gemini-api 
streamlit vector-search kenya edtech university helb timetable 
exam-timetable class-schedule document-intelligence python ai-assistant 
hybrid-rag generative-ai student-portal pdfplumber

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

