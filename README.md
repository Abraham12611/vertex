# Vertex: AI-Powered DevRel Automation Platform

**Vertex** is a next-generation platform for developer relations (DevRel) teams, startups, and technical communities. It orchestrates multiple AI agents to automate content creation, competitor analysis, community engagement, and technical documentation—empowering teams to scale their DevRel impact with speed, consistency, and insight.

---

## Table of Contents

- [Vertex: AI-Powered DevRel Automation Platform](#vertex-ai-powered-devrel-automation-platform)
	- [Table of Contents](#table-of-contents)
	- [What is Vertex?](#what-is-vertex)
		- [The Problem](#the-problem)
		- [The Solution](#the-solution)
	- [Architecture Overview](#architecture-overview)
	- [Key Integrations](#key-integrations)
		- [Vultr](#vultr)
		- [Groq](#groq)
		- [CrewAI](#crewai)
		- [Coral Protocol](#coral-protocol)
		- [FastAPI](#fastapi)
	- [Other Technologies We Integrated](#other-technologies-we-integrated)
	- [Monorepo Structure](#monorepo-structure)

---

## What is Vertex?

Vertex is an AI-powered DevRel automation platform that enables developer-focused companies to:

- **Automate technical content creation** (blogs, docs, code samples)
- **Perform real-time competitor and SEO analysis**
- **Engage and grow developer communities** (Discord, Slack, GitHub)
- **Generate actionable analytics and content plans**
- **Orchestrate multi-agent workflows** for scalable, consistent DevRel operations

### The Problem

DevRel teams face challenges with manual content creation, inconsistent messaging, limited resources, and the need to scale community engagement and technical documentatio.

### The Solution

Vertex solves these challenges by orchestrating a crew of specialized AI agents (Strategy, Content, Community, Analytics) that work together to automate and optimize DevRel workflows. The platform leverages state-of-the-art LLMs, real-time data integrations, and a modern, developer-centric UI.

---

## Architecture Overview

- **Frontend:** Next.js 14 (React 18, TypeScript, Tailwind CSS) for a beautiful, dark-themed, and responsive UI.
- **Backend:** FastAPI (Python) for high-performance APIs, agent orchestration, and integrations.
- **AI Orchestration:** CrewAI for multi-agent workflows, Groq for LLM inference, Coral Protocol for agent communication.
- **Data & Infra:** Managed PostgreSQL (Vultr), Redis, Celery, Docker, and Nginx for robust, scalable deployment.

---

## Key Integrations

### Vultr

- **Managed PostgreSQL:** All relational data (users, projects, content, analytics) is stored in a managed PostgreSQL instance on Vultr.
  - [Database settings](https://github.com/Abraham12611/vertex/blob/main/apps/api/core/settings.py)
  - [SQLAlchemy/Postgres models](https://github.com/Abraham12611/vertex/blob/main/apps/api/db/models/)
  - [Alembic migrations](https://github.com/Abraham12611/vertex/blob/main/apps/api/db/migration/versions/)
  - [Alembic config](https://github.com/Abraham12611/vertex/blob/main/apps/api/alembic/env.py)
- **Nginx on Vultr:** Used as a reverse proxy for API and web, with health checks and restart policies (see [changelog.md](https://github.com/Abraham12611/vertex/blob/main/changelog.md#L61)).
- **Deployment:** Docker Compose and CI/CD scripts deploy the API, workers, and Nginx to Vultr infrastructure.

### Groq

- **LLM Inference:** Groq's API and SDK are used for all LLM-powered features (content generation, analysis, etc.).
  - [Groq API integration](https://github.com/Abraham12611/vertex/blob/main/apps/api/core/llm.py)
  - [Groq settings](https://github.com/Abraham12611/vertex/blob/main/apps/api/core/settings.py)
  - [Groq usage in agents](https://github.com/Abraham12611/vertex/blob/main/apps/api/agents/strategy_agent.py), [content_agent.py](https://github.com/Abraham12611/vertex/blob/main/apps/api/agents/content_agent.py), [community_agent.py](https://github.com/Abraham12611/vertex/blob/main/apps/api/agents/community_agent.py), [analytics_agent.py](https://github.com/Abraham12611/vertex/blob/main/apps/api/agents/analytics_agent.py)
  - [Groq in CrewAI](https://github.com/Abraham12611/vertex/blob/main/apps/api/agents/crew.py)
- **Use Cases:** Generating blueprints, content plans, technical guides, and real-time analysis.
- **Where Used:** All agent modules, API endpoints for content/blueprint generation, and streaming endpoints.

### CrewAI

- **Multi-Agent Orchestration:** CrewAI is used to define, manage, and execute agent workflows (Strategy, Content, Community, Analytics).
  - [CrewAI integration](https://github.com/Abraham12611/vertex/blob/main/apps/api/agents/crew.py)
  - [Agent definitions](https://github.com/Abraham12611/vertex/blob/main/apps/api/agents/strategy_agent.py), [content_agent.py](https://github.com/Abraham12611/vertex/blob/main/apps/api/agents/content_agent.py), [community_agent.py](https://github.com/Abraham12611/vertex/blob/main/apps/api/agents/community_agent.py), [analytics_agent.py](https://github.com/Abraham12611/vertex/blob/main/apps/api/agents/analytics_agent.py)
  - [Workflow orchestration](https://github.com/Abraham12611/vertex/blob/main/apps/api/flows/devrel_flow.py)
- **Use Cases:** Automated DevRel workflows, content/analysis generation, and agent collaboration.
- **Where Used:** Backend agent orchestration, API endpoints, and demo/test flows.

### Coral Protocol

- **Agent Communication:** Coral Protocol is used for secure, scalable agent-to-agent and agent-to-user communication.
  - [Coral client integration](https://github.com/Abraham12611/vertex/blob/main/apps/api/agents/coral_client.py)
  - [Coral API usage](https://github.com/Abraham12611/vertex/blob/main/apps/api/core/coral.py)
  - [Coral settings](https://github.com/Abraham12611/vertex/blob/main/apps/api/core/settings.py)
- **Use Cases:** Multi-agent coordination, thread management, and message passing.
- **Where Used:** Agent orchestration, backend communication, and future extensibility.

### FastAPI

- **API Framework:** FastAPI powers all backend APIs, providing async endpoints, dependency injection, and OpenAPI docs.
  - [Main FastAPI app](https://github.com/Abraham12611/vertex/blob/main/apps/api/main.py)
  - [API routers](https://github.com/Abraham12611/vertex/blob/main/apps/api/api/v1/routers/)
  - [Dependency management](https://github.com/Abraham12611/vertex/blob/main/apps/api/api/v1/deps.py)
- **Use Cases:** All backend endpoints, agent orchestration, authentication, and streaming.
- **Where Used:** Entire backend, including health checks, content/blueprint APIs, and agent endpoints.

---

## Other Technologies We Integrated

- **Redis:** Real-time updates, background task queue, and WebSocket pub/sub.
  - [Redis settings](https://github.com/Abraham12611/vertex/blob/main/apps/api/core/settings.py)
  - [Redis usage](https://github.com/Abraham12611/vertex/blob/main/apps/api/api/v1/routers/ws.py), [health.py](https://github.com/Abraham12611/vertex/blob/main/apps/api/api/v1/routers/health.py)
- **Celery:** Distributed task queue for background jobs and agent workflows.
  - [Celery worker](https://github.com/Abraham12611/vertex/blob/main/apps/api/worker/celery_worker.py)
  - [Celery integration](https://github.com/Abraham12611/vertex/blob/main/apps/api/core/settings.py)
- **pgvector:** Vector search for semantic memory and embeddings.
  - [pgvector models](https://github.com/Abraham12611/vertex/blob/main/apps/api/db/models/chunk.py), [document.py](https://github.com/Abraham12611/vertex/blob/main/apps/api/db/models/document.py)
  - [pgvector migration](https://github.com/Abraham12611/vertex/blob/main/apps/api/db/migration/versions/timestamp_add_pgvector_and_memory_tables.py)
  - [pgvector tool](https://github.com/Abraham12611/vertex/blob/main/apps/api/agents/pgvector_search_tool.py)
- **Moz API:** SEO and competitor analysis.
  - [Moz API integration](https://github.com/Abraham12611/vertex/blob/main/apps/api/core/moz.py)
  - [Moz tool](https://github.com/Abraham12611/vertex/blob/main/apps/api/agents/moz_insights_tool.py)
- **JWT (jose):** Authentication and access control.
  - [JWT usage](https://github.com/Abraham12611/vertex/blob/main/apps/api/core/secuirity.py), [deps.py](https://github.com/Abraham12611/vertex/blob/main/apps/api/api/v1/deps.py)
- **Pydantic:** Data validation and settings management.
  - [Settings](https://github.com/Abraham12611/vertex/blob/main/apps/api/core/settings.py)
  - [API models](https://github.com/Abraham12611/vertex/blob/main/apps/api/api/v1/routers/)
- **Markdown2, Marked, DOMPurify:** Markdown parsing and safe HTML rendering.
  - [Backend Markdown2](https://github.com/Abraham12611/vertex/blob/main/apps/api/api/v1/routers/content.py)
  - [Frontend Marked/DOMPurify](https://github.com/Abraham12611/vertex/blob/main/apps/web/src/app/blueprints/%5Bid%5D/page.tsx)
- **Numpy:** Embedding and analytics calculations.
  - [Embeddings](https://github.com/Abraham12611/vertex/blob/main/apps/api/core/embeddings.py)
- **Docker & Docker Compose:** Containerized deployment for API, workers, Redis, Postgres, and Nginx.
  - [Dockerfile](https://github.com/Abraham12611/vertex/blob/main/apps/api/Dockerfile)
  - [Docker Compose](https://github.com/Abraham12611/vertex/blob/main/DEMO_SETUP.md)
- **Flower:** Celery monitoring dashboard.
  - [Flower usage](https://github.com/Abraham12611/vertex/blob/main/DEMO_SETUP.md)
- **Next.js, React, TypeScript, Tailwind CSS:** Modern frontend stack for the dashboard and onboarding flows.
  - [Web app](https://github.com/Abraham12611/vertex/blob/main/apps/web/)
- **Framer Motion, React Icons:** Animations and iconography in the frontend.
  - [BlueprintModal](https://github.com/Abraham12611/vertex/blob/main/apps/web/src/components/BlueprintModal.tsx)
- **Zustand:** State management in the frontend.
  - [Project store](https://github.com/Abraham12611/vertex/blob/main/apps/web/src/store/useProjectStore.ts)

---

## Monorepo Structure

- **/apps/api/**: FastAPI backend, agent orchestration, integrations, and database models.
- **/apps/web/**: Next.js frontend, onboarding wizard, dashboard, and blueprint/content plan flows.
- **/landing-page/**: Standalone Vite+React landing page for marketing/demo.
- **/db/**: Database models, migrations, and Alembic scripts.
- **/agents/**: All agent definitions and tools (CrewAI, Groq, Moz, Coral, etc.).
- **/core/**: Core utilities, settings, LLM, embeddings, and protocol clients.
- **/flows/**: Multi-agent workflow orchestration.
- **/worker/**: Celery worker and background task management.
- **/components/**: Shared frontend components (Sidebar, Modals, etc.).

---

**Vertex** is built for developer experience, speed, and extensibility. For more details, see the code links above or open an issue!

