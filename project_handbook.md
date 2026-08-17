# AI Document Assistant — Personal Development & Troubleshooting Handbook

A practical record of what was tried, what failed, what was fixed, and how to run the project again.

- **Project type**: Production-style learning project
- **Working folder**: `D:\ai-document-assistant`
- **Purpose of this document**: This is written as a project journal, not as a generic tutorial. If I come back to this project after a few weeks, I should be able to understand why each technology exists, what problem it solved, what error I previously faced, and how to start the application again.

> [!NOTE]
> The attached development notes contain some version inconsistencies (for example, Angular is described once as v21 and later as Angular 18). This handbook keeps the architecture and behavior from the notes, but I should verify the exact installed version from the current frontend `package.json` before changing dependencies.

---

## 1. What I Am Building

The AI Document Assistant is a learning application where a user can register, upload PDF documents, ask questions about those documents, and receive answers generated from the document content. The main reason for building it is to understand the complete path from a frontend application to authentication, database storage, document processing, vector search, RAG, and an LLM.

```text
 [Angular 18 Frontend] (Port 4200)
       │
       ▼ (GraphQL Queries & Mutations + JWT Authorization Bearer Header)
 [Strawberry GraphQL Router] (FastAPI, Port 8000)
       │
       ├─► [Supabase Auth] (Remote User Session Verification)
       │
       ├─► [Supabase Storage] (Uploads PDF to private UUID directories)
       │
       ├─► [Local SentenceTransformer] (all-MiniLM-L6-v2: encodes text to 384-dim vectors)
       │
       ├─► [Supabase PostgreSQL] (Writes file records, logs chat bubbles, runs pgvector Cosine Search <=>)
       │
       └─► [Google Gemini API] (gemini-3.1-flash-lite: reads matched chunks & generates markdown response)
```

---

## 7. Final Technology Stack — What I Am Actually Using

- Angular frontend with TypeScript and SCSS.
- Angular Router with protected routes.
- Angular standalone component architecture and services.
- Native Angular HttpClient for the custom GraphQL client.
- Python backend.
- FastAPI web framework.
- Strawberry GraphQL.
- Supabase Auth.
- Supabase PostgreSQL.
- SQLAlchemy asynchronous ORM/database layer.
- asyncpg PostgreSQL driver.
- Supabase Storage for PDF files.
- pgvector PostgreSQL extension.
- SentenceTransformers with `all-MiniLM-L6-v2` for local 384-dimensional embeddings.
- Python RAG pipeline for retrieval and context construction.
- Google Gemini for final natural-language generation.
- Git + GitHub for source control.
- GitHub Actions is part of the planned architecture for CI/CD.

---

## 8. Important Final Stack Decision: Why Local Embeddings?

The final implementation uses `all-MiniLM-L6-v2` locally. This was a practical choice for a learning project: the model runs on the local machine, produces 384-dimensional vectors, and avoids depending on a paid embedding API. The first download is relatively large, but after the model is present, later uploads reuse it.

`PDF text ➔ chunks ➔ SentenceTransformer ➔ 384 numbers ➔ pgvector`

> [!WARNING]
> If I change the embedding model later, I must also change the pgvector dimension and re-create/re-embed existing chunks. The model and vector dimension must stay compatible.

---

## 9. How to Start the Project Again After a Break

### 9.1 Open two terminals

Terminal 1 = backend. Terminal 2 = frontend.

### 9.2 Start backend

```cmd
cd D:\ai-document-assistant\backend
.\venv\Scripts\activate
pip install -r requirements.txt
python app/main.py
```

**Expected backend behavior:**

- FastAPI starts on the configured local host/port.
- Database initialization runs during startup.
- The GraphQL endpoint is available at `/graphql`.
- The health endpoint is available at `/health`.
- The terminal should show successful database setup logs.

### 9.3 Start frontend

```cmd
cd D:\ai-document-assistant\frontend
npm install
npm start
```

Then open the Angular application at: **`http://localhost:4200`**

---

## 10. First Things to Check When Something Breaks

- Check which terminal has the error: browser/Angular, FastAPI, database, Supabase, or Gemini.
- Read the first meaningful error message instead of the last line only.
- Check whether the backend is actually running.
- Check whether the frontend is actually running.
- Check `.env` values. Do not edit only `.env.example` and expect the running server to change.
- If an authentication error appears, log out and log in again so the browser has a real Supabase session.
- If a database hostname error appears, check the connection string and DNS/network before changing application code.
- If a PostgreSQL schema error appears, compare the current database schema with `models.py`. `create_all()` is not a replacement for migrations.
- If an upload error appears, check the Supabase Storage bucket name, service credentials, database row, and backend terminal together.
- If RAG returns nothing, check that `document_chunks` actually contain text and embeddings before debugging the LLM.
- If Gemini fails, check the API key, model availability, SDK version, quota, and the configured fallback models.
- Restart the relevant server after changing environment variables or Python dependencies.

---

## 11. Verification Checklist

- [ ] Backend starts without Python import/configuration errors.
- [ ] `http://localhost:8000/health` returns a successful health response.
- [ ] `http://localhost:8000/graphql` opens and the GraphQL schema can be inspected.
- [ ] Angular starts on `http://localhost:4200`.
- [ ] Registering a user creates the user in Supabase Auth.
- [ ] Logging in produces a real Supabase session.
- [ ] Authenticated GraphQL requests carry the session token.
- [ ] Supabase PostgreSQL contains documents, document_chunks, chat_sessions and chat_messages tables.
- [ ] The documents Storage bucket exists.
- [ ] Uploading a PDF creates a Storage object and a PostgreSQL document record.
- [ ] Refreshing the browser keeps the uploaded document in the dashboard.
- [ ] PDF processing creates chunks with page/source information.
- [ ] `document_chunks` contains 384-dimensional embeddings.
- [ ] pgvector similarity search returns relevant chunks for a question.
- [ ] Chat history is saved in PostgreSQL and survives refresh.
- [ ] Gemini receives retrieved context and returns an answer based on that context.
- [ ] Questions outside the document context use the configured 'not found in the document' behavior rather than inventing an answer.

---

## 12. Security Rules I Must Not Forget

- Never put secret API keys in Angular source code.
- Never commit `backend/.env`.
- Do not expose the Supabase service-role key to the browser.
- Keep LLM API keys on the backend.
- Validate the authenticated user before accessing private documents.
- Filter document retrieval by user ownership.
- Validate PDF file type and file size.
- Do not trust a document ID supplied by the browser without checking ownership.
- Do not expose raw internal stack traces to end users.
- If a real secret was ever exposed in a public repository, rotate it rather than simply deleting it from the latest commit.

---

## 13. Project Structure I Should Expect

```text
ai-document-assistant/
├── frontend/
│   └── Angular application
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── graphql/
│   │   ├── auth/
│   │   ├── database/
│   │   ├── documents/
│   │   ├── embeddings/
│   │   ├── rag/
│   │   └── llm/
│   ├── requirements.txt
│   ├── .env
│   └── .env.example
├── docs/
├── .gitignore
└── README.md
```

The original architecture also proposed keeping architecture and development documentation under `docs/`. That is useful for this learning project because the goal is to understand the flow, not just make the application work.

---

## 14. What Each Important Backend Folder Does

| Folder/file       | Responsibility                                        | Simple way to remember it  |
| :---------------- | :---------------------------------------------------- | :------------------------- |
| **`main.py`**     | Starts FastAPI, middleware, routes and startup tasks. | Entry point / server       |
| **`config.py`**   | Loads environment configuration.                      | Settings                   |
| **`graphql/`**    | Queries, mutations and schema.                        | GraphQL contract           |
| **`auth/`**       | Validates the current user.                           | Who is calling?            |
| **`database/`**   | Connection, SQLAlchemy models and repositories.       | Permanent data             |
| **`documents/`**  | Upload, extraction, chunking and processing.          | Understand the PDF         |
| **`embeddings/`** | Turns text into vectors.                              | Meaning ➔ numbers          |
| **`rag/`**        | Retrieves relevant chunks and prepares context.       | Find the right information |
| **`llm/`**        | Calls Gemini through an abstraction.                  | Write the final answer     |

---

## 15. Git / GitHub Recovery Notes

The project previously had a nested Git repository inside `frontend`. The intended setup is one repository at the project root.

```cmd
cd D:\ai-document-assistant
rmdir /s /q frontend\.git
git init
git add .
git commit -m "chore: initialize project with frontend and backend foundations"
git remote add origin <your-github-repo-url>
git branch -M main
git push -u origin main
```

> [!NOTE]
> If origin already exists, inspect it with `git remote -v` before changing it. Do not paste credentials or tokens into commands that may be stored in shell history.

---

## 16. Useful Verification Commands

- **Check Git repository:**
  ```cmd
  git status
  git remote -v
  git log --oneline -5
  ```
- **Backend environment:**
  ```cmd
  python --version
  pip --version
  ```
- **Frontend:**
  ```cmd
  node --version
  npm --version
  ```
- **Backend health:**
  Navigate to `http://localhost:8000/health` in your browser.
- **GraphQL:**
  Navigate to `http://localhost:8000/graphql` in your browser.

---

## 17. What the RAG Pipeline Is Actually Doing

RAG is not the same thing as simply sending the entire PDF to Gemini. The project first prepares the document for search. The PDF is extracted into text, text is split into chunks, and each chunk gets a vector embedding. When the user asks a question, the question is embedded using the same model. PostgreSQL/pgvector compares that question vector with stored chunk vectors and returns the closest matches. Only then is the retrieved context sent to Gemini.

### Upload Pipeline:

`PDF ➔ Text extraction ➔ Chunks ➔ Embeddings ➔ PostgreSQL + pgvector`

### Question Pipeline:

`Question ➔ Question embedding ➔ pgvector similarity search ➔ Relevant chunks ➔ Prompt + context ➔ Gemini ➔ Answer`

---

## 18. What I Learned From the Problems

- A frontend mock can make an application look complete even when nothing is persistent yet.
- Authentication is not just login UI; the backend must know who the user is and enforce ownership.
- GraphQL has its own schema contract. Backend/database fields are not automatically GraphQL fields.
- A Storage bucket and a database table solve different problems.
- Database schema changes need migrations in serious projects. SQLAlchemy `create_all()` is useful for initial development, but it is not a full migration system.
- Vector search depends on a fixed embedding dimension. Changing the embedding model affects stored vectors.
- An LLM is the last part of the RAG pipeline, not the first. Retrieval should work before debugging answer quality.
- Environment variables are loaded by the running process. Editing `.env` normally means restarting the backend.
- When a browser still has an old auth session, backend fixes may appear not to work.
- For production, secrets, storage policies, database migrations, background workers, rate limits, and observability need stronger treatment than in this learning project.

---

## 19. Current State / Final Outcome Recorded in the Notes

All ten phases are fully completed. The final system map records Angular, FastAPI, GraphQL, Supabase Auth, Supabase Storage, PostgreSQL, local SentenceTransformer embeddings, pgvector and Gemini. The final features include light-theme UI, authenticated users, persistent documents, PDF parsing/chunking, semantic search, RAG answers, citations and persisted chat history.

---

## 20. If I Come Back After 1 Month — My Short Restart Routine

1. Open `D:\ai-document-assistant` in VS Code.
2. Check Git status.
3. Open `backend/.env` and confirm required local configuration exists. Never paste secrets into this handbook.
4. Open two terminals.
5. **Backend**: `cd D:\ai-document-assistant\backend` ➔ `.\venv\Scripts\activate` ➔ `python app/main.py`
6. **Frontend**: `cd D:\ai-document-assistant\frontend` ➔ `npm start`
7. Open `/health` and `/graphql` first.
8. Open the Angular login page and verify Supabase authentication.
9. Go to the dashboard and verify an existing document is still visible.
10. Upload a small PDF and wait for `PROCESSED`.
11. Check Supabase Storage and the `documents`/`document_chunks` tables.
12. Ask a question that is clearly answered by the PDF.
13. If the answer fails, debug in this order: auth ➔ database ➔ chunks ➔ embeddings ➔ pgvector retrieval ➔ Gemini.

---

## 21. Original Architecture Reference

The original architecture document defined the learning goal as:
`Angular ➔ GraphQL ➔ Strawberry ➔ FastAPI ➔ Supabase ➔ PostgreSQL ➔ RAG ➔ pgvector ➔ LLM ➔ Response`
and explicitly required incremental development, one phase at a time, with an explanation, files changed, commands, code, run instructions, expected output and a verification checklist before moving forward.

Incremental development made it possible to isolate errors instead of changing the whole application at once.

---

## 22. Source Basis and Editing Note

This handbook was assembled from the two project files supplied with the conversation: the original architecture/development prompt and the running development log. I intentionally wrote it as a practical personal developer journal: direct language, short explanations, problem ➔ cause ➔ fix, and repeatable run steps. I did not copy real credentials into this document.

_End of handbook — update this file whenever the stack or project flow changes._
