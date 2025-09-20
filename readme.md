## Verifying Claims with Transparency

A robust fact-checking system designed to combat misinformation by verifying user-submitted claims with evidence-backed explanations. In a world where false information spreads rapidly, this tool provides clear, transparent, and accessible verdicts to help users discern truth from fiction. The backend processes claims using web searches, machine learning models, and text polishing, while the frontend (under development) offers a user-friendly interface for interaction.

> [!NOTE]
> This project is currently in the experimental and development phase, and it may sometimes produce unsatisfactory results.

---

### The Problem

Misinformation, including fake news and misleading claims, spreads quickly across digital platforms, often causing confusion, mistrust, or harm. Many existing fact-checking tools provide limited explanations or are not user-friendly for non-technical audiences. Additionally, the lack of accessible, evidence-based verification systems makes it challenging for individuals to validate claims they encounter online.

---

### Our Solution

ExplainableDocs-AI addresses these challenges by offering a fact-checking system that:

1. **Verifies Claims**: Users submit claims via a CLI or frontend interface, receiving verdicts such as "Likely True," "Likely False," or "Mixed/Uncertain."
2. **Provides Transparent Explanations**: Instead of just a verdict, the system delivers detailed explanations backed by credible web sources.
3. **Ensures Accessibility**: The CLI is easy to use, and the Vue-based frontend (in progress) aims to make fact-checking intuitive for all users.
4. **Caches Results**: Stores results in a PostgreSQL database to improve efficiency for repeated queries.

---

### Key Features

- **Explainable Verdicts**: Generates clear, evidence-based explanations with references to credible sources.
- **Machine Learning Integration**: Uses Sentence Transformers for semantic similarity and BART-MNLI for natural language inference (NLI) to classify evidence.
- **Text Polishing**: Employs Pegasus-XSUM to rephrase explanations for clarity and readability.
- **Efficient Caching**: Stores results in PostgreSQL to avoid redundant processing.
- **Scalable Architecture**: Backend is designed for potential integration with web APIs, and the frontend uses modern Vue 3 with Vite.
- **Web Search**: Leverages Google Custom Search to retrieve relevant sources for analysis.

---

### System Architecture

The system follows a modular, data-driven architecture that combines web scraping, machine learning, and database caching for robust fact-checking.

**Data Flow**:

1. **Claim Input**: Users submit a claim via the CLI (`main.py`) or the Vue frontend (under development).
2. **Cache Check**: The backend queries the PostgreSQL database (`search_log` table) to check for cached results using a normalized claim.
3. **Web Search**: If no cache is found, the system uses Google Custom Search API (`search_claim`) to fetch up to 10 relevant URLs (can be increased).
4. **Heuristic Analysis**: The `analyze_verdicts` scores search results’ titles and snippets using keyword-based heuristics to produce an initial verdict (Likely True, Likely False, Uncertain).
5. **Deep ML Analysis**: The `select_evidence_from_urls` function in `ml_models.py`:
    - Fetches and cleans web content using Trafilatura.
    - Extracts sentences and ranks them by similarity to the claim using Sentence Transformers (`all-MiniLM-L6-v2`).
    - Classifies sentences as ENTAILMENT, CONTRADICTION, or NEUTRAL using BART-MNLI (`facebook/bart-large-mnli`).
6. **Verdict Fusion**: The `simple_fuse_verdict` combines heuristic and ML results to produce a final verdict.
7. **Explanation Generation**: The `build_explanation`constructs a factual explanation from supporting and contradicting evidence.
8. **Text Polishing**: The `polish_text` in `text_polisher.py` rephrases the explanation using Pegasus-XSUM (`google/pegasus-xsum`) for fluency.
9. **Response and Caching**: The final verdict, explanation, and evidence are returned to the user and stored in PostgreSQL via `upsert_result`.

**Architecture Diagram** (Conceptual):

```
[User Input: CLI/Frontend]
          |
          v
[Cache Check: PostgreSQL]
          |
          v
[Web Search: Google Custom Search]
          |
          v
[Heuristic Analysis: Keyword Scoring]
          |
          v
[ML Analysis: Sentence Transformers + BART-MNLI]
          |
          v
[Verdict Fusion: Combine Heuristic + ML]
          |
          v
[Explanation Generation]
          |
          v
[Text Polishing: Pegasus-XSUM]
          |
          v
[Output to User + Cache in PostgreSQL]

```

---

### Tech Stack

- **Backend**:
    - **Python 3.x**: Core language for processing logic.
    - **Requests**: For HTTP requests to Google Custom Search and web scraping.
    - **Psycopg2**: PostgreSQL adapter for caching results.
    - **Transformers (Hugging Face)**: For BART-MNLI and Pegasus-XSUM models.
    - **Sentence Transformers**: For semantic similarity (`all-MiniLM-L6-v2`).
    - **Trafilatura**: For extracting clean text from web pages.
    - **python-dotenv**: For managing environment variables.
- **Frontend**:
    - **Vue 3**: JavaScript framework for building the UI.
    - **Vite**: Build tool for fast development and production builds.
    - **ESLint**: For code linting and quality.
- **Machine Learning Models**:
    - **Sentence Embedder**: `sentence-transformers/all-MiniLM-L6-v2` for ranking sentences.
    - **NLI Model**: `facebook/bart-large-mnli` for evidence classification.
    - **Polisher Model**: `google/pegasus-xsum` for explanation rephrasing.
- **Storage**: PostgreSQL for caching search results and explanations.

---

### Future Scope

- **API Integration**: Transition the CLI backend to a FastAPI-based REST API for seamless frontend integration.
- **Enhanced Frontend**: Complete the Vue 3 frontend with features like claim history and source visualization.
- **Multi-Source Search**: Incorporate additional search APIs (e.g., X search) for broader evidence collection.
- **Media Support**: Add verification for images, videos, or audio using computer vision models.
- **Multi-Language Support**: Extend NLI and polishing models to handle non-English claims.
- **Performance Optimization**: Use lighter ML models or caching mechanisms to reduce latency.

---

### Installation Guide

### Backend Setup

1. **Prerequisites**:
    - Python 3.8+
    - PostgreSQL (local or cloud-hosted)
    - Google Custom Search API key and Engine ID
    - Git 
2. **Clone the Repository**:
    
    ```bash
    git clone https://github.com/DarkenStars/ExplainableDocs-AI.git
    cd ExplainableDocs-AI/backend
    
    ```
    
3. **Install Dependencies**:
    
    ```
    .venv\Scripts\Activate.ps1

    pip install -r requirements.txt
    
    ```
    
4. **Set Up Environment Variables**:
    
    Create a `.env` file in `backend/`:
    
    ```
    API_KEY=<your-google-api-key>
    SEARCH_ENGINE_ID=<your-google-custom-search-engine-id>
    DB_NAME=<database-name>
    DB_USER=<database-user>
    DB_PASSWORD=<database-password>
    DB_HOST=<database-host e.g., localhost>
    DB_PORT=<database-port e.g., 5432>
    
    ```
    
5. **Run the Backend**:
    
    ```bash
    python main.py
    ```
    OR 

    ```bash
    python app.py # to run FastAPI 
    ```

### Frontend Setup

1. **Prerequisites**:
    - Node.js (v16+)
    - npm
2. **Navigate to Frontend Directory**:
    
    ```bash
    cd ExplainableDocs-AI/frontend
    
    ```
    
3. **Install Dependencies**:
    
    ```bash
    npm install
    
    ```
    
4. **Run Development Server**:
    
    ```bash
    npm run dev
    
    ```
    
    Access at `http://localhost:5173` (or as shown).
    
5. **Build for Production**:
    
    ```bash
    npm run build
    
    ```
    
6. **Lint Code**:
    
    ```bash
    npm run lint
    
    ```
## Run the bot

 ```bash
 RUN `python -m uvicorn app:app --host 0.0.0.0 --port 5000 --reload`

 RUN `python .\bot_tele.py`

 RUN BACKEND
`python -m uvicorn app:app --host 0.0.0.0 --port 5000 --reload` --> for bot and frontend
```
using `start.ps1`:
```ps1
Set-Location backend

.venv\Scripts\Activate.ps1

Start-Process powershell -ArgumentList "python -m uvicorn app:app --host 0.0.0.0 --port 5000 --reload"
python .\bot_tele.py
```

---

### License

This project is licensed under the MIT License. See the `LICENSE` file for details.