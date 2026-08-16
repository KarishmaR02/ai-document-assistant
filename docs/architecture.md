# Architecture Documentation — AI Document Assistant

This document outlines the architecture, components, and data flow of the AI Document Assistant learning application.

## High-Level Request Flow

```text
  [ Angular UI ] --(GraphQL)--> [ Strawberry GraphQL ] --> [ FastAPI Backend ]
                                                               |
                                     +-------------------------+-------------------------+
                                     |                         |                         |
                                     v                         v                         v
                              [ Supabase Auth ]        [ Supabase Storage ]      [ RAG Pipeline ]
                                                                                         |
                                                                                         v
                                                                                   [ pgvector ]
                                                                                         |
                                                                                         v
                                                                                      [ LLM ]
```

---

## Architecture Components

### 1. Frontend: Angular
* **What is it?** A modern web application framework for building single-page client applications using TypeScript, HTML, and CSS.
* **Why are we using it?** To provide a responsive, highly professional, and component-driven user interface for registering, uploading documents, tracking status, and interacting with the RAG assistant.
* **Where is it used?** Running in the user's browser, handling routing, views, state management, and user input validation.
* **What data flows through it?**
  * Inputs: User credentials, PDF uploads, chat questions.
  * Outputs: Query results, document lists, processing states, and assistant responses.

### 2. GraphQL Layer: Strawberry
* **What is it?** A Python library for creating GraphQL APIs using type hints.
* **Why are we using it?** It allows us to define our API schema naturally using standard Python typing, serving as a type-safe interface between our frontend client and python services.
* **Where is it used?** Inside the FastAPI backend as the main API layer.
* **What data flows through it?** GraphQL Queries and Mutations payload.

### 3. Backend API: FastAPI
* **What is it?** A modern, fast (high-performance), web framework for building APIs with Python.
* **Why are we using it?** It provides high performance, automatic OpenAPI documentation, easy integration with Strawberry, and native support for asynchronous tasks.
* **Where is it used?** Backend server hosting.
* **What data flows through it?** Routes GraphQL requests, manages authentication middleware, handles background tasks for PDF text extraction and embeddings.

### 4. Authentication: Supabase Auth
* **What is it?** Identity management service built on GoTrue.
* **Why are we using it?** To securely register and log in users without having to manually manage hash salts, password resets, and session tokens.
* **Where is it used?** User signup/login requests verify with Supabase Auth; frontend stores the JWT token and includes it in the HTTP headers sent to FastAPI.
* **What data flows through it?** Credentials (username/password) -> JWT (JSON Web Token) containing user metadata.

### 5. Database: Supabase PostgreSQL
* **What is it?** A robust relational database engine.
* **Why are we using it?** To store structured metadata (document names, sizes, processing status, and user associations) as well as the chat sessions and message histories.
* **Where is it used?** Backend service accesses it via an asynchronous connection library.
* **What data flows through it?** SQL queries, application data schemas, inserts and updates for documents and chat logs.

### 6. Storage: Supabase Storage
* **What is it?** A file storage system built on AWS S3.
* **Why are we using it?** To store raw PDF files. Relational databases are not designed for large binary objects.
* **Where is it used?** PDF uploads from FastAPI are piped straight to the Supabase storage bucket.
* **What data flows through it?** Raw PDF binary data.

### 7. Vector Database: pgvector (PostgreSQL extension)
* **What is it?** An extension for PostgreSQL that enables storing and querying vector embeddings.
* **Why are we using it?** To store document chunk embeddings and perform similarity searches directly inside our SQL database.
* **Where is it used?** Runs inside Supabase PostgreSQL.
* **What data flows through it?** Float vectors (e.g., 1536 or 768 dimensions), similarity query results (Cosine / L2 distance).

### 8. Embedding Model
* **What is it?** An ML model that converts text chunks into semantic vector representations.
* **Why are we using it?** To power the retrieval part of RAG by mapping texts with similar meanings close together in vector space.
* **Where is it used?** Triggered in the FastAPI backend when processing new documents and when a user asks a question.
* **What data flows through it?** Text string -> Float vector.

### 9. RAG Pipeline
* **What is it?** Retrieval-Augmented Generation pipeline.
* **Why are we using it?** It extracts, cleans, chunks, retrieves, and optionally reranks context to inject into the LLM context window.
* **Where is it used?** Run asynchronously on backend.
* **What data flows through it?**
  1. PDF text -> Document Chunks.
  2. Query -> pgvector similarity search -> Top K Chunks -> Context String.

### 10. Large Language Model (LLM)
* **What is it?** Generative model that produces text response given a prompt template.
* **Why are we using it?** To synthesize a conversational answer from the retrieved text context.
* **Where is it used?** External API call from backend.
* **What data flows through it?** System instructions + context + user query -> Synthetic text answer.

---

## Detailed Data Flows

### A. Document Upload & Processing Flow
```text
[Angular UI]
     | (Upload PDF)
     v
[FastAPI] ---> Saves file to ---> [Supabase Storage]
     |
     +-------> Inserts Document (Status: UPLOADED) ---> [PostgreSQL]
     |
     +-------> (Background Worker Triggered)
                  |
                  v
             [Text Extraction] (PDF -> String)
                  |
                  v
             [Chunking] (String -> overlapping chunks)
                  |
                  v
             [Embeddings Service] (Chunks -> Vectors)
                  |
                  v
             [pgvector] (Store vectors and metadata)
                  |
                  v
             [PostgreSQL] (Update Document Status: PROCESSED)
```

### B. Chat & QA Flow
```text
[Angular UI]
     | (Ask: "What is the policy on casual leaves?")
     v
[FastAPI]
     |
     +---> 1. Generate Embedding for query string
     |
     +---> 2. Query pgvector for closest chunks (where user_id matches)
     |
     +---> 3. Build Prompt: "Context: [Retrieved Chunks] Question: [Query]"
     |
     +---> 4. Send Prompt to [LLM Service]
     |
     +---> 5. Save Query & Response to [PostgreSQL chat_messages]
     |
     v
[Angular UI] (Display Answer)
```
