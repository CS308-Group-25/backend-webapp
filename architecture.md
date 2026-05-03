**CS308 Online Store — Architecture Document**

Version 1.0 | Finalized after two external review rounds

**Stack: Next.js · FastAPI · PostgreSQL**

# **1. Architecture Statement**

**Use a modular monolith with domain-oriented modules, layered backend services, OpenAPI-defined contracts, and a frontend-first Next.js app consuming a single FastAPI backend.**

This statement is the north star for every technical decision in the project. When in doubt, ask: does this choice align with the statement above?

# **2. System Overview**

The system has three distinct runtime layers communicating over HTTP/JSON:

```
Browser (User)

↕ HTTP/JSON

Next.js (Frontend — runs in user's browser)

↕ REST API calls to /api/v1/...

FastAPI (Backend — runs on server)

↕ SQL via SQLAlchemy

PostgreSQL (Database — runs on server)
```

Next.js is purely a frontend. It has no business logic, no database access, and no API routes that duplicate backend functionality. All domain logic lives exclusively in FastAPI.

# **3. Repository Structure**

Two repositories in the GitHub organization. One per runtime layer. No monorepo.

```
github.com/your-org/

frontend/ ← Next.js

backend/ ← FastAPI
```

**Why not one repo?**

-   Frontend (npm) and backend (pip) have completely separate dependency systems

-   Pull requests stay focused — no mixing of frontend and backend changes

-   Team members can own a repo without constant cross-layer merge conflicts

-   CI/CD pipelines are simpler per repo

**Branch protection rule (set on day one)**

-   Protect main in both repos

-   Require at least 1 Pull Request review before merging

-   No direct pushes to main by anyone

-   This also ensures the 5 commits per member grading requirement is met cleanly

# **4. Backend Architecture (FastAPI)**

## **4.1 Layered Architecture**

Every feature in the backend goes through exactly three layers in sequence:

```
Router ← HTTP boundary only. No logic. Validates input via Pydantic, calls service.

↓

Service ← All business rules live here. Calls repository for data.

↓

Repository ← All database queries live here. No business logic.
```

This separation is the single most important structural decision. It enables parallel development (6 people can work on different modules without stepping on each other), and it makes unit testing straightforward — the Service layer is tested in isolation with a mocked repository, no database required.

## **4.2 Domain-Based Folder Structure**

Organize by domain module, not by layer type. This prevents 6 people from editing the same folder simultaneously.

```
backend/

modules/

products/

router.py ← FastAPI route definitions only

service.py ← business logic

repository.py ← database queries

schema.py ← Pydantic request/response models

model.py ← SQLAlchemy ORM model

orders/

auth/

users/

cart/

invoices/

discounts/

refunds/

reviews/

wishlist/

categories/

core/

database.py ← DB session setup (get_db dependency)

security.py ← JWT encode/decode, bcrypt hashing

dependencies.py ← shared Depends() functions

alembic/

versions/ ← one migration file per schema change

scripts/

seed.py ← populates DB with demo data

tests/

test_products.py ← pytest unit tests per module

test_orders.py

main.py ← registers all routers

requirements.txt

docker-compose.yml ← local PostgreSQL

.env.example
```

## **4.3 Key Backend Technologies**

**Pydantic**

FastAPI is built on Pydantic. Every request and response shape is defined as a Pydantic class in schema.py. Pydantic validates incoming data automatically and returns a 422 error (not 400 — FastAPI's default) if validation fails. Response schemas also act as a security filter: fields not included in the schema (such as password_hash) are never sent to the client.

**Dependency Injection via Depends()**

FastAPI's built-in DI system. Used for two critical things: injecting the database session into repositories, and injecting the current authenticated user into protected routes. This makes routes testable — in tests, the real database can be swapped for a fake.

**SQLAlchemy ORM**

Database tables are defined as Python classes (models). SQLAlchemy translates method calls into SQL. Default rule: use the ORM. Exception: complex reporting queries (revenue over date ranges, aggregations) may use SQLAlchemy Core or raw SQL when the ORM produces inefficient output — but this must be documented with a comment explaining why.

**Alembic — Migrations**

Every schema change — adding a table, adding a column, changing a type — is captured as an Alembic migration file and committed to git. Every team member runs alembic upgrade head after pulling. This is not optional.

**Critical Migration Rule**

-   One migration per schema change — not one per sprint

-   If you add a column on Tuesday, that is a migration on Tuesday

-   Never batch schema changes to the end of a sprint

-   Batching migrations causes merge conflicts and broken local environments

## **4.4 Authentication & Security**

**JWT + httpOnly Cookies**

When a user logs in, FastAPI creates a signed JWT containing the user ID and role. The JWT is sent to the browser as an httpOnly cookie (not stored in localStorage). httpOnly cookies are inaccessible to JavaScript, making them resistant to XSS attacks. The logout endpoint clears this cookie server-side.

**Bcrypt Password Hashing**

Passwords are never stored as plain text. On registration, the password is hashed with bcrypt (via passlib[bcrypt]). On login, the submitted password is hashed and compared to the stored hash.

**Payment Data — Never Store Full Card Details**

**Security Rule — Payment Data**

-   Never persist full credit card numbers in the database

-   The card number flows into the mock payment function and is immediately discarded

-   Only store: card_last4 (e.g. '4242'), card_brand (e.g. 'Visa'), payment_status, paid_at, amount

-   This satisfies the course requirement for security-aware handling of sensitive information
**Role-Based Access Control (RBAC)**

Three roles: customer, product_manager, sales_manager. A FastAPI dependency require_role(role) is injected into any route that requires a specific role. Any /admin/ route requires a manager role — this is enforced at the dependency level, not inside business logic.

# **5. Frontend Architecture (Next.js)**

## **5.1 Core Rule**

Next.js is a frontend application that consumes FastAPI. It is not a second backend.

-   No API routes duplicating backend logic

-   No database access from Next.js

-   Business logic (orders, payments, stock) lives exclusively in FastAPI

-   Narrow server-side usage (e.g. auth cookie plumbing) is acceptable — becoming a second backend is not

## **5.2 Feature-Based Folder Structure**

Organize by feature, not by file type. This lets 6 people work in parallel with minimal overlap.

```
frontend/

features/

products/

components/ ← ProductCard, ProductGrid, etc.

hooks/ ← useProducts, useProduct, etc.

api.ts ← API calls for this feature

cart/

orders/

auth/

reviews/

wishlist/

admin/

lib/

api-client.ts ← single Axios instance with base URL + auth headers

components/

ui/ ← shared components: Button, Modal, etc.

app/ ← Next.js App Router pages

store/ ← Zustand stores (cart, UI state)
```

## **5.3 Key Frontend Technologies**

**React Query (TanStack Query) — NOT SWR**

All server data fetching goes through React Query. It handles loading states, error states, caching, and automatic refetching. This is especially important for stock counts and order statuses that need to stay current. Decision: React Query only. SWR is not used — pick one library and be consistent.

**Zustand — Client State Only**

Used for UI state that multiple components share but that does not come from the server. Primary use case: shopping cart contents before the user logs in. React Query owns server state. Zustand owns client state. They do not overlap.

**Axios — Centralized API Client**

One Axios instance configured in lib/api-client.ts with the FastAPI base URL. All features import this client. The client automatically attaches the auth cookie and handles base URL configuration. No raw fetch() calls scattered across components.

**Tailwind CSS**

Utility-first CSS framework. Styling is co-located with components via class names. Recommended but not mandatory — the team may substitute another approach if frontend members prefer it.

# **6. Database (PostgreSQL)**

## **6.1 Core Rules**

-   PostgreSQL runs as a Docker container locally — one command spins it up identically on every machine

-   Schema changes go through Alembic — never manual ALTER TABLE

-   Sensitive data rules: passwords are bcrypt hashed, card numbers are never stored

-   ORM is the default for queries; raw SQL is allowed only for complex aggregations with a code comment explaining why

## **6.2 Soft Deletes vs State Machines**

**Critical Distinction**

-   Products → use soft delete (add deleted_at column). Invoices and order history must still reference removed products.

-   Orders → never deleted. Use a status state machine instead.

-   Order states: pending → confirmed → processing → in_transit → delivered

-   Cancellation: pending or confirmed → cancelled

-   Returns: delivered → refund_requested → refunded

-   This is what the course grades when it requires processing / in-transit / delivered status tracking.

## **6.3 Local Development Setup**

Every team member runs PostgreSQL locally via Docker. The backend repo contains a docker-compose.yml. Steps on day one:

-   Clone backend repo

-   Run: docker compose up -d (starts local PostgreSQL)

-   Run: alembic upgrade head (creates all tables)

-   Run: python scripts/seed.py (loads demo data for development)

For the demo environment, one shared PostgreSQL instance is needed. Options: Railway, Render, or Supabase free tier. This decision is deferred until Sprint 3.

# **7. Final Decision Matrix**

  ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  **Pattern / Technology**                               **Decision**              **Rationale**
  ------------------------------------------------------ ------------------------- ---------------------------------------------------------------------------------------
  Layered Architecture (Router / Service / Repository)   ✅ Adopt                  Enables parallel work, clean testability, clear ownership

  Domain-based module folders                            ✅ Adopt                  6 people working in parallel — flat layer folders cause constant collisions

  SQLAlchemy ORM                                         ✅ Adopt                  Readable, type-safe, team-friendly queries

  Alembic Migrations                                     ✅ Adopt                  Schema evolution across sprints without manual SQL coordination

  FastAPI Dependency Injection (Depends)                 ✅ Adopt                  Built-in, zero cost, essential for auth and testing

  JWT in httpOnly Cookie                                 ✅ Adopt                  More secure than localStorage; makes logout endpoint meaningful

  Bcrypt (passlib)                                       ✅ Adopt                  Industry standard for password hashing

  React Query (TanStack Query)                           ✅ Adopt                  Server state management — handles loading, caching, invalidation

  Zustand                                                ✅ Adopt                  Client-side UI state (cart before login, modals)

  Axios + centralized api-client.ts                      ✅ Adopt                  Single place to configure base URL, auth headers

  Soft deletes for Products                              ✅ Adopt                  Invoices must reference products even after removal

  Alembic: one migration per schema change               ✅ Adopt                  Not one per sprint — every change migrated immediately

  Raw SQL for complex reports                            ✅ Allow (with comment)   Revenue aggregations are cleaner in SQL than ORM; document why

  Next.js as pure frontend                               ✅ Adopt                  Business logic lives in FastAPI only

  Order state machine instead of soft delete             ✅ Adopt                  Orders are never deleted; they transition through statuses

  Docker for local PostgreSQL                            ✅ Adopt                  Identical local environments for all 6 team members

  2 GitHub repos (frontend + backend)                    ✅ Adopt                  Clean separation, separate dependency systems, focused PRs

  CQRS                                                   ❌ Reject                 Solves a scale problem you don't have; doubles development effort

  Message queues / Celery / Redis                        ❌ Reject                 Mock payment and email can be synchronous; extra infrastructure for zero benefit

  Redux                                                  ❌ Reject                 React Query handles server state; Zustand handles client state — Redux adds nothing

  Monorepo                                               ❌ Reject                 Requires extra tooling (Turborepo/nx); no benefit at this team size

  SWR                                                    ❌ Reject                 React Query chosen — pick one library and be consistent

  Next.js full-stack (API routes for domain logic)       ❌ Reject                 Creates a second backend; splits domain logic across two runtimes
  ------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# **8. Suggested Team Ownership**

  --------------------------------------------------------------------------------------------
  **Team Member**             **Primary Repo**     **Domain Modules**
  --------------------------- -------------------- -------------------------------------------
  Senior CS student           Backend              auth, core, orders, refunds

  Senior (FastAPI exposure)   Backend              products, categories, discounts

  Senior CS student           Backend              invoices, revenue reports, cart

  Senior CS student           Frontend             product pages, cart UI, search/filter

  Sophomore/Junior 1          Frontend + Backend   reviews, wishlist, order status UI

  Sophomore/Junior 2          Frontend + Backend   admin panel, delivery views, user profile
  --------------------------------------------------------------------------------------------

# **9. Day One Setup Checklist**

Complete this before any feature development begins.

**GitHub**

-   Create frontend and backend repositories in the GitHub organization

-   Protect main branch in both repos (require 1 PR review, no direct push)

-   Invite all team members with appropriate permissions

**Backend**

-   Initialize FastAPI project with the module folder structure from Section 4.2

-   Set up docker-compose.yml for local PostgreSQL

-   Initialize Alembic

-   Create .env.example with DATABASE_URL, SECRET_KEY, and other config keys

-   Write the first migration (User and Product tables)

-   Confirm alembic upgrade head runs successfully on every team member's machine

**Frontend**

-   Initialize Next.js project with App Router

-   Set up Tailwind CSS

-   Install React Query, Zustand, Axios

-   Create lib/api-client.ts pointing at FastAPI base URL

-   Create the feature folder structure from Section 5.2

**Team Agreement**

-   Everyone reads this document

-   No one pushes business logic to Next.js

-   Every schema change gets a migration immediately

-   Pydantic schemas are written before implementation begins for any endpoint

-   FastAPI /docs is the source of truth for the API contract

*--- End of Architecture Document ---*
