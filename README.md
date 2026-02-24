# 📚 StudyAI — Multi-Agent AI Study Companion

**StudyAI** is a premium, multi-agent AI study ecosystem designed to transform static study materials into dynamic, interconnected learning experiences. Orchestrated by **LangGraph**, it processes your documents through a sophisticated 10-node agentic pipeline to extract deep insights, generate adaptive revision plans, and provide data-driven analytics.

---

## 🚀 Key Features

### 🧠 Intelligent Multi-Agent Pipeline
The core of StudyAI is a state-graph architecture that handles:
1.  **Explainable AI Connections**: Not just "what" is related, but **"why"**. The retriever uses Llama-3.1-8B to explain semantic links between new uploads and your existing library.
2.  **Cross-Material Intelligence**: Discovers shared concepts across your entire library (e.g., *"This 'Backpropagation' concept in 'DL_Notes.pdf' connects to 'Chain Rule' in 'Calculus.pdf' because..."*).
3.  **Smart AI Revision Tips**: Actionable, content-aware study guidance. Instead of just "Review," the AI suggests specific actions like *"Re-read the weight update derivation on page 3 and trace the gradients."*
4.  **Adaptive SM-2 Spaced Repetition**: Optimizes your memory retention with a personalized study roadmap that synchronizes concept mastery across **all** your documents.
5.  **Context-Aware Quizzes**: AI-generated **MCQs** grounded in your actual study material via **RAG**.

### 📊 Advanced Learning Analytics
*   **Mastery Gauge**: A speedometer-style visualization of your overall knowledge progress.
*   **Concept Overlap Mapping**: A sophisticated bubble chart showing "knowledge hubs"—concepts that appear across multiple subjects.
*   **Study Rhythm Dashboard**: Vibrant spline-area charts tracking your daily learning velocity and streak.
*   **Knowledge Gap Analysis**: Automated identification of weak areas with prioritized "Urgent Review" recommendations.

### 🌐 Retrieval-Augmented Intelligence (RAG)
*   **Global Ask AI Chat**: A natural language Q&A interface where you can chat with your entire study library at once.
*   **Hierarchical Summaries**: Multi-level, structured overviews generated for every document.

---

## ⚙️ Workflow Architecture

StudyAI uses a modular **Agentic Pipeline** facilitated by **LangGraph**:

1.  **Ingestion**: `ParserNode` extracts content from PDF, DOCX, and Text files.
2.  **Extraction**: `ExtractorNode` identifies core academic concepts and definitions.
3.  **Indexing**: `EmbedNode` & `IndexNode` generate vector embeddings and update the **FAISS Vector DB**.
4.  **Retrieval & Linking**: `RetrieverNode` & `ConnectionNode` explain the "Why" behind cross-document relationships.
5.  **Synthesis**: `SummarizerNode`, `QuizNode`, and `RevisionNode` build the learning materials.
6.  **Insights**: `AnalyticsNode` aggregates data for the unified dashboard.

---

## 🛠️ Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Agent Orchestration** | LangGraph, LangChain |
| **LLMs (High Power)** | Groq (Llama-3.3-70B-Versatile) |
| **Embeddings** | HuggingFace (sentence-transformers/all-MiniLM-L6-v2) |
| **Database** | SQLite (Metadata), SQLAlchemy (ORM) |
| **Vector Search** | FAISS (Local Vector Storage) |
| **Frontend** | Streamlit, Plotly, Premium Vanilla CSS |
| **Parsing** | PyMuPDF (PDF), python-docx (Word) |

---

## 🎨 Design Excellence

*   **Premium Aesthetics**: A custom "Nebula Dark" theme using `#1fb89a` (Mint) and `#e8a020` (Gold) accents.
*   **Micro-Animations**: Page transitions, hover "lift" effects on cards, and button-glow interactions for a "live" UI feel.
*   **Responsive Metrics**: Gradient-text metrics and animated progress bars.
*   **One-Click Flow**: Seamless transition from upload to processing to active study.

---

## 🏁 Getting Started

### 1. Prerequisites
* Python 3.10+
* A [Groq API Key](https://console.groq.com/)

### 2. Installation
```bash
git clone https://github.com/ashley-1318/Study-AI.git
cd Study-AI/study-ai
pip install -r requirements.txt
```

### 3. Running the Project
Use the one-click startup script:
```powershell
.\start_project.bat
```
* **Frontend**: `http://localhost:8501`
* **Backend**: `http://localhost:8000`

---

## 📄 License
MIT License. Built with ❤️ for smarter learning.
