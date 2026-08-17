# AI Document Assistant

A production-style learning application demonstrating the complete Retrieval-Augmented Generation (RAG) flow:

**Angular (Light Theme) ➔ GraphQL (Strawberry) ➔ FastAPI ➔ Supabase (Auth & Storage) ➔ PostgreSQL (pgvector) ➔ LLM**

## Project Structure

- `/frontend`: Angular single-page application.
- `/backend`: FastAPI Python backend with Strawberry GraphQL.
- `/docs`: Architecture and development documentation.

## How to Run Locally

Check the instructions inside:

- [Architecture Documentation](docs/architecture.md)
- [Frontend README](frontend/README.md)

AI DOCUMENT ASSISTANT

Personal Development & Troubleshooting Handbook

A practical record of what was tried, what failed, what was fixed, and how to run the project again

Project type: Production-style learning project

Working folder: D:\ai-document-assistant

Purpose of this document: This is written as a project journal, not as a generic tutorial. If I come back to this project after a few weeks, I should be able to understand why each technology exists, what problem it solved, what error I previously faced, and how to start the application again.

Note: The attached development notes contain some version inconsistencies (for example, Angular is described once as v21 and later as Angular 18). This handbook keeps the architecture and behavior from the notes, but I should verify the exact installed version from the current frontend package.json before changing dependencies.

1. What I Am Building

The AI Document Assistant is a learning application where a user can register, upload PDF documents, ask questions about those documents, and receive answers generated from the document content. The main reason for building it is to understand the complete path from a frontend application to authentication, database storage, document processing, vector search, RAG, and an LLM.

User
↓
Angular
↓
GraphQL / REST upload
↓
FastAPI + Strawberry
↓
Supabase Auth / PostgreSQL / Storage
↓
PDF extraction → chunking
↓
SentenceTransformer embeddings
↓
pgvector similarity search
↓
Gemini LLM
↓
Answer + citations
↓
Angular chat UI

The original architecture plan describes the main flow as:

Angular → GraphQL → Strawberry → FastAPI → Supabase → PostgreSQL → RAG → pgvector → LLM → Response

The final implementation notes also use a REST upload endpoint for the actual PDF file transfer. That is important to remember: GraphQL is used for application queries/mutations, while the file upload path became a REST POST endpoint.

2. Why I Chose This Stack

Area

Final choice

Why it is here

Important note

Frontend

Angular + TypeScript + SCSS

Build the UI and learn modern Angular structure, routing, services and guards.

Light theme was chosen during development.

API

Python + FastAPI

Main backend server, configuration, uploads, database access and AI pipeline.

Runs locally with Uvicorn through app/main.py.

GraphQL

Strawberry GraphQL

Typed queries/mutations between Angular and Python.

Angular uses a lightweight HttpClient-based GraphQL service rather than Apollo.

Authentication

Supabase Auth

Registration, login, sessions and user identity.

Real Supabase tokens replaced the initial mock token.

Database

Supabase PostgreSQL

Permanent application data and chat/document records.

SQLAlchemy + asyncpg are used from FastAPI.

Vector search

pgvector

Stores embeddings and performs semantic similarity search.

Uses cosine distance operator <=>.

Embeddings

SentenceTransformer all-MiniLM-L6-v2

Creates semantic vectors locally without a paid embedding API.

384 dimensions; first model download is roughly 120 MB.

File storage

Supabase Storage

Stores the actual uploaded PDF files.

Files are isolated under the user's UUID folder.

RAG

Python RAG pipeline

Retrieves the most relevant document chunks before asking the LLM.

User/document ownership is part of retrieval rules.

LLM

Google Gemini

Turns retrieved document context into a natural-language answer.

Provider is kept behind an LLM service abstraction.

Source control

Git + GitHub

Tracks project history and allows the complete project to be pushed.

Repository must be initialized at project root.

CI/CD

GitHub Actions (planned/architecture)

Future automation for checks/deployment.

Keep this separate from local development until needed.

3. Technology Options I Considered / Tried

The project was deliberately kept on the Angular + Python architecture. Some alternatives were considered during the AI integration work.

Gemini was selected as the LLM because it could be called directly from the Python backend and fit the existing FastAPI architecture.

A Vercel AI SDK / React-style useChat approach was considered but not adopted. The notes point out that useChat is designed around React/Next.js patterns, while this project uses Angular.

Using a JavaScript @ai-sdk/google provider would also have meant changing the Python/FastAPI backend architecture. That would have added a Node.js backend just for the AI layer, which was not useful for this learning goal.

OpenAI, Gemini, Qwen, or another provider can still be added later because the intended design uses an LLM service abstraction.

The embedding side deliberately uses a local SentenceTransformer model instead of depending on a paid embedding API.

4. Development Phases and What Each Phase Solved

Phase

Area

What was done

Why it mattered

Phase 1

Angular UI

Created login, register, dashboard, document list/upload UI and chat UI using mock services.

Learned standalone components, routing, guards, services, forms and UI structure.

Phase 2

FastAPI foundation

Created Python backend, .env configuration, CORS, logging and /health endpoint.

Proved Angular could communicate with the backend before adding complexity.

Phase 3

Strawberry GraphQL

Added /graphql, schema, queries, mutations and Angular GraphQL helper.

Proved Angular → GraphQL → Strawberry → FastAPI flow.

Phase 4

Supabase Auth

Connected real registration/login/session handling and passed auth tokens to the backend.

Established real user identity and ownership checks.

Phase 5

PostgreSQL

Connected SQLAlchemy + asyncpg to Supabase PostgreSQL and created document/chat tables.

Solved temporary-memory persistence and created a real data model.

Phase 6

Document upload

Added REST PDF upload to FastAPI, Supabase Storage and database metadata tracking.

Solved disappearing files after refresh.

Phase 7

PDF processing

Extracted PDF text, cleaned it and split it into chunks with page/source metadata.

Prepared documents for semantic search.

Phase 8

Embeddings + pgvector

Generated 384-dimensional vectors with SentenceTransformer and stored them in pgvector.

Made semantic similarity search possible.

Phase 9

RAG retrieval

Converted questions to vectors, searched pgvector and returned relevant chunks/citations.

Connected the user's question to the correct document context.

Phase 10

Gemini LLM

Sent retrieved context to Gemini and returned a natural answer.

Completed the RAG answer generation flow.

5. Major Problems I Faced and How I Overcame Them

5.1 Angular uploads disappeared after refresh

What happened: The first version stored uploaded documents only in temporary browser/application state. A browser refresh restarted Angular and the mock list came back.

How it was fixed: Moved document persistence to PostgreSQL and actual PDF storage to Supabase Storage. The dashboard now reads saved document metadata instead of relying on a temporary list.

What I should remember: Remember: database metadata and Storage file are two different things. PostgreSQL tells the app that the file exists; Supabase Storage holds the actual PDF.

Source note: See the original project development log for the exact terminal/output context.

5.2 FastAPI could not start because of the Python import path

What happened: Running python app/main.py caused Python to have trouble resolving the app package/imports.

How it was fixed: main.py was adjusted so the parent directory is available to Python, allowing the backend to be started from the backend folder.

What I should remember: If this comes back, first confirm the terminal is inside D:\ai-document-assistant\backend and run python app/main.py.

Source note: See the original project development log for the exact terminal/output context.

5.3 Git repository was initialized inside frontend

What happened: frontend had its own hidden .git folder. That made the root D:\ai-document-assistant folder behave differently from the intended single repository.

How it was fixed: Deleted frontend\.git, initialized Git at the project root, added all project folders, committed, connected the personal GitHub remote and pushed.

What I should remember: For a project with frontend + backend + docs, the root should normally be the repository boundary.

Source note: See the original project development log for the exact terminal/output context.

5.4 JWT algorithm / mock token problem

What happened: During the transition from mock authentication to real Supabase Auth, the browser still had the old mock_token in local storage. The backend then tried to treat it as a real JWT.

How it was fixed: Logged out, created/logged into a real Supabase user, and replaced the mock session. Later, the backend verification was changed to use Supabase's server-side user verification instead of assuming one local signing algorithm.

What I should remember: When authentication behavior changes, always clear the old session and log in again before debugging the backend token.

Source note: See the original project development log for the exact terminal/output context.

5.5 JWT secret was wrong

What happened: A UUID-like value was placed where the real JWT secret was expected.

How it was fixed: Copied the correct secret from the Supabase JWT settings and restarted FastAPI so the .env value was reloaded.

What I should remember: Never guess which Supabase key is which. Public keys, service-role keys and JWT signing secrets have different purposes.

Source note: See the original project development log for the exact terminal/output context.

5.6 Supabase database hostname / DNS error

What happened: The backend produced socket.gaierror: [Errno 11001] getaddrinfo failed. The machine could not resolve the Supabase database hostname.

How it was fixed: Checked DNS/network connectivity, then considered the Supabase connection pooler and used the Supabase-provided pooler connection string with the asyncpg SQLAlchemy prefix.

What I should remember: If the error is getaddrinfo failed, do not immediately change Python code. First check the actual hostname, DNS and network path.

Source note: See the original project development log for the exact terminal/output context.

5.7 SQLAlchemy could not reference auth.users

What happened: SQLAlchemy's metadata registry did not know about Supabase's externally managed auth.users table, so a normal ForeignKey('auth.users.id') caused NoReferencedTableError.

How it was fixed: The project moved the Supabase auth foreign-key creation to PostgreSQL DDL executed after the application tables are created.

What I should remember: Supabase system tables are not normal SQLAlchemy models in this project. Treat that boundary carefully.

Source note: See the original project development log for the exact terminal/output context.

5.8 Existing document_chunks table had no embedding column

What happened: Phase 5 created document_chunks before Phase 8 introduced the embedding field. SQLAlchemy create_all() does not perform a general schema migration for an existing table.

How it was fixed: Because this is a learning/development project, the existing tables were dropped and recreated so the schema matched the current model.

What I should remember: In a real production system, use proper database migrations instead of dropping tables.

Source note: See the original project development log for the exact terminal/output context.

5.9 Missing text import during pgvector setup

What happened: A Python import required by the database/DDL code was missing.

How it was fixed: Restored the text import in connection.py and restarted the backend.

What I should remember: When a Python startup error points to a missing name/import, fix the smallest failing layer before changing database logic.

Source note: See the original project development log for the exact terminal/output context.

5.10 GraphQL schema mismatch for errorMessage

What happened: Angular requested errorMessage, but the Strawberry DocumentType did not expose that field.

How it was fixed: Added errorMessage to the GraphQL type and mapped it to the database field.

What I should remember: GraphQL has a strict schema. A field existing in the database is not enough; the GraphQL type must expose it too.

Source note: See the original project development log for the exact terminal/output context.

5.11 Gemini model returned 404

What happened: The selected Gemini model name was not available for the account/API version in use, and the Python SDK/model naming also changed during development.

How it was fixed: Updated the Gemini library and added model fallback logic so the service can try supported model targets instead of failing on the first model.

What I should remember: Do not assume that a model name from an old tutorial will always be available. Keep model configuration in one place.

Source note: See the original project development log for the exact terminal/output context.

5.12 Gemini key / environment issue

What happened: A key was pasted/configured incorrectly during setup, and changes to .env were not visible until the backend was restarted.

How it was fixed: Corrected the environment configuration and restarted FastAPI after changing the key.

What I should remember: Whenever .env changes, restart the backend. Also keep real keys out of source control.

Source note: See the original project development log for the exact terminal/output context.

5.13 Chat still showed mock responses before RAG/LLM was connected

What happened: The frontend chat service was still using the mock Phase 1 service even though document chunks and embeddings already existed in the database.

How it was fixed: Replaced the mock chat path with the Phase 9 retrieval flow and then connected Gemini in Phase 10.

What I should remember: This is a good reminder that backend capability and frontend usage are separate things. A feature can exist in the backend but still not be used by the UI.

Source note: See the original project development log for the exact terminal/output context.

6. The Final Working Architecture

LOGIN / USER FLOW
Angular
↓
Supabase Auth
↓
Supabase session token
↓
Angular GraphQL requests carry Authorization: Bearer <token>
↓
FastAPI verifies the user with Supabase
↓
Strawberry resolvers receive authenticated user context

UPLOAD FLOW
Angular
↓
POST /api/documents/upload
↓
FastAPI validates user + PDF type + file size
↓
Supabase Storage
└── <user UUID>/<file>.pdf
↓
PostgreSQL documents row
↓
Background processing
↓
PDF text extraction
↓
Cleaning + chunking
↓
SentenceTransformer embeddings
↓
document_chunks + pgvector

QUESTION / RAG FLOW
User question
↓
Angular chat
↓
GraphQL sendMessage
↓
FastAPI
↓
Convert question to 384-dim embedding
↓
pgvector cosine similarity search (<=>)
↓
Top relevant chunks from the user's document
↓
Build context + prompt
↓
Google Gemini
↓
Natural-language answer
↓
Save question + answer to chat_messages
↓
Angular displays answer + citations

7. Final Technology Stack — What I Am Actually Using

Angular frontend with TypeScript and SCSS.

Angular Router with protected routes.

Angular standalone component architecture and services.

Native Angular HttpClient for the custom GraphQL client.

Python backend.

FastAPI web framework.

Strawberry GraphQL.

Supabase Auth.

Supabase PostgreSQL.

SQLAlchemy asynchronous ORM/database layer.

asyncpg PostgreSQL driver.

Supabase Storage for PDF files.

pgvector PostgreSQL extension.

SentenceTransformers with all-MiniLM-L6-v2 for local 384-dimensional embeddings.

Python RAG pipeline for retrieval and context construction.

Google Gemini for final natural-language generation.

Git + GitHub for source control.

GitHub Actions is part of the planned architecture for CI/CD.

8. Important Final Stack Decision: Why Local Embeddings?

The final implementation uses all-MiniLM-L6-v2 locally. This was a practical choice for a learning project: the model runs on the local machine, produces 384-dimensional vectors, and avoids depending on a paid embedding API. The first download is relatively large, but after the model is present, later uploads reuse it.

PDF text → chunks → SentenceTransformer → 384 numbers → pgvector

Note: If I change the embedding model later, I must also change the pgvector dimension and re-create/re-embed existing chunks. The model and vector dimension must stay compatible.

9. How to Start the Project Again After a Break

This is the section I should follow first when I return to the project.

9.1 Open two terminals

Terminal 1 = backend. Terminal 2 = frontend.

9.2 Start backend

cd D:\ai-document-assistant\backend
.\venv\Scripts\activate
pip install -r requirements.txt
python app/main.py

Expected backend behavior:

FastAPI starts on the configured local host/port.

Database initialization runs during startup.

The GraphQL endpoint is available at /graphql.

The health endpoint is available at /health.

If the project uses database-backed startup initialization, the terminal should show successful database setup logs.

9.3 Start frontend

cd D:\ai-document-assistant\frontend
npm install
npm start

Then open the Angular application at:

http://localhost:4200

10. First Things to Check When Something Breaks

Check which terminal has the error: browser/Angular, FastAPI, database, Supabase, or Gemini.

Read the first meaningful error message instead of the last line only.

Check whether the backend is actually running.

Check whether the frontend is actually running.

Check .env values. Do not edit only .env.example and expect the running server to change.

If an authentication error appears, log out and log in again so the browser has a real Supabase session.

If a database hostname error appears, check the connection string and DNS/network before changing application code.

If a PostgreSQL schema error appears, compare the current database schema with models.py. create_all() is not a replacement for migrations.

If an upload error appears, check the Supabase Storage bucket name, service credentials, database row, and backend terminal together.

If RAG returns nothing, check that document_chunks actually contain text and embeddings before debugging the LLM.

If Gemini fails, check the API key, model availability, SDK version, quota, and the configured fallback models.

Restart the relevant server after changing environment variables or Python dependencies.

11. Verification Checklist

☐ Backend starts without Python import/configuration errors.

☐ http://localhost:8000/health returns a successful health response.

☐ http://localhost:8000/graphql opens and the GraphQL schema can be inspected.

☐ Angular starts on http://localhost:4200.

☐ Registering a user creates the user in Supabase Auth.

☐ Logging in produces a real Supabase session.

☐ Authenticated GraphQL requests carry the session token.

☐ Supabase PostgreSQL contains documents, document_chunks, chat_sessions and chat_messages tables.

☐ The documents Storage bucket exists.

☐ Uploading a PDF creates a Storage object and a PostgreSQL document record.

☐ Refreshing the browser keeps the uploaded document in the dashboard.

☐ PDF processing creates chunks with page/source information.

☐ document_chunks contains 384-dimensional embeddings.

☐ pgvector similarity search returns relevant chunks for a question.

☐ Chat history is saved in PostgreSQL and survives refresh.

☐ Gemini receives retrieved context and returns an answer based on that context.

☐ Questions outside the document context should use the configured 'not found in the document' behavior rather than inventing an answer.

12. Security Rules I Must Not Forget

Never put secret API keys in Angular source code.

Never commit backend/.env.

Do not expose the Supabase service-role key to the browser.

Keep LLM API keys on the backend.

Validate the authenticated user before accessing private documents.

Filter document retrieval by user ownership.

Validate PDF file type and file size.

Do not trust a document ID supplied by the browser without checking ownership.

Do not expose raw internal stack traces to end users.

If a real secret was ever exposed in a public repository, rotate it rather than simply deleting it from the latest commit.

13. Project Structure I Should Expect

ai-document-assistant/
├── frontend/
│ └── Angular application
├── backend/
│ ├── app/
│ │ ├── main.py
│ │ ├── config.py
│ │ ├── graphql/
│ │ ├── auth/
│ │ ├── database/
│ │ ├── documents/
│ │ ├── embeddings/
│ │ ├── rag/
│ │ └── llm/
│ ├── requirements.txt
│ ├── .env
│ └── .env.example
├── docs/
├── .gitignore
└── README.md

The original architecture also proposed keeping architecture and development documentation under docs/. That is useful for this learning project because the goal is to understand the flow, not just make the application work.

14. What Each Important Backend Folder Does

Folder/file

Responsibility

Simple way to remember it

main.py

Starts FastAPI, middleware, routes and startup tasks.

Entry point / server

config.py

Loads environment configuration.

Settings

graphql/

Queries, mutations and schema.

GraphQL contract

auth/

Validates the current user.

Who is calling?

database/

Connection, SQLAlchemy models and repositories.

Permanent data

documents/

Upload, extraction, chunking and processing.

Understand the PDF

embeddings/

Turns text into vectors.

Meaning → numbers

rag/

Retrieves relevant chunks and prepares context.

Find the right information

llm/

Calls Gemini through an abstraction.

Write the final answer

15. Git / GitHub Recovery Notes

The project previously had a nested Git repository inside frontend. The intended setup is one repository at the project root.

cd D:\ai-document-assistant
rmdir /s /q frontend\.git
git init
git add .
git commit -m "chore: initialize project with frontend and backend foundations"
git remote add origin <your-github-repo-url>
git branch -M main
git push -u origin main

Note: If origin already exists, inspect it with git remote -v before changing it. Do not paste credentials or tokens into commands that may be stored in shell history.

16. Useful Verification Commands

# Check Git repository

git status
git remote -v
git log --oneline -5

# Backend environment

python --version
pip --version

# Frontend

node --version
npm --version

# Backend health

# Open in browser:

http://localhost:8000/health

# GraphQL

# Open in browser:

http://localhost:8000/graphql

17. What the RAG Pipeline Is Actually Doing

RAG is not the same thing as simply sending the entire PDF to Gemini. The project first prepares the document for search. The PDF is extracted into text, text is split into chunks, and each chunk gets a vector embedding. When the user asks a question, the question is embedded using the same model. PostgreSQL/pgvector compares that question vector with stored chunk vectors and returns the closest matches. Only then is the retrieved context sent to Gemini.

Upload:
PDF
↓
Text extraction
↓
Chunks
↓
Embeddings
↓
PostgreSQL + pgvector

Question:
Question
↓
Question embedding
↓
pgvector similarity search
↓
Relevant chunks
↓
Prompt + context
↓
Gemini
↓
Answer

Note: The project notes show successful retrieval of the three most relevant paragraphs for a test question before Gemini was connected. That was the key proof that the RAG retrieval layer was working.

18. What I Learned From the Problems

A frontend mock can make an application look complete even when nothing is persistent yet.

Authentication is not just login UI; the backend must know who the user is and enforce ownership.

GraphQL has its own schema contract. Backend/database fields are not automatically GraphQL fields.

A Storage bucket and a database table solve different problems.

Database schema changes need migrations in serious projects. SQLAlchemy create_all() is useful for initial development, but it is not a full migration system.

Vector search depends on a fixed embedding dimension. Changing the embedding model affects stored vectors.

An LLM is the last part of the RAG pipeline, not the first. Retrieval should work before debugging answer quality.

Environment variables are loaded by the running process. Editing .env normally means restarting the backend.

When a browser still has an old auth session, backend fixes may appear not to work.

For production, secrets, storage policies, database migrations, background workers, rate limits, and observability need stronger treatment than in this learning project.

19. Current State / Final Outcome Recorded in the Notes

The final development log says all ten phases were completed. The final system map records Angular, FastAPI, GraphQL, Supabase Auth, Supabase Storage, PostgreSQL, local SentenceTransformer embeddings, pgvector and Gemini. The final features include light-theme UI, authenticated users, persistent documents, PDF parsing/chunking, semantic search, RAG answers, citations and persisted chat history.

Note: Before changing anything in the future, run the project once and verify the actual current code. The development log is a history of what was done; it should not be treated as a substitute for the current source code.

20. If I Come Back After 1 Month — My Short Restart Routine

Open D:\ai-document-assistant in VS Code.

Check Git status.

Open backend/.env and confirm required local configuration exists. Never paste secrets into this handbook.

Open two terminals.

Backend: cd D:\ai-document-assistant\backend → .\venv\Scripts\activate → python app/main.py

Frontend: cd D:\ai-document-assistant\frontend → npm start

Open /health and /graphql first.

Open the Angular login page and verify Supabase authentication.

Go to the dashboard and verify an existing document is still visible.

Upload a small PDF and wait for PROCESSED.

Check Supabase Storage and the documents/document_chunks tables.

Ask a question that is clearly answered by the PDF.

If the answer fails, debug in this order: auth → database → chunks → embeddings → pgvector retrieval → Gemini.

21. Original Architecture Reference

The original architecture document defined the learning goal as Angular → GraphQL → Strawberry → FastAPI → Supabase → PostgreSQL → RAG → pgvector → LLM → Response and explicitly required incremental development, one phase at a time, with an explanation, files changed, commands, code, run instructions, expected output and a verification checklist before moving forward.

Note: That incremental rule is worth keeping. It was one of the most useful decisions in the project because it made it possible to isolate errors instead of changing the whole application at once.

22. Source Basis and Editing Note

This handbook was assembled from the two project files supplied with the conversation: the original architecture/development prompt and the running development log. I intentionally wrote it as a practical personal developer journal: direct language, short explanations, problem → cause → fix, and repeatable run steps. I did not copy real credentials into this document.

End of handbook — update this file whenever the stack or project flow changes.
