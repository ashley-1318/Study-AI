<div align="center">

<img src="https://img.shields.io/badge/StudyAI-Multi--Agent%20Learning-1fb89a?style=for-the-badge&logo=bookstack&logoColor=white" alt="StudyAI"/>

# 📚 StudyAI

### Multi-Agent AI Study Companion & Adaptive Learning Intelligence System

> _Transform static study materials into dynamic, interconnected learning experiences — powered by LangGraph, Groq, and RAG._

<br/>

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.39-FF4B4B?style=flat-square&logo=streamlit)](https://streamlit.io)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2-1fb89a?style=flat-square)](https://langchain-ai.github.io/langgraph)
[![Groq](https://img.shields.io/badge/Groq-Llama--3.3--70B-e8a020?style=flat-square)](https://groq.com)
[![FAISS](https://img.shields.io/badge/FAISS-Vector%20DB-4285F4?style=flat-square)](https://faiss.ai)
[![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?style=flat-square&logo=sqlite)](https://sqlite.org)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-22c55e?style=flat-square)](LICENSE)

<br/>

[🚀 Quick Start](#-quick-start) • [🏗️ Architecture](#️-system-architecture) • [⚙️ Workflow](#️-agent-pipeline-workflow) • [🛠️ Tech Stack](#️-technology-stack) • [📸 Features](#-key-features) • [📡 API Reference](#-api-reference)

<br/>

</div>

---

## 📖 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [System Architecture](#️-system-architecture)
- [Agent Pipeline Workflow](#️-agent-pipeline-workflow)
- [RAG Architecture](#-rag-retrieval-augmented-generation)
- [Technology Stack](#️-technology-stack)
- [Project Structure](#-project-structure)
- [Database Schema](#-database-schema)
- [API Reference](#-api-reference)
- [Quick Start](#-quick-start)
- [Configuration](#️-configuration)
- [Design System](#-design-system)
- [Contributing](#-contributing)

---

## 🌟 Overview

**StudyAI** is a premium, production-ready multi-agent AI study ecosystem built on **LangGraph orchestration**. It transforms static documents (PDFs, Word files, text) into a dynamic, interconnected knowledge base — automatically extracting concepts, linking them across your entire study library, generating adaptive quizzes from your own content, and scheduling intelligent revision sessions with AI-generated study guidance.

Unlike generic study tools, StudyAI answers questions **using your own notes**, generates quizzes **grounded in your actual uploaded content**, and explains **why** concepts across different documents are related.

```
Upload PDF  →  AI Understands It  →  Links to Past Materials
     ↓               ↓                        ↓
  Concepts       Smart Summary          WHY Explanation
  Extracted      Generated              "This connects to
                                         Chain Rule in
  Quiz Created ← Revision Plan ←        calculus.pdf
  From YOUR      With AI Tips           because..."
  Content
```

---

## 🚀 Key Features

### 🧠 Intelligent Multi-Agent Pipeline (10 Nodes)

| Node               | Role                                 | Technology            |
| ------------------ | ------------------------------------ | --------------------- |
| **ParseNode**      | Extract text from PDF, DOCX, TXT, MD | PyMuPDF, python-docx  |
| **ExtractNode**    | Identify concepts + definitions      | Groq Llama-3.3-70B    |
| **EmbedNode**      | Generate 384-dim vector embeddings   | sentence-transformers |
| **IndexNode**      | Store embeddings in FAISS per user   | FAISS IndexFlatL2     |
| **RetrieverNode**  | Cross-material semantic search + WHY | FAISS + Groq          |
| **SummarizerNode** | Hierarchical markdown summaries      | RAG + Groq            |
| **QuizNode**       | Context-aware MCQ/TF/FillBlank gen   | RAG + Groq            |
| **RevisionNode**   | SM-2 scheduling + AI study tips      | SM-2 Algorithm + Groq |
| **AnalyticsNode**  | Mastery scoring + coverage mapping   | SQLAlchemy            |
| **ConnectionNode** | Explainable cross-document links     | FAISS + Groq          |

---

### 🔗 Explainable Cross-Material Intelligence

StudyAI doesn't just find related documents — it **explains the conceptual link**:

```
❌  Old Way:    "Related: calculus.pdf"

✅  StudyAI:   "Backpropagation in ml_notes.pdf connects to
                Chain Rule in calculus.pdf because both
                involve computing derivatives layer-by-layer
                in a compositional function structure."
                Similarity Score: 0.87
```

---

### 💡 Smart AI Revision Tips

The revision planner goes beyond scheduling — it gives **specific actionable guidance**:

```
❌  Old Way:    "Review: Backpropagation — due tomorrow"

✅  StudyAI:   "Review: Backpropagation — due tomorrow
                💡 AI Tip: Re-read the weight update equation
                in Section 3 and manually trace gradients
                through a 2-layer network example."
                🔗 Also weak on: Gradient Descent, Chain Rule
```

---

### ❓ RAG-Powered Context-Aware Quizzes

Quizzes are generated **from your actual content**, not generic internet knowledge:

```
❌  Generic:   "What is backpropagation?"

✅  RAG Quiz:  "According to your notes, what determines
                the magnitude of the weight update during
                backpropagation?"
                → Options reference your specific content
                → Explanation cites your source material
```

---

### 📊 Advanced Learning Analytics

- **Mastery Gauge** — Speedometer-style visualization (0–100%)
- **Concept Overlap Bubble Chart** — Shows knowledge hubs across materials
- **Study Rhythm Area Chart** — Daily learning velocity tracker
- **90-Day Activity Heatmap** — GitHub-style study consistency map
- **Knowledge Gap Priority Table** — Urgent review recommendations
- **Quiz Performance Trend** — Score progression over time

---

### 💬 Ask AI — RAG Chat Interface

Chat with your entire study library in plain English:

```
You:      "What did my notes say about gradient descent?"

StudyAI:  "Based on your ml_notes.pdf (Source 1) and
           deep_learning.pdf (Source 2), gradient descent
           is an optimization algorithm that minimizes the
           loss function by iteratively updating parameters
           in the direction of the negative gradient...

           📚 2 sources used | Relevance: 0.94"
```

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        STUDENT (Browser)                            │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    STREAMLIT FRONTEND  :8501                        │
│                                                                     │
│  ┌───────────┐ ┌────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │
│  │ Dashboard │ │ Upload │ │   Quiz   │ │Summaries │ │ Revision │  │
│  │ Gauge     │ │ WS Live│ │ MCQ/TF/  │ │ RAG Gen  │ │ SM-2 +   │  │
│  │ KG Chart  │ │Progress│ │FillBlank │ │ Download │ │ AI Tips  │  │
│  └───────────┘ └────────┘ └──────────┘ └──────────┘ └──────────┘  │
│  ┌───────────┐ ┌────────┐ ┌──────────┐                             │
│  │Analytics  │ │ Ask AI │ │ History  │  Nebula Dark Theme          │
│  │ Heatmap   │ │ RAG    │ │Timeline  │  Micro-Animations           │
│  │ Overlap   │ │ Chat   │ │ Filters  │  Plotly Charts              │
│  └───────────┘ └────────┘ └──────────┘                             │
└──────────────────────────────┬──────────────────────────────────────┘
                               │  HTTP REST + WebSocket
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     FASTAPI BACKEND  :8000                          │
│                                                                     │
│   /auth/*          Google OAuth 2.0 + JWT (access 24h/refresh 30d) │
│   /materials/*     Upload, list, delete, summary                    │
│   /quiz/*          Generate, submit, history                        │
│   /concepts/*      List, related, semantic search                   │
│   /revision/*      Plan, complete, custom generate                  │
│   /analytics/*     Overview, gaps, heatmap, coverage, overlap       │
│   /history/*       Timeline, stats                                  │
│   /ask             RAG Q&A endpoint                                 │
│   /rag-summary     RAG-enhanced summary                             │
│   /ws/pipeline/*   WebSocket live agent progress                    │
│                                                                     │
│   26 endpoints · JWT auth · CORS · Background tasks                │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                  LANGGRAPH AGENT PIPELINE                           │
│                                                                     │
│   ┌────────┐   ┌─────────┐   ┌───────┐   ┌───────┐   ┌─────────┐  │
│   │ PARSE  │──▶│ EXTRACT │──▶│ EMBED │──▶│ INDEX │──▶│RETRIEVE │  │
│   │PyMuPDF │   │  Groq   │   │ STF   │   │ FAISS │   │FAISS+LLM│  │
│   │docx/txt│   │JSON NER │   │384-dim│   │ Disk  │   │WHY Expl.│  │
│   └────────┘   └─────────┘   └───────┘   └───────┘   └────┬────┘  │
│                                                             │       │
│   ┌──────────┐   ┌──────┐   ┌──────────┐   ┌───────────┐  │       │
│   │ANALYTICS │◀──│REVIS-│◀──│   QUIZ   │◀──│SUMMARIZE  │◀─┘       │
│   │Mastery   │   │ION   │   │RAG+Groq  │   │RAG+Groq   │          │
│   │Coverage  │   │SM-2+ │   │MCQ/TF/FB │   │Hierarchi- │          │
│   │Events    │   │AITips│   │          │   │cal MD     │          │
│   └──────────┘   └──────┘   └──────────┘   └───────────┘          │
│                                                                     │
│   Tools: Embedder │ FAISSStore │ RAGEngine │ QuizTool               │
└──────────────┬───────────────────────────┬─────────────────────────┘
               │                           │
               ▼                           ▼
┌──────────────────────┐     ┌─────────────────────────┐
│     SQLITE DB        │     │    FAISS VECTOR DB       │
│                      │     │                          │
│  users               │     │  {user_id}.index         │
│  study_materials     │     │  {user_id}.json          │
│  concepts            │     │                          │
│  quizzes             │     │  384-dim embeddings      │
│  quiz_answers        │     │  Per-user isolation      │
│  revision_plans      │     │  Millisecond ANN search  │
│  learning_events     │     │  Cross-material RAG      │
│                      │     │  Persisted to disk       │
│  7 tables            │     │  IndexFlatL2             │
│  SQLAlchemy ORM      │     │                          │
│  WAL mode enabled    │     │                          │
└──────────────────────┘     └─────────────────────────┘
                                          │
                                          ▼
                             ┌─────────────────────────┐
                             │       GROQ API           │
                             │                          │
                             │  llama-3.3-70b-versatile │
                             │  ~200 tokens/sec         │
                             │                          │
                             │  · Concept extraction    │
                             │  · RAG answer generation │
                             │  · Quiz generation       │
                             │  · Summary synthesis     │
                             │  · Revision tips         │
                             │  · Connection reasons    │
                             └─────────────────────────┘
```

---

## ⚙️ Agent Pipeline Workflow

Every uploaded document is processed through a **10-node stateful LangGraph pipeline**. Progress is streamed live to the frontend via WebSocket.

```
USER UPLOADS: machine_learning.pdf
                        │
                        ▼
╔═══════════════════════════════════════════════════════╗
║  NODE 1: PARSE                                   ⏳  ║
║                                                       ║
║  PyMuPDF splits PDF into text chunks                  ║
║  Minimum chunk size: 100 characters                   ║
║  Output: 47 meaningful text chunks                    ║
╚══════════════════════════╦════════════════════════════╝
                           │
                           ▼
╔═══════════════════════════════════════════════════════╗
║  NODE 2: EXTRACT                                 ⏳  ║
║                                                       ║
║  Groq Llama-3.3-70B reads each chunk                  ║
║  Identifies concepts + definitions                    ║
║  Deduplicates by name (case-insensitive)               ║
║  Output: 12 concepts saved to SQLite                  ║
║  Example: { name: "Backpropagation",                  ║
║             definition: "Algorithm for computing..."} ║
╚══════════════════════════╦════════════════════════════╝
                           │
                           ▼
╔═══════════════════════════════════════════════════════╗
║  NODE 3: EMBED                                   ⏳  ║
║                                                       ║
║  sentence-transformers encodes all 47 chunks          ║
║  Model: all-MiniLM-L6-v2 (runs locally, no API)       ║
║  Output: 47 × 384-dimensional float vectors           ║
╚══════════════════════════╦════════════════════════════╝
                           │
                           ▼
╔═══════════════════════════════════════════════════════╗
║  NODE 4: INDEX                                   ⏳  ║
║                                                       ║
║  FAISS IndexFlatL2 stores all 47 vectors              ║
║  Metadata JSON persisted alongside index              ║
║  Location: faiss_indexes/{user_id}.index              ║
║  Enables sub-millisecond semantic search              ║
╚══════════════════════════╦════════════════════════════╝
                           │
                           ▼
╔═══════════════════════════════════════════════════════╗
║  NODE 5: RETRIEVE + EXPLAIN                      ⏳  ║
║                                                       ║
║  FAISS searches across ALL past uploads               ║
║  Finds top-5 semantically similar chunks              ║
║  Excludes current material from results               ║
║  Groq generates WHY explanation per link:             ║
║                                                       ║
║  "Backpropagation in ml.pdf connects to Chain         ║
║   Rule in calculus.pdf because both involve           ║
║   computing derivatives compositionally."             ║
║                                                       ║
║  Saves related_concepts JSON to SQLite                ║
╚══════════════════════════╦════════════════════════════╝
                           │
                           ▼
╔═══════════════════════════════════════════════════════╗
║  NODE 6: SUMMARIZE (RAG-Enhanced)                ⏳  ║
║                                                       ║
║  Retrieves top-12 most relevant chunks via FAISS      ║
║  Groq generates hierarchical markdown summary:        ║
║                                                       ║
║  ## Neural Networks                                   ║
║  ### Architecture                                     ║
║  - Input, hidden, and output layers...                ║
║  ## Key Takeaways                                     ║
║  - Gradient descent minimizes the loss...             ║
║                                                       ║
║  Saves summary to StudyMaterial in SQLite             ║
╚══════════════════════════╦════════════════════════════╝
                           │
                           ▼
╔═══════════════════════════════════════════════════════╗
║  NODE 7: QUIZ (RAG-Enhanced)                     ⏳  ║
║                                                       ║
║  For each of 8 concepts:                              ║
║    → Retrieve top-4 FAISS chunks about concept        ║
║    → Groq generates 2 questions per concept           ║
║    → Questions types: MCQ / True-False / FillBlank    ║
║    → Questions grounded in student's actual PDF       ║
║    → Tagged: { rag_enhanced: true }                   ║
║                                                       ║
║  Saves 16 questions to SQLite quizzes table           ║
╚══════════════════════════╦════════════════════════════╝
                           │
                           ▼
╔═══════════════════════════════════════════════════════╗
║  NODE 8: REVISION (SM-2 + AI Tips)               ⏳  ║
║                                                       ║
║  Finds all weak concepts (mastery < 0.6)              ║
║  Applies SM-2 spaced repetition algorithm:            ║
║    quality < 3  → interval = 1 day (reset)            ║
║    rep 0        → interval = 1 day                    ║
║    rep 1        → interval = 6 days                   ║
║    rep 2+       → interval = interval × EF            ║
║                                                       ║
║  Generates AI tip per weak concept:                   ║
║  "Re-read the weight update equation and              ║
║   trace gradients through a 2-layer network."         ║
║                                                       ║
║  Upserts RevisionPlan in SQLite                       ║
╚══════════════════════════╦════════════════════════════╝
                           │
                           ▼
╔═══════════════════════════════════════════════════════╗
║  NODE 9: ANALYTICS                               ⏳  ║
║                                                       ║
║  Calculates: mastered ≥0.7 / learning 0.4-0.7 / weak  ║
║  Updates StudyMaterial.status = "done"                ║
║  Logs LearningEvent(type="upload")                    ║
║  Updates concept coverage map                         ║
╚══════════════════════════╦════════════════════════════╝
                           │
                           ▼
╔═══════════════════════════════════════════════════════╗
║  ✅ PIPELINE COMPLETE                                 ║
║                                                       ║
║  47 chunks indexed in FAISS                           ║
║  12 concepts extracted and saved                      ║
║  1 RAG-enhanced hierarchical summary                  ║
║  16 context-grounded quiz questions                   ║
║  Revision plan with AI tips for weak concepts         ║
║  Cross-material links with WHY explanations           ║
║  All steps broadcast live via WebSocket               ║
╚═══════════════════════════════════════════════════════╝
```

---

## 🔍 RAG (Retrieval-Augmented Generation)

StudyAI uses RAG in **5 places** throughout the system:

```
┌──────────────────────────────────────────────────────────────┐
│                    HOW RAG WORKS                             │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  STUDENT QUESTION: "What is backpropagation?"               │
│          │                                                   │
│          ▼                                                   │
│  ┌─────────────────────────────────────────────┐            │
│  │  STEP 1: EMBED THE QUERY                    │            │
│  │  sentence-transformers → 384-dim vector     │            │
│  └────────────────────┬────────────────────────┘            │
│                       │                                      │
│                       ▼                                      │
│  ┌─────────────────────────────────────────────┐            │
│  │  STEP 2: FAISS SEMANTIC SEARCH              │            │
│  │  Search across ALL user's uploaded content  │            │
│  │  Returns top-5 most relevant chunks         │            │
│  │  With similarity scores (L2 distance)       │            │
│  └────────────────────┬────────────────────────┘            │
│                       │                                      │
│                       ▼                                      │
│  ┌─────────────────────────────────────────────┐            │
│  │  STEP 3: BUILD CONTEXT BLOCK                │            │
│  │                                             │            │
│  │  [Source 1 | Doc: ml_notes...]              │            │
│  │  "Backpropagation is the algorithm for      │            │
│  │  computing gradients by applying the chain  │            │
│  │  rule backwards through the network..."     │            │
│  │  ---                                        │            │
│  │  [Source 2 | Doc: dl_book...]               │            │
│  │  "The gradient flows from output layer to   │            │
│  │  input layer, updating weights at each..."  │            │
│  └────────────────────┬────────────────────────┘            │
│                       │                                      │
│                       ▼                                      │
│  ┌─────────────────────────────────────────────┐            │
│  │  STEP 4: GROQ LLM GENERATES ANSWER          │            │
│  │                                             │            │
│  │  Prompt: "Answer using ONLY the context     │            │
│  │  below from student's own materials.        │            │
│  │  Cite which Source(s) you used."            │            │
│  └────────────────────┬────────────────────────┘            │
│                       │                                      │
│                       ▼                                      │
│  ┌─────────────────────────────────────────────┐            │
│  │  STEP 5: GROUNDED ANSWER WITH CITATIONS     │            │
│  │                                             │            │
│  │  "Based on your ml_notes.pdf (Source 1),    │            │
│  │  backpropagation works by [specific answer  │            │
│  │  from their actual document content]...     │            │
│  │                                             │            │
│  │  📚 2 sources used | Relevance: 0.94"       │            │
│  └─────────────────────────────────────────────┘            │
│                                                              │
│  RAG IS USED IN:                                            │
│    1. Ask AI Chat      → answers from your library          │
│    2. Quiz Generation  → questions from your content        │
│    3. Summary Gen      → best chunks across document        │
│    4. Revision Tips    → content-aware study guidance       │
│    5. Cross-Material   → explain WHY concepts link          │
└──────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Technology Stack

### Core Technologies

| Category                  | Technology                 | Version | Purpose                                       |
| ------------------------- | -------------------------- | ------- | --------------------------------------------- |
| **Agent Orchestration**   | LangGraph                  | 0.2.0   | Stateful multi-agent pipeline                 |
| **LLM Framework**         | LangChain                  | 0.3.0   | LLM abstractions + tools                      |
| **LLM Provider**          | Groq API                   | 0.11.0  | Fast LLM inference                            |
| **LLM Model (Primary)**   | Llama-3.3-70B-Versatile    | —       | Concept extraction, RAG, quiz gen, summaries  |
| **LLM Model (Secondary)** | Llama-3.1-8B-Instant       | —       | Cross-material "WHY" explanations (retriever) |
| **Embeddings**            | sentence-transformers      | 3.1.0   | Local 384-dim embeddings                      |
| **Embedding Model**       | all-MiniLM-L6-v2           | —       | Fast, accurate, free                          |
| **Vector Database**       | FAISS (faiss-cpu)          | 1.8.0   | Per-user ANN search                           |
| **Relational DB**         | SQLite + SQLAlchemy        | 2.0.35  | Persistent metadata storage                   |
| **Backend API**           | FastAPI + Uvicorn          | 0.115.0 | REST API + WebSocket                          |
| **Frontend**              | Streamlit                  | 1.39.0  | Interactive UI                                |
| **Charts**                | Plotly                     | 5.24.0  | Interactive dark-theme charts                 |
| **Graph viz**             | NetworkX                   | 3.3     | Knowledge graph rendering                     |
| **Auth**                  | python-jose + Google OAuth | 3.3.0   | JWT + OAuth 2.0                               |
| **PDF Parsing**           | PyMuPDF (fitz)             | 1.24.0  | PDF text extraction                           |
| **DOCX Parsing**          | python-docx                | 1.1.2   | Word document extraction                      |
| **HTTP Client**           | httpx + requests           | 0.27.0  | API calls                                     |
| **WebSocket**             | websockets                 | 13.0    | Live pipeline progress                        |

### Why These Choices?

```
┌─────────────────────────────────────────────────────────┐
│  WHY TWO LLM MODELS?                                    │
│  ────────────────────────────────────────────────────── │
│  🔹 Llama-3.3-70B (Primary):                            │
│     • Complex reasoning tasks                           │
│     • Concept extraction (multi-turn inference)         │
│     • Quiz generation (creativity + accuracy)           │
│     • RAG answers (comprehensive responses)             │
│                                                         │
│  🔹 Llama-3.1-8B (Secondary):                           │
│     • Short explanations (20 words)                     │
│     • Retrieval "WHY" reasoning                         │
│     • 4x faster for simple tasks                        │
│     • Lower cost for high-volume operations             │
│                                                         │
│  💡 OPTIMIZATION STRATEGY:                              │
│     Use 70B for quality → 8B for speed/cost             │
│     Retriever generates 10+ explanations per upload     │
│     8B = 90% cheaper + instant responses                │
│     70B only when depth/accuracy matters                │
└─────────────────────────────────────────────────────────┘
```

### Cost-Performance Trade-off

**Retriever Node Analysis:**

- **Per Upload:** Generates 5-10 "WHY" explanations for cross-material connections
- **Llama-3.3-70B Cost:** ~$0.59/1M tokens → $0.006 per explanation
- **Llama-3.1-8B Cost:** ~$0.05/1M tokens → $0.0005 per explanation (12x cheaper)
- **Speed:** 8B completes in <1s vs 70B's 2-3s

**100 Students × 50 Uploads/Year:**

- 70B-only: 5,000 explanations × $0.006 = **$30/year**
- 8B hybrid: 5,000 explanations × $0.0005 = **$2.50/year**
- **Savings:** $27.50 (91% reduction) with negligible quality loss

**Quality Validation:**

```python
# 20-word explanations DON'T need 70B reasoning:
# ✅ "Both discuss gradient descent as an optimization technique."
# ✅ "Backpropagation applies the chain rule from calculus."

# These don't benefit from 70B's extra parameters
```

---

## 📁 Project Structure

```
studyai/
│
├── backend/                          # FastAPI application
│   ├── main.py                       # App entry, CORS, WebSocket, startup
│   ├── auth.py                       # Google OAuth 2.0 + JWT helpers
│   ├── database.py                   # SQLAlchemy models (7 tables)
│   ├── db_utils.py                   # Query helpers (8 functions)
│   ├── seed.py                       # Development seed data script
│   │
│   ├── routes_auth.py                # /auth/* — login, callback, refresh
│   ├── routes_materials.py           # /materials/* — upload, list, delete
│   ├── routes_quiz.py                # /quiz/* — generate, submit, history
│   ├── routes_concepts.py            # /concepts/* — list, related, search
│   ├── routes_revision.py            # /revision/* — plan, complete, generate
│   ├── routes_analytics.py           # /analytics/* — overview, gaps, heatmap
│   ├── routes_history.py             # /history/* — timeline, stats
│   ├── routes_rag.py                 # /ask, /rag-summary, /search/semantic
│   │
│   ├── agents/                       # LangGraph pipeline nodes
│   │   ├── __init__.py
│   │   ├── graph.py                  # StateGraph definition + run_pipeline()
│   │   ├── parser.py                 # Node 1: PDF/DOCX/TXT chunking
│   │   ├── extractor.py              # Node 2: Groq concept extraction
│   │   ├── retriever.py              # Node 5: FAISS cross-material search
│   │   ├── summarizer.py             # Node 6: RAG-enhanced summaries
│   │   ├── quiz_gen.py               # Node 7: RAG quiz generation
│   │   ├── revision.py               # Node 8: SM-2 + AI tips
│   │   └── analytics.py              # Node 9: Mastery + event logging
│   │
│   ├── tools/                        # Reusable agent tools
│   │   ├── __init__.py
│   │   ├── embedder.py               # sentence-transformers singleton
│   │   ├── faiss_store.py            # FAISSStore class (add/search/delete)
│   │   ├── rag.py                    # RAG engine (retrieve + generate)
│   │   ├── concept_tool.py           # Groq concept extraction tool
│   │   └── quiz_tool.py              # Groq question generation tool
│   │
│   ├── uploads/                      # User uploaded files (gitignored)
│   ├── faiss_indexes/                # Per-user FAISS indexes (gitignored)
│   ├── studyai.db                    # SQLite database (gitignored)
│   └── .env                          # Environment variables (gitignored)
│
├── frontend/                         # Streamlit application
│   ├── app.py                        # Entry point + home + global CSS
│   ├── api_client.py                 # Centralized HTTP + WebSocket client
│   ├── streamlit_auth.py             # OAuth flow + token refresh + login UI
│   │
│   └── pages/                        # 8 application modules
│       ├── 1_dashboard.py            # Gauge + KG + rhythm chart + due today
│       ├── 2_upload.py               # Upload + WS progress + materials list
│       ├── 3_quiz.py                 # Standard quiz + RAG quiz tabs
│       ├── 4_summaries.py            # Summaries + RAG gen + semantic search
│       ├── 5_revision.py             # SM-2 planner + AI tips + custom plan
│       ├── 6_analytics.py            # All charts + gaps table + overlap
│       ├── 7_ask.py                  # RAG chat interface + source citations
│       └── 8_history.py              # Learning timeline + stats + filters
│
├── requirements.txt                  # All Python dependencies (pinned)
├── .env.example                      # Environment variable template
├── start_project.bat                 # One-click Windows startup script
└── README.md
```

---

## 🗄️ Database Schema

```
┌─────────────────────────────────────────────────────────────────┐
│                      SQLITE DATABASE SCHEMA                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────┐         ┌────────────────────────────┐   │
│  │      users       │         │      study_materials       │   │
│  ├──────────────────┤         ├────────────────────────────┤   │
│  │ id (PK, UUID)    │◄────────│ user_id (FK → users)       │   │
│  │ google_id        │    1:N  │ id (PK, UUID)              │   │
│  │ email (unique)   │         │ filename                   │   │
│  │ name             │         │ content_text (Text)        │   │
│  │ avatar_url       │         │ summary (Text)             │   │
│  │ created_at       │         │ chunk_count (default: 0)   │   │
│  │ last_login       │         │ status: pending|processing │   │
│  │ updated_at       │         │          done|error        │   │
│  └──────────────────┘         │ created_at, updated_at     │   │
│           │                   └────────────────────────────┘   │
│           │                             │                       │
│           │         ┌───────────────────┘                       │
│           │         ▼                                           │
│           │   ┌─────────────────────────────────────────────┐  │
│           │   │               concepts                      │  │
│           │   ├─────────────────────────────────────────────┤  │
│           │   │ id (PK, UUID)                               │  │
│           └───│ user_id (FK → users)                        │  │
│               │ material_id (FK → study_materials)          │  │
│               │ name, definition (Text)                     │  │
│               │ embedding_id                                │  │
│               │ mastery_score (Float, 0.0–1.0)              │  │
│               │ related_concepts (JSON [])                  │  │
│               │ easiness_factor (Float, 2.5)                │  │
│               │ repetition_count (Int, 0)                   │  │
│               │ interval_days (Int, 1)                      │  │
│               │ next_review (DateTime)                      │  │
│               └─────────────────────────────────────────────┘  │
│                                                                 │
│   ┌──────────────────────┐      ┌──────────────────────────┐   │
│   │       quizzes        │      │      quiz_answers        │   │
│   ├──────────────────────┤      ├──────────────────────────┤   │
│   │ id (PK, UUID)        │◄─────│ quiz_id (FK → quizzes)   │   │
│   │ user_id (FK)         │ 1:N  │ concept_id (FK nullable) │   │
│   │ material_id (FK null)│      │ question (Text)          │   │
│   │ questions (JSON [])  │      │ user_answer              │   │
│   │ difficulty           │      │ correct (Boolean)        │   │
│   │ score (nullable)     │      │ answered_at              │   │
│   │ taken_at (nullable)  │      └──────────────────────────┘   │
│   │ created_at           │                                      │
│   └──────────────────────┘                                      │
│                                                                 │
│   ┌──────────────────────┐      ┌──────────────────────────┐   │
│   │    revision_plans    │      │     learning_events      │   │
│   ├──────────────────────┤      ├──────────────────────────┤   │
│   │ id (PK, UUID)        │      │ id (PK, UUID)            │   │
│   │ user_id (FK)         │      │ user_id (FK)             │   │
│   │ concept_ids (JSON [])│      │ event_type:              │   │
│   │ schedule (JSON {})   │      │   upload|quiz|revision   │   │
│   │ priority_score       │      │   search|summary_view    │   │
│   │ next_review          │      │   ask                    │   │
│   │ created_at           │      │ concept_id (FK nullable) │   │
│   │ updated_at           │      │ result (JSON {})         │   │
│   └──────────────────────┘      │ timestamp               │   │
│                                 └──────────────────────────┘   │
│                                                                 │
│  Pragmas: WAL mode · foreign_keys=ON · synchronous=NORMAL      │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📡 API Reference

### Authentication

| Method | Endpoint         | Description                     |
| ------ | ---------------- | ------------------------------- |
| `GET`  | `/auth/login`    | Get Google OAuth URL            |
| `GET`  | `/auth/callback` | OAuth code exchange + JWT issue |
| `POST` | `/auth/refresh`  | Rotate JWT token pair           |
| `GET`  | `/auth/me`       | Current user profile            |
| `POST` | `/auth/logout`   | Stateless logout                |

### Study Materials

| Method   | Endpoint                         | Description                        |
| -------- | -------------------------------- | ---------------------------------- |
| `POST`   | `/api/v1/materials/upload`       | Upload file + launch pipeline      |
| `GET`    | `/api/v1/materials/`             | List all materials + concept count |
| `GET`    | `/api/v1/materials/{id}`         | Single material + concepts         |
| `GET`    | `/api/v1/materials/{id}/summary` | Summary + concept mastery          |
| `DELETE` | `/api/v1/materials/{id}`         | Delete file + FAISS + DB cascade   |

### Quiz

| Method | Endpoint                    | Description                         |
| ------ | --------------------------- | ----------------------------------- |
| `POST` | `/api/v1/quiz/generate`     | Adaptive quiz (weak concepts first) |
| `POST` | `/api/v1/quiz/{id}/submit`  | Grade answers + update mastery      |
| `GET`  | `/api/v1/quiz/history`      | Last 20 quizzes with scores         |
| `POST` | `/api/v1/quiz/rag-generate` | RAG quiz from content               |
| `POST` | `/api/v1/quiz/rag-submit`   | Grade RAG quiz                      |

### Revision

| Method | Endpoint                    | Description                   |
| ------ | --------------------------- | ----------------------------- |
| `GET`  | `/api/v1/revision/plan`     | Plan + due today + AI tips    |
| `POST` | `/api/v1/revision/complete` | Mark reviewed + SM-2 update   |
| `POST` | `/api/v1/revision/generate` | Custom plan (strategy + days) |

### Analytics

| Method | Endpoint                     | Description                    |
| ------ | ---------------------------- | ------------------------------ |
| `GET`  | `/api/v1/analytics/overview` | Stats summary                  |
| `GET`  | `/api/v1/analytics/gaps`     | Knowledge gaps with actions    |
| `GET`  | `/api/v1/analytics/heatmap`  | 90-day activity heatmap        |
| `GET`  | `/api/v1/analytics/coverage` | Concept coverage by topic      |
| `GET`  | `/api/v1/analytics/overlap`  | Cross-material concept overlap |

### RAG

| Method | Endpoint                  | Description                |
| ------ | ------------------------- | -------------------------- |
| `POST` | `/api/v1/ask`             | RAG Q&A from study library |
| `POST` | `/api/v1/rag-summary`     | RAG-enhanced summary       |
| `GET`  | `/api/v1/search/semantic` | Semantic chunk search      |

### History

| Method | Endpoint                | Description            |
| ------ | ----------------------- | ---------------------- |
| `GET`  | `/api/v1/history`       | Full learning timeline |
| `GET`  | `/api/v1/history/stats` | Event statistics       |

### WebSocket

| Endpoint                                  | Description                   |
| ----------------------------------------- | ----------------------------- |
| `WS /ws/pipeline/{material_id}?token=JWT` | Live pipeline progress stream |

> All endpoints return: `{"success": bool, "data": any, "error": str | null}`
> All protected endpoints require: `Authorization: Bearer <access_token>`

---

## 🚀 Quick Start

### Prerequisites

- Python **3.10+**
- [Groq API Key](https://console.groq.com/) (free)
- [Google OAuth Credentials](https://console.cloud.google.com/) (for auth)

### 1. Clone the Repository

```bash
git clone https://github.com/ashley-1318/Study-AI.git
cd Study-AI/study-ai
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
cp .env.example backend/.env
# Edit backend/.env with your credentials
```

### 4. Launch with One Click

```powershell
# Windows
.\start_project.bat
```

```bash
# Manual (any OS)
# Terminal 1 — Backend
cd backend
python seed.py
uvicorn main:app --reload --port 8000

# Terminal 2 — Frontend
cd frontend
streamlit run app.py --server.port 8501
```

### 5. Open StudyAI

| Service               | URL                          |
| --------------------- | ---------------------------- |
| **Frontend**          | http://localhost:8501        |
| **Backend API**       | http://localhost:8000        |
| **API Documentation** | http://localhost:8000/docs   |
| **Health Check**      | http://localhost:8000/health |

---

## ⚙️ Configuration

Create `backend/.env` from the template:

```env
# ── LLM ──────────────────────────────────────────────
GROQ_API_KEY=gsk_...

# ── Google OAuth ─────────────────────────────────────
# Get from: console.cloud.google.com → APIs & Services
GOOGLE_CLIENT_ID=....apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-...
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/callback

# ── JWT Security ─────────────────────────────────────
# Generate: python -c "import secrets; print(secrets.token_hex(32))"
JWT_SECRET=your-64-char-hex-secret-here

# ── Database ─────────────────────────────────────────
DATABASE_URL=sqlite:///./studyai.db

# ── File Storage ─────────────────────────────────────
FAISS_INDEX_PATH=./faiss_indexes
UPLOAD_PATH=./uploads

# ── App ──────────────────────────────────────────────
ENVIRONMENT=development
APP_NAME=StudyAI
```

---

## 🎨 Design System

StudyAI uses a custom **"Nebula Dark"** theme throughout:

```
COLOR PALETTE
─────────────────────────────────────
  #0b0c14   Background Base (deepest)
  #080a12   Sidebar Dark
  #12141f   Card / Surface
  #1e2135   Border / Divider
  #1fb89a   Mint Teal (primary accent)
  #e8a020   Gold Amber (secondary accent)
  #22c55e   Success Green (mastered)
  #ef4444   Alert Red (weak / urgent)
  #a0aec0   Muted Text (captions)

MICRO-ANIMATIONS
─────────────────────────────────────
  Page load:    fadeSlideIn 0.35s ease
  Card hover:   translateY(-2px) + teal glow shadow
  Button hover: translateY(-1px) + teal border glow
  Progress bar: gradient teal→amber animated
  Metric text:  gradient teal→amber text-fill

CHART THEME
─────────────────────────────────────
  Template:     plotly_dark
  Background:   #0b0c14
  Primary:      #1fb89a (teal)
  Secondary:    #e8a020 (amber)
  Success:      #22c55e
  Danger:       #ef4444
```

---

## 🔬 SM-2 Spaced Repetition Algorithm

StudyAI implements the **SM-2 algorithm** (used by Anki, Duolingo) for optimal memory retention:

```
INPUTS:
  quality          → 0–5 rating (0=blackout, 5=perfect)
  easiness_factor  → concept difficulty (default: 2.5)
  repetition_count → number of successful reviews
  interval_days    → current spacing interval

ALGORITHM:
  if quality < 3:
      repetition_count = 0
      interval_days = 1          # Review tomorrow

  else:
      if   repetition_count == 0: interval = 1
      elif repetition_count == 1: interval = 6
      else:                       interval = round(interval × EF)
      repetition_count += 1

  EF = max(1.3, EF + 0.1 − (5−q) × (0.08 + (5−q) × 0.02))
  next_review = utcnow + timedelta(days=interval)
  mastery_score = min(1.0, round(quality / 5.0, 2))

RESULT (typical sequence):
  Review 1: +1 day  │ Review 3: +15 days
  Review 2: +6 days │ Review 4: +35 days  (exponential spacing)

STUDYAI ENHANCEMENTS:
  + AI-generated study tip per concept (from Groq)
  + FAISS retrieves exact paragraphs to review
  + Related weak concepts flagged automatically
  + Cross-material connections surfaced
```

---

## 🤝 Contributing

Contributions are welcome! Here's how to get started:

```bash
# 1. Fork the repository
# 2. Create a feature branch
git checkout -b feature/your-feature-name

# 3. Make your changes
# 4. Run tests (if applicable)
# 5. Commit with conventional commits
git commit -m "feat: add concept clustering visualization"

# 6. Push and open a PR
git push origin feature/your-feature-name
```

### Development Tips

```bash
# Backend hot-reload
uvicorn main:app --reload --port 8000

# Streamlit auto-refresh
streamlit run app.py --server.runOnSave true

# Reset database (fresh start)
rm backend/studyai.db backend/faiss_indexes/*.index
python backend/seed.py

# View API docs
open http://localhost:8000/docs
```

---

## 📄 License

```
MIT License

Copyright (c) 2025 StudyAI

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files, to deal
in the Software without restriction, including without limitation the
rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software...
```

---

<div align="center">

**Built with ❤️ for smarter learning**

[![Groq](https://img.shields.io/badge/Powered%20by-Groq-e8a020?style=flat-square)](https://groq.com)
[![LangGraph](https://img.shields.io/badge/Orchestrated%20by-LangGraph-1fb89a?style=flat-square)](https://langchain-ai.github.io/langgraph)
[![FAISS](https://img.shields.io/badge/Vector%20Search-FAISS-4285F4?style=flat-square)](https://faiss.ai)

_If this project helped you, please ⭐ star the repository!_

</div>
