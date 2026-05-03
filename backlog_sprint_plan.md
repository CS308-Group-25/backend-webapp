**CS308 Online Store**

**Product Backlog & Sprint Plan**

*Sprints 1–2 detailed | Sprints 3–5 high-level | Progress demo: May 1, 2026*

**6 team members · 5 sprints · 2-week cadence**

# **0. Grading Requirements — Backlog Discipline**

These are hard grade requirements. The backlog structure in this document is designed to satisfy all of them.

  **Requirement**                **Count**       **How satisfied**
  ------------------------------ --------------- -----------------------------------------------------------------------------------------------------
  **Product backlog items**      ≥ 15 per demo   25 user stories in backlog. All created in Jira before Sprint 1 starts.

  **Sprint backlog items**       ≥ 30 per demo   Sprint 1: 47 tasks. Sprint 2: 43 tasks. Sprint 3: 39 tasks. Sprint 4: 37 tasks. Sprint 5: 29 tasks.

  **Unit tests**                 ≥ 25 per demo   Test tasks built into every backend story. Distribution table in Tooling Guide.

  **Commits per member**         ≥ 5 per demo    6 members × 5 commits = 30+ commits. Conventional commits + feature branches.

  **Bug reports**                ≥ 5 per demo    Jira bug template live day one. File bugs as found during development.

  **SCRUM meeting attendance**   Required        Sprint planning, review, retrospective attended by all.

# **1. Sprint Overview**

  **Sprint**     **Focus / Epics**                                    **Dates**          **Demo Gate**
  -------------- ---------------------------------------------------- ------------------ -------------------------
  **Sprint 1**   Setup + Auth + Product listing foundation            Mar 13 – Mar 27   Sprint review

  **Sprint 2**   Cart + Orders + Search/Sort + Invoice + PDF          Mar 27 – Apr 10   Sprint review

  **Sprint 3**   Reviews + Delivery status + Wishlist + Stock mgmt    Apr 10 – Apr 24   Sprint review

  **Sprint 4**   Discounts + Refunds + Admin panel + Demo polish      Apr 24 – May 8    **PROGRESS DEMO May 1**

  **Sprint 5**   Revenue charts + Security + UI polish + Final prep   May 15 – May 22   **FINAL DEMO TBA**

**Progress Demo (May 1) — Must-Have Features**

-   Feature 1: Browse products by category, add to cart

-   Feature 3: Stock shown on product page, order status (processing / in_transit / delivered)

-   Feature 4: Login before checkout, mock payment, invoice shown + PDF emailed

-   Feature 5: Customers can rate and comment; product manager approves/rejects

-   Feature 7: Search by name/description, sort by price/popularity, out-of-stock items searchable but not addable

-   Feature 9: All product fields present: ID, name, model, serial_no, description, stock, price, warranty, distributor

# **2. Product Backlog — All User Stories**

**25 user stories across 9 epics.** All created in Jira before Sprint 1 starts. Priority: Must Have = required for progress or final demo. Should Have = expected at final demo. Could Have = enhancement.

## **Epic: Project Setup**

**US-01 · Initialize project infrastructure** [Setup]

As a **development team**, I want to set up repositories, CI pipelines, local database, and folder structures, so that every team member can start feature development immediately without environment issues.

**Acceptance Criteria:**

-   Both GitHub repos exist with protected main branches and PR requirements

-   docker-compose.yml runs local PostgreSQL with one command on any team member's machine

-   Alembic is initialized and alembic upgrade head succeeds on all machines

-   GitHub Actions CI is green on both repos

-   ruff, ESLint, and Prettier are configured and running in CI

-   .env.example files exist in both repos

> **Priority:** Must Have | **Sprint:** Sprint 1 | **Assignee:** Emir | **Type:** Story
## **Epic: Authentication**

**US-02 · Register a new account** [Auth]

As a **visitor**, I want to register with my name, email, password, address, and tax ID, so that I can place orders and access my purchase history.

**Acceptance Criteria:**

-   POST /api/v1/auth/register creates a new user and returns 201

-   Password is hashed with bcrypt — plain text never stored

-   Duplicate email returns 400 with a clear error message

-   Registration page is accessible and submits correctly

-   3 unit tests cover happy path, duplicate email, and weak password

> **Priority:** Must Have | **Sprint:** Sprint 1 | **Assignee:** Emir | **Type:** Story
**US-03 · Log in and log out** [Auth]

As a **registered user**, I want to log in with my email and password and log out when I am done, so that my session is secure and my data is protected.

**Acceptance Criteria:**

-   POST /api/v1/auth/login sets an httpOnly JWT cookie on success

-   Wrong credentials return 401

-   GET /api/v1/auth/me returns the current user's data

-   POST /api/v1/auth/logout clears the cookie

-   Frontend redirects to login page for protected routes when not authenticated

-   3 unit tests cover login, logout, and wrong password

> **Priority:** Must Have | **Sprint:** Sprint 1 | **Assignee:** Emir | **Type:** Story
## **Epic: Products**

**US-04 · Browse products and view product details** [Products]

As a **visitor**, I want to browse supplements by category and view full details for any product, so that I can find what I am looking for and make an informed purchase decision.

**Acceptance Criteria:**

-   GET /api/v1/products returns a paginated product list

-   GET /api/v1/products/{id} returns all course-required fields: id, name, model, serial_no, description, stock, price, warranty, distributor

-   Product detail page also shows supplement-specific fields: brand, flavor, form (powder/capsule/tablet), serving_size, goal_tags (e.g. muscle gain, recovery, endurance)

-   Current stock count is displayed on the product detail page

-   Out-of-stock products are displayed but the add-to-cart button is disabled

-   Products are browsable without logging in

-   Average rating is visible on the product listing card and detail page

> **Priority:** Must Have | **Sprint:** Sprint 1 | **Assignee:** Senior BE | **Type:** Story
**US-05 · Search, sort, and filter products** [Products]

As a **visitor**, I want to search products by name or description and sort or filter by price, popularity, brand, or category, so that I can quickly find specific supplements without browsing the full catalog.

**Acceptance Criteria:**

-   GET /api/v1/products?search= performs case-insensitive match on name and description

| -   GET /api/v1/products?sort=price_asc|price_desc|popularity_desc works correctly                                                                                                                               |

-   GET /api/v1/products?category= filters by category ID

-   GET /api/v1/products?brand= filters by brand name

-   Out-of-stock items appear in search results but cannot be added to cart

-   Search bar, sort dropdown, category filter, and brand filter are visible and functional

-   4 unit tests: search match, empty results, sort ordering, out-of-stock inclusion in results

> **Priority:** Must Have | **Sprint:** Sprint 2 | **Assignee:** Senior BE | **Type:** Story
**US-06A · Manage products and stock levels** [Products]

As a **product manager**, I want to add, edit, and remove products and update stock quantities, so that the store catalog and inventory stay accurate at all times.

**Acceptance Criteria:**

-   POST /api/v1/admin/products creates a product record with catalog fields (name, model, serial_no, description, stock, warranty, distributor, brand, flavor, form, serving_size, goal_tags, category_id) — price is not set here; it is set by the sales manager after product creation (201)

-   PATCH /api/v1/admin/products/{id} updates catalog and descriptive fields (name, model, serial_no, description, stock, warranty, distributor, brand, flavor, form, serving_size, goal_tags) — price and discount fields are not editable here; pricing authority belongs to the sales manager

-   DELETE /api/v1/admin/products/{id} soft-deletes the product (sets deleted_at)

-   Deleted products no longer appear in the public product listing

-   Product manager can update stock quantity directly from the admin panel

-   Admin product management page is accessible only to product managers

-   3 unit tests: create product, soft delete sets deleted_at, deleted product excluded from public listing

> **Priority:** Must Have | **Sprint:** Sprint 2 | **Assignee:** Senior BE | **Type:** Story
**US-06B · Manage product categories** [Products]

As a **product manager**, I want to add, edit, and remove product categories, so that the supplement catalog stays organized and categories reflect the current product range.

**Acceptance Criteria:**

-   POST /api/v1/admin/categories creates a new category (201)

-   PATCH /api/v1/admin/categories/{id} updates category name or description

-   DELETE /api/v1/admin/categories/{id} returns 400 if products are still assigned to that category

-   GET /api/v1/categories is publicly accessible and returns the full category list

-   Admin category management page is accessible only to product managers

> **Priority:** Must Have | **Sprint:** Sprint 2 | **Assignee:** Senior BE | **Type:** Story
## **Epic: Cart**

**US-07 · Add products to cart without logging in** [Cart]

As a **visitor**, I want to add products to a shopping cart before logging in, so that I can browse and plan my purchase without needing an account.

**Acceptance Criteria:**

-   Guest cart is stored in Zustand on the frontend (client-side only)

-   Products can be added, updated in quantity, and removed from the guest cart

-   On login, the guest cart is merged into the server-side cart automatically

-   Out-of-stock products cannot be added to cart (button disabled)

-   Cart item count is visible in the navigation bar

> **Priority:** Must Have | **Sprint:** Sprint 2 | **Assignee:** Deniz | **Type:** Story
**US-08 · Manage authenticated cart and proceed to checkout** [Cart]

As a **customer**, I want to view and manage my cart as a logged-in user and proceed to checkout, so that I can review and adjust my selections before placing an order.

**Acceptance Criteria:**

-   GET /api/v1/cart returns cart contents with item totals

-   PATCH /api/v1/cart/items/{product_id} updates quantity correctly

-   DELETE /api/v1/cart/items/{product_id} removes item

-   Cart page shows product names, quantities, unit prices, and total

-   Proceed to checkout button is accessible from cart page

> **Priority:** Must Have | **Sprint:** Sprint 2 | **Assignee:** Deniz | **Type:** Story
## **Epic: Orders**

**US-09 · Place an order with mock payment** [Orders]

As a **customer**, I want to enter my delivery address and credit card details to place an order, so that I can purchase products and receive a confirmation with invoice.

**Acceptance Criteria:**

-   POST /api/v1/orders accepts delivery_address, card number (transient), card_last4, card_brand

-   Mock payment function is called synchronously and returns success

-   Stock is decremented for each ordered item on order placement

-   Invoice is generated and returned in the response (invoice_id)

-   Invoice PDF is sent to the customer's registered email

-   Full card number is never persisted — only card_last4 and card_brand are stored

-   Order confirmation page shows order summary and invoice link

-   4 unit tests cover successful order, out-of-stock rejection, payment mock, and stock decrement

> **Priority:** Must Have | **Sprint:** Sprint 2 | **Assignee:** Emir | **Type:** Story
**US-10 · Track and cancel orders** [Orders]

As a **customer**, I want to view my order history and track the status of each order, so that I know where my order is and can cancel it if needed.

**Acceptance Criteria:**

-   GET /api/v1/orders returns the customer's own orders

-   GET /api/v1/orders/{id} returns order detail with current status

-   Order status values are displayed clearly: pending, confirmed, processing, in_transit, delivered

-   PATCH /api/v1/orders/{id} with status: cancelled works if order is pending or confirmed

-   Cancellation returns 400 if the order is already processing or later

-   Order history page is accessible from the customer's account section

> **Priority:** Must Have | **Sprint:** Sprint 3 | **Assignee:** Emir | **Type:** Story
**US-11A · View delivery queue** [Orders]

As a **product manager**, I want to see a delivery list with all required fields for each pending order, so that deliveries can be tracked and managed systematically.

**Acceptance Criteria:**

-   GET /api/v1/admin/orders?status=processing returns orders ready for delivery

-   Each order in the response includes: delivery_id (order_id), customer_id, product_id, quantity, total_price, delivery_address, completed flag (derived from status = delivered)

-   Product manager can open the invoice/order summary associated with any delivery row

-   Delivery queue page is accessible only to product managers

-   Page shows customer name and contact details alongside delivery address

-   Orders can be filtered by status: processing, in_transit, delivered

> **Priority:** Must Have | **Sprint:** Sprint 3 | **Assignee:** Senior 4 | **Type:** Story
**US-11B · Update delivery status** [Orders]

As a **product manager**, I want to update the delivery status of an order through the processing, in-transit, and delivered states, so that customers are informed about their delivery progress and the delivery queue stays current.

**Acceptance Criteria:**

| -   PATCH /api/v1/admin/orders/{id} accepts status: processing | in_transit | delivered                                                                                                                                               |

-   Invalid transitions (e.g. delivered → processing) return 400

-   Status change is immediately reflected in the customer's order tracking view

-   Admin delivery page shows the current status of every order with a change action

-   2 unit tests: valid status transition, invalid transition returns 400

> **Priority:** Must Have | **Sprint:** Sprint 3 | **Assignee:** Senior 4 | **Type:** Story
## **Epic: Invoices**

**US-12 · Receive and access invoice after purchase** [Invoices]

As a **customer**, I want to receive an invoice PDF by email after placing an order and access it later, so that I have a record of my purchase for accounting purposes.

**Acceptance Criteria:**

-   Invoice PDF is generated automatically on order placement

-   PDF is emailed to the customer's registered email address

-   GET /api/v1/orders/{id}/invoice returns the invoice object

-   Invoice shows: order ID, customer name, product list, quantities, prices, total, date

-   Customer cannot access another customer's invoice (403)

> **Priority:** Must Have | **Sprint:** Sprint 2 | **Assignee:** Senior BE | **Type:** Story
**US-13 · View and export invoices as sales manager** [Invoices]

As a **sales manager**, I want to view all invoices filtered by date range and export them as PDF, so that I can track sales and generate reports for any time period.

**Acceptance Criteria:**

-   GET /api/v1/admin/invoices?from=&to= returns paginated invoice list

-   GET /api/v1/admin/invoices/{id}/pdf returns the PDF file for download

-   Invoice list shows: invoice ID, customer, total, date

-   Date range filter works correctly

-   Admin invoices page is accessible only to sales managers

> **Priority:** Must Have | **Sprint:** Sprint 4 | **Assignee:** Senior BE | **Type:** Story
## **Epic: Reviews**

**US-14 · Rate and comment on products** [Reviews]

As a **customer**, I want to submit a 1–5 star rating and optional comment for a product I have purchased, so that other customers can benefit from my experience and find quality supplements.

**Acceptance Criteria:**

-   POST /api/v1/products/{id}/reviews accepts rating (1–5) and optional comment

-   Review status defaults to pending — not publicly visible until approved by product manager

-   GET /api/v1/products/{id}/reviews returns only approved reviews

-   Average rating (out of 5) is shown on the product listing card and detail page

-   3 unit tests: submission accepted, pending default status, only approved reviews returned publicly

> **Priority:** Must Have | **Sprint:** Sprint 3 | **Assignee:** Junior 1 | **Type:** Story
**US-15 · Moderate product reviews** [Reviews]

As a **product manager**, I want to approve or reject customer comments before they become publicly visible, so that only appropriate content appears on the store.

**Acceptance Criteria:**

| -   PATCH /api/v1/admin/reviews/{id} with approval_status: approved | rejected works                                                                               |

-   Approved reviews become immediately visible on the product page

-   Rejected reviews remain hidden from public view

-   DELETE /api/v1/admin/reviews/{id} permanently removes a review

-   Admin review moderation page lists all pending reviews

-   2 unit tests cover approve and reject behaviour

> **Priority:** Must Have | **Sprint:** Sprint 3 | **Assignee:** Junior 1 | **Type:** Story
## **Epic: Wishlist & Discounts**

**US-16 · Maintain a product wishlist and receive discount alerts** [Wishlist]

As a **customer**, I want to save products to a wishlist and be notified when a wishlisted product goes on sale, so that I never miss a discount on something I want to buy.

**Acceptance Criteria:**

-   GET /api/v1/wishlist/items returns the customer's wishlist

-   POST /api/v1/wishlist/items adds a product to the wishlist

-   DELETE /api/v1/wishlist/items/{product_id} removes a product

-   When a sales manager applies a discount, an email notification is sent to all customers who have that product wishlisted

-   Wishlist page shows current price and active discount badge if applicable

> **Priority:** Must Have | **Sprint:** Sprint 3 | **Assignee:** Junior 2 | **Type:** Story
**US-17 · Set and remove product discounts** [Discounts]

As a **sales manager**, I want to set the initial price for new products, apply discount rates to selected products, and remove discounts when campaigns end, so that I have full control over product pricing and can run targeted promotional campaigns.

**Acceptance Criteria:**

-   PATCH /api/v1/admin/products/{id}/price sets the base price for a product — only accessible to sales managers

-   POST /api/v1/admin/discounts applies discount_rate to product_ids list

-   System recalculates and updates product prices automatically

-   Wishlist notification emails are sent automatically on discount creation

-   DELETE /api/v1/admin/discounts/{id} restores original prices

-   Admin discount management page is accessible only to sales managers

-   3 unit tests cover price recalculation, notification trigger, and price restoration

> **Priority:** Must Have | **Sprint:** Sprint 4 | **Assignee:** Senior BE | **Type:** Story
## **Epic: Refunds**

**US-18 · Request a refund for a purchased item** [Refunds]

As a **customer**, I want to request a refund for a specific item within 30 days of purchase, so that I can return products that did not meet my expectations.

**Acceptance Criteria:**

-   POST /api/v1/orders/{order_id}/items/{item_id}/refund-requests creates a refund request (201)

-   Refund can only be requested for items whose order status is delivered — not for items still in processing or in_transit

-   The 30-day eligibility window is calculated from the purchase date (order created_at), not from the delivery date — these are tracked independently

-   Request returns 400 if submitted more than 30 days after the purchase date

-   Refund request states: requested → approved_waiting_return → returned_received → refunded

-   Sales manager marks returned_received when the physical item arrives back at the store

-   Refund amount is the original item purchase price including any discount active at time of purchase

-   Customer can track refund request status in their order history

-   4 unit tests: 30-day boundary, discount-inclusive amount, state transition, duplicate request prevention

> **Priority:** Must Have | **Sprint:** Sprint 4 | **Assignee:** Emir | **Type:** Story
**US-19 · Evaluate and process refund requests** [Refunds]

As a **sales manager**, I want to review pending refund requests, approve them, mark returned items as received, and authorize refunds, so that legitimate returns are processed correctly and stock is restored only after physical return is confirmed.

**Acceptance Criteria:**

-   GET /api/v1/admin/refund-requests returns all requests filterable by status

-   PATCH /api/v1/admin/refund-requests/{id} supports transitions: requested → approved_waiting_return, approved_waiting_return → returned_received, returned_received → refunded

-   PATCH /api/v1/admin/refund-requests/{id} with status: rejected closes the request at any state

-   On refunded: item quantity is restored to product stock

-   On refunded: refund amount is credited back to the customer's account record

-   Admin refunds page shows: customer name, product, order date, refund amount, reason, current state

> **Priority:** Must Have | **Sprint:** Sprint 4 | **Assignee:** Senior 4 | **Type:** Story
## **Epic: Reports**

**US-20 · View revenue and profit chart** [Reports]

As a **sales manager**, I want to view a chart of revenue and profit/loss for any given date range, so that I can monitor business performance and make pricing decisions.

**Acceptance Criteria:**

-   GET /api/v1/admin/reports/revenue?from=&to= returns revenue, cost, profit, and chart_data array

-   Chart renders in the admin panel with clearly labelled axes

-   Date range picker is available on the reports page

-   Data correctly accounts for refunded orders (refunded amount excluded from revenue)

> **Priority:** Should Have | **Sprint:** Sprint 5 | **Assignee:** Senior BE | **Type:** Story
## **Epic: Security**

**US-21 · Enforce base security and role boundaries from day one** [Security]

As a **system**, I want to have base security measures in place from the first sprint, so that sensitive data is protected and role boundaries are enforced throughout development, not as an afterthought.

**Acceptance Criteria:**

-   Passwords stored as bcrypt hashes — plain text never appears in database or logs

-   Credit card numbers never persisted — only card_last4 and card_brand stored

-   All /admin/ routes return 403 for non-manager users (require_admin dependency)

-   Customers cannot access other customers' orders, invoices, or cart (403)

-   JWT tokens are signed with SECRET_KEY from environment variable — never hardcoded

-   Base security tasks T-017b and T-017c added to Sprint 1 task list

> **Priority:** Must Have | **Sprint:** Sprint 1 | **Assignee:** Emir | **Type:** Story
**US-22 · Security hardening, token expiry, and production hygiene** [Security]

As a **system**, I want to apply production-grade security settings before final demo, so that the application meets the course's explicit requirement for security-aware development.

**Acceptance Criteria:**

-   JWT tokens have a defined expiry (e.g. 24 hours) and are invalidated on logout

-   HTTPS enforced in production deployment

-   Sensitive fields excluded from all API responses via Pydantic response_model

-   Input sanitized — no raw user strings interpolated into SQL queries

-   Environment secrets never committed to git — CI uses GitHub Secrets

> **Priority:** Must Have | **Sprint:** Sprint 5 | **Assignee:** Emir | **Type:** Story
## **Epic: Concurrency & Data Consistency**

**US-23 · Prevent race conditions in stock management and order placement** [Concurrency]

As a **system**, I want to handle multiple simultaneous checkouts correctly without overselling stock, so that the application remains correct under concurrent usage as required by the course brief.

**Acceptance Criteria:**

-   Order placement uses a database transaction with SELECT FOR UPDATE on the product stock row

-   If two simultaneous checkouts compete for the last item in stock, exactly one succeeds and the other receives a 409 or 400 response

-   Stock decrement and order creation are atomic — no partial state if the transaction fails

-   Cart quantity validation re-checks stock at order placement time, not only at add-to-cart time

-   3 unit tests cover: concurrent stock decrement, oversell prevention, transaction rollback on payment failure

> **Priority:** Must Have | **Sprint:** Sprint 3 | **Assignee:** Emir | **Type:** Story
# **3. Sprint 1 — Detailed Task Breakdown**

**Dates:** March 13 – March 27, 2026 | Days remaining: \~9 | **Stories: US-01, US-02, US-03, US-04**

**Sprint 1 Goal**

-   Every team member has a working local environment and can run the app.

-   A visitor can open the frontend, see a product listing, and view product details.

-   A user can register and log in.

-   CI is green. Main is protected. Jira is populated.

**US-01 — Project Infrastructure**

  **ID**       **Task Description**                                                                               **Assignee**   **Type**   **Est (h)**   **Layer**
  ------------ -------------------------------------------------------------------------------------------------- -------------- ---------- ------------- -----------
  **T-001**    Create frontend and backend GitHub repos in org, set branch protection rules                       Senior 4       **CI**     1             GitHub

  **T-002**    Initialize FastAPI project with domain module folder structure (Section 4.2 of Architecture doc)   Emir           **BE**     2             Backend

  **T-003**    Create docker-compose.yml with PostgreSQL 15 service                                               Senior 4       **DB**     1             Backend

  **T-004**    Initialize Alembic, confirm alembic upgrade head runs on all team machines                         Senior 4       **DB**     2             Backend

  **T-005**    Create backend .env.example with all required keys                                                 Senior 4       **BE**     0.5           Backend

  **T-006**    Configure ruff in pyproject.toml                                                                   Senior 4       **CI**     0.5           Backend

  **T-007**    Set up pytest folder structure and conftest.py with base fixtures                                  Emir           **TEST**   1             Backend

  **T-008**    Create GitHub Actions backend CI workflow (lint + tests, no DB)                                    Senior 4       **CI**     2             GitHub

  **T-009**    Initialize Next.js project with App Router and TypeScript                                          Deniz          **FE**     1             Frontend

  **T-010**    Configure Tailwind CSS, ESLint, and Prettier                                                       Deniz          **FE**     1             Frontend

  **T-011**    Install React Query, Zustand, and Axios; create lib/api-client.ts                                  Deniz          **FE**     1             Frontend

  **T-012**    Create feature folder structure (products, auth, cart, orders, admin)                              Deniz          **FE**     1             Frontend

  **T-013**    Create frontend .env.example with NEXT_PUBLIC_API_URL                                              Deniz          **FE**     0.5           Frontend

  **T-014**    Create GitHub Actions frontend CI workflow (lint + build)                                          Senior 4       **CI**     1.5           GitHub

  **T-015**    Create Jira project: set issue types, bug template, story template, sprint board                   Emir           **CI**     1.5           Jira

  **T-016**    Create all 25 user stories in Jira product backlog with acceptance criteria                        Emir           **CI**     2             Jira

  **T-017**    Create seed.py with 3 categories and 10 sample products                                            Junior 2       **BE**     1.5           Backend

  **T-017b**   Verify bcrypt hashing is wired into registration (never store plain text passwords)                Emir           **TEST**   0.5           Backend

  **T-017c**   Verify /admin/ routes return 403 for non-manager users — write 2 smoke tests                     Emir           **TEST**   1             Backend

**US-02 — Register**

  **ID**      **Task Description**                                                                   **Assignee**   **Type**   **Est (h)**   **Layer**
  ----------- -------------------------------------------------------------------------------------- -------------- ---------- ------------- -----------
  **T-018**   Create User SQLAlchemy model with all required fields; generate Alembic migration      Emir           **DB**     1.5           Backend

  **T-019**   Create UserRepository with get_by_email and create_user methods                        Emir           **BE**     1             Backend

  **T-020**   Create AuthService.register() with bcrypt hashing and duplicate email check            Emir           **BE**     1.5           Backend

  **T-021**   Create Pydantic RegisterRequest and UserPublicResponse schemas                         Emir           **BE**     0.5           Backend

  **T-022**   Create POST /api/v1/auth/register router endpoint                                      Emir           **BE**     0.5           Backend

  **T-023**   Write 3 unit tests: happy path, duplicate email (400), missing required fields (422)   Emir           **TEST**   1.5           Backend

  **T-024**   Create registration page with form (name, email, password, address, tax_id)            Deniz          **FE**     2             Frontend

  **T-025**   Connect registration form to POST /api/v1/auth/register via api-client.ts              Deniz          **FE**     1             Frontend

**US-03 — Login + Logout**

  **ID**      **Task Description**                                                                 **Assignee**   **Type**   **Est (h)**   **Layer**
  ----------- ------------------------------------------------------------------------------------ -------------- ---------- ------------- -----------
  **T-026**   Create JWT encode/decode functions in core/security.py                               Emir           **BE**     1.5           Backend

  **T-027**   Create get_current_user, require_admin Depends() functions in core/dependencies.py   Emir           **BE**     1.5           Backend

  **T-028**   Create AuthService.login() and POST /api/v1/auth/login (sets httpOnly cookie)        Emir           **BE**     1             Backend

  **T-029**   Create POST /api/v1/auth/logout (clears cookie) and GET /api/v1/auth/me              Emir           **BE**     0.5           Backend

  **T-030**   Write 3 unit tests: login success, wrong password (401), token cookie set            Emir           **TEST**   1             Backend

  **T-031**   Create login page with email + password form                                         Deniz          **FE**     1.5           Frontend

  **T-032**   Implement auth state in Zustand; redirect to login for protected routes              Deniz          **FE**     2             Frontend

**US-04 — Product Listing & Detail**

  **ID**      **Task Description**                                                                                                                                                              **Assignee**   **Type**   **Est (h)**   **Layer**
  ----------- --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- -------------- ---------- ------------- -----------
  **T-033**   Create Category and Product SQLAlchemy models with all course-required fields plus supplement fields (brand, flavor, form, serving_size, goal_tags); generate Alembic migration   Senior BE      **DB**     2.5           Backend

  **T-034**   Create ProductRepository with get_all (basic, no search yet) and get_by_id                                                                                                        Senior BE      **BE**     1             Backend

  **T-035**   Create ProductService.list_products() and get_product()                                                                                                                           Senior BE      **BE**     1             Backend

  **T-036**   Create GET /api/v1/products and GET /api/v1/products/{id} endpoints + schemas                                                                                                     Senior BE      **BE**     1             Backend

  **T-037**   Create GET /api/v1/categories endpoint                                                                                                                                            Senior BE      **BE**     0.5           Backend

  **T-038**   Write 2 unit tests: list returns all products, get_by_id returns correct product                                                                                                  Senior BE      **TEST**   1             Backend

  **T-039**   Create product listing page with ProductCard components (name, price, stock badge)                                                                                                Deniz          **FE**     2.5           Frontend

  **T-040**   Create product detail page with all required fields and stock count                                                                                                               Deniz          **FE**     2             Frontend

  **T-041**   Create category navigation sidebar/tabs on product listing page                                                                                                                   Junior 2       **FE**     1.5           Frontend

**US-21A — Base Security & Role Boundaries**

  **ID**       **Task Description**                                                                                                    **Assignee**   **Type**   **Est (h)**   **Layer**
  ------------ ----------------------------------------------------------------------------------------------------------------------- -------------- ---------- ------------- -----------
  **T-042**    Verify passlib[bcrypt] is installed and wired into AuthService.register() — confirm hash stored, never plain text   Junior 1       **TEST**   0.5           Backend

  **T-046**    Confirm SECRET_KEY is loaded from environment variable in core/security.py — never hardcoded                          Emir           **BE**     0.5           Backend

  **T-047a**   Write smoke test: /admin/ route with customer token returns 403 (can run without order/cart/invoice existing)           Junior 1       **TEST**   0.5           Backend

  **T-048**    Confirm card_number is not present in any SQLAlchemy model or Pydantic response schema                                  Senior BE      **TEST**   0.5           Backend

**Sprint 1 — Acceptance checklist before review on March 27**

-   docker compose up -d + alembic upgrade head works on all 6 machines

-   GitHub Actions is green on both repos

-   A visitor can open the frontend and see the product listing with seeded data

-   A visitor can click a product and see its detail page with stock count

-   A visitor can register a new account

-   A registered user can log in and the auth/me endpoint returns their data

-   All 25 Jira stories exist in the product backlog

-   At least 9 unit tests passing (T-023, T-030, T-038 sets)

# **4. Sprint 2 — Detailed Task Breakdown**

**Dates:** March 27 – April 10, 2026 | **Stories: US-05, US-06, US-07, US-08, US-09, US-12**

**Sprint 2 Goal**

-   A customer can search and sort products, add them to cart, and place a complete order.

-   Mock payment runs, stock decrements, invoice PDF is generated and emailed.

-   A product manager can add new products via the admin interface.

-   Search, sort, and category filter are all working on the frontend.

**US-05 — Search, Sort & Filter**

  **ID**      **Task Description**                                                                        **Assignee**   **Type**   **Est (h)**   **Layer**
  ----------- ------------------------------------------------------------------------------------------- -------------- ---------- ------------- -----------
  **T-101**   Extend ProductRepository to support search (ILIKE on name + description)                    Senior BE      **BE**     1.5           Backend

  **T-102**   Extend ProductRepository to support sort (price_asc, price_desc, popularity_desc, newest)   Senior BE      **BE**     1             Backend

  **T-103**   Add category filter and pagination (page, page_size) to GET /api/v1/products                Senior BE      **BE**     1             Backend

  **T-104**   Write 4 unit tests: search match, empty results, sort order, out-of-stock inclusion         Senior BE      **TEST**   1.5           Backend

  **T-105**   Add search bar component to product listing page                                            Deniz          **FE**     1.5           Frontend

  **T-106**   Add sort dropdown and category filter to product listing page                               Deniz          **FE**     1.5           Frontend

  **T-107**   Disable add-to-cart button for out-of-stock products; show out-of-stock badge               Deniz          **FE**     1             Frontend

**US-06A — Manage Products & Stock Levels**

  **ID**      **Task Description**                                                                                     **Assignee**   **Type**   **Est (h)**   **Layer**
  ----------- -------------------------------------------------------------------------------------------------------- -------------- ---------- ------------- -----------
  **T-108**   Create POST /api/v1/admin/products endpoint with all required fields                                     Senior BE      **BE**     1             Backend

  **T-109**   Create PATCH /api/v1/admin/products/{id} and DELETE (soft delete) endpoints                              Senior BE      **BE**     1             Backend

  **T-111**   Write 3 unit tests: create product, soft delete sets deleted_at, deleted product excluded from listing   Senior BE      **TEST**   1             Backend

  **T-112**   Create admin product management page (add/edit/delete product form)                                      Junior 2       **FE**     3             Frontend

**US-06B — Manage Product Categories**

  **ID**      **Task Description**                                                            **Assignee**   **Type**   **Est (h)**   **Layer**
  ----------- ------------------------------------------------------------------------------- -------------- ---------- ------------- -----------
  **T-110**   Create category admin endpoints: POST, PATCH, DELETE /api/v1/admin/categories   Senior BE      **BE**     1             Backend

  **T-113**   Create admin category management page                                           Junior 2       **FE**     2             Frontend

**US-07 — Add Products to Cart Without Logging In**

  **ID**       **Task Description**                                                                         **Assignee**   **Type**   **Est (h)**   **Layer**
  ------------ -------------------------------------------------------------------------------------------- -------------- ---------- ------------- -----------
  **T-119**    Create Zustand cart store for guest cart state (add, update, remove, clear)                  Deniz          **FE**     2             Frontend

  **T-121**    Add add-to-cart button on product listing and detail pages                                   Deniz          **FE**     1             Frontend

  **T-122**    Implement guest cart merge into server cart on login                                         Deniz          **FE**     2             Frontend

  **T-123**    Add cart item count badge to navigation bar                                                  Deniz          **FE**     0.5           Frontend

  **T-124b**   Block add-to-cart for out-of-stock products on the frontend (button disabled, badge shown)   Deniz          **FE**     0.5           Frontend

**US-08 — Manage Authenticated Cart and Proceed to Checkout**

  **ID**      **Task Description**                                                         **Assignee**   **Type**   **Est (h)**   **Layer**
  ----------- ---------------------------------------------------------------------------- -------------- ---------- ------------- -----------
  **T-114**   Create Cart and CartItem SQLAlchemy models; generate Alembic migration       Senior 4       **DB**     1.5           Backend

  **T-115**   Create CartRepository with get, add_item, update_item, remove_item methods   Senior 4       **BE**     1.5           Backend

  **T-116**   Create CartService with stock check on add (400 if out of stock)             Senior 4       **BE**     1.5           Backend

  **T-117**   Create cart endpoints: GET, POST, PATCH, DELETE /api/v1/cart/items           Senior 4       **BE**     1             Backend

  **T-118**   Write 3 unit tests: add to cart, out-of-stock rejection (400), remove item   Senior 4       **TEST**   1             Backend

  **T-120**   Create cart page showing items, quantities, unit prices, and totals          Deniz          **FE**     2             Frontend

**US-09 — Order Placement with Mock Payment**

  **ID**      **Task Description**                                                                                                  **Assignee**   **Type**   **Est (h)**   **Layer**
  ----------- --------------------------------------------------------------------------------------------------------------------- -------------- ---------- ------------- -----------
  **T-124**   Create Order, OrderItem, and Payment SQLAlchemy models; generate migration                                            Emir           **DB**     2             Backend

  **T-125**   Create mock payment function in core/payment.py (always returns success)                                              Emir           **BE**     0.5           Backend

  **T-126**   Create OrderService.place_order(): validate stock, call mock payment, decrement stock, create order                   Emir           **BE**     3             Backend

  **T-127**   Create POST /api/v1/orders endpoint and response schemas                                                              Emir           **BE**     1             Backend

  **T-128**   Create GET /api/v1/orders and GET /api/v1/orders/{id} endpoints                                                       Emir           **BE**     0.5           Backend

  **T-129**   Write 4 unit tests: successful order, out-of-stock rejection, stock decrements correctly, card number not persisted   Junior 1       **TEST**   2             Backend

  **T-130**   Create checkout page with delivery address and card input form                                                        Junior 1       **FE**     2.5           Frontend

  **T-131**   Create order confirmation page showing order summary and invoice link                                                 Junior 1       **FE**     1.5           Frontend

  **T-132**   Create order history page listing customer's past orders with status badges                                          Junior 1       **FE**     2             Frontend

**US-12 — Invoice Generation & Email**

  **ID**      **Task Description**                                                            **Assignee**   **Type**   **Est (h)**   **Layer**
  ----------- ------------------------------------------------------------------------------- -------------- ---------- ------------- -----------
  **T-133**   Create Invoice SQLAlchemy model; generate migration                             Senior BE      **DB**     1             Backend

  **T-134**   Create InvoiceService.generate_invoice() using ReportLab to produce PDF bytes   Senior BE      **BE**     2.5           Backend

  **T-135**   Integrate email sending (Mailpit for dev / SendGrid for production)             Senior BE      **BE**     2             Backend

  **T-136**   Wire invoice generation and email into OrderService.place_order() flow          Senior BE      **BE**     1             Backend

  **T-137**   Create GET /api/v1/orders/{id}/invoice endpoint                                 Senior BE      **BE**     0.5           Backend

  **T-138**   Create invoice detail page accessible from order history                        Junior 1       **FE**     1.5           Frontend

**US-21B — Ownership Security Checks (Sprint 2 continuation — depends on order/cart/invoice endpoints)**

  **ID**       **Task Description**                                                                              **Assignee**   **Type**   **Est (h)**   **Layer**
  ------------ ------------------------------------------------------------------------------------------------- -------------- ---------- ------------- -----------
  **T-043**    Add ownership check to GET /api/v1/orders/{id} — raise 403 if order.user_id ≠ current_user.id   Emir           **BE**     1             Backend

  **T-044**    Add ownership check to GET /api/v1/orders/{id}/invoice — same 403 pattern                       Senior BE      **BE**     0.5           Backend

  **T-045**    Add ownership check to GET /api/v1/cart — cart must belong to current user                      Senior 4       **BE**     0.5           Backend

  **T-047b**   Write unit test: customer accessing another customer's order returns 403                         Junior 1       **TEST**   0.5           Backend

**Sprint 2 — Acceptance checklist before review on April 10**

-   A visitor can search products by keyword and sort by price or popularity

-   Out-of-stock products appear in search results but the add-to-cart button is disabled

-   A guest visitor can add products to cart without logging in

-   Guest cart items are preserved and merged after logging in

-   A logged-in customer can complete checkout: fill delivery address, enter card details, and place order

-   Stock count decrements correctly after order placement

-   Invoice PDF is generated and appears in the order confirmation

-   Invoice email is received in Mailpit (dev environment)

-   Product manager can add a new product via the admin interface

-   At least 25 total unit tests passing across both sprints

-   Minimum UI quality: product listing, cart, and checkout pages are visually presentable — not placeholder wireframes. Polish continues in Sprint 3 but basic layout must be done.

# **5. Sprint 3 — Detailed Task Breakdown**

**Dates:** April 10 – April 24, 2026 | **Stories: US-10, US-11A, US-11B, US-14, US-15, US-16, US-23**

**Sprint 3 Goal**

-   Customers can track order status and cancel eligible orders.

-   Product manager can view the delivery queue and advance delivery states.

-   Customers can submit reviews; product manager can approve or reject them.

-   Wishlist is live and discount notification emails are wired up.

-   Concurrent checkout is safe — no overselling under simultaneous purchases.

**US-10 — Track and Cancel Orders**

  **ID**      **Task Description**                                                                                    **Assignee**   **Type**   **Est (h)**   **Layer**
  ----------- ------------------------------------------------------------------------------------------------------- -------------- ---------- ------------- -----------
  **T-201**   Add PATCH /api/v1/orders/{id} endpoint — customer cancel (validates status is pending or confirmed)   Emir           **BE**     1             Backend

  **T-202**   Write OrderService logic: cancel_order() with state validation, return 400 if not cancellable           Emir           **BE**     1.5           Backend

  **T-203**   Write 2 unit tests: cancel success when pending, cancel returns 400 when processing                     Junior 1       **TEST**   1             Backend

  **T-204**   Create order history page listing customer's orders with status badges and cancel button               Junior 1       **FE**     2             Frontend

  **T-205**   Create order detail page showing full order info and current status                                     Junior 1       **FE**     1.5           Frontend

  **T-206**   Disable cancel button on frontend when order is in non-cancellable state                                Junior 1       **FE**     0.5           Frontend

**US-11A — View Delivery Queue**

  **ID**      **Task Description**                                                                                                                                               **Assignee**   **Type**   **Est (h)**   **Layer**
  ----------- ------------------------------------------------------------------------------------------------------------------------------------------------------------------ -------------- ---------- ------------- -----------
  **T-207**   Verify GET /api/v1/admin/orders?status= returns all required delivery fields: order_id, customer_id, product_id, quantity, total_price, delivery_address, status   Senior 4       **BE**     1             Backend

  **T-208**   Extend admin orders response schema to include customer_name and delivery_address explicitly                                                                       Senior 4       **BE**     1             Backend

  **T-209**   Create admin delivery queue page — filterable by status (processing / in_transit / delivered)                                                                    Senior 4       **FE**     2.5           Frontend

  **T-210**   Delivery queue table shows: delivery ID, customer, product list, quantity, total, address, status                                                                  Senior 4       **FE**     1.5           Frontend

  **T-211**   Add role guard: delivery queue page accessible only to product managers                                                                                            Senior 4       **FE**     0.5           Frontend

**US-11B — Update Delivery Status**

  **ID**      **Task Description**                                                                                     **Assignee**   **Type**   **Est (h)**   **Layer**
  ----------- -------------------------------------------------------------------------------------------------------- -------------- ---------- ------------- -----------
  **T-212**   Implement state transition validation in OrderService: only valid progressions allowed, 400 on invalid   Senior 4       **BE**     1.5           Backend

  **T-213**   Write 2 unit tests: valid status transition (processing → in_transit), invalid returns 400               Senior 4       **TEST**   1             Backend

  **T-214**   Add status change action button to delivery queue row (dropdown: processing / in_transit / delivered)    Senior 4       **FE**     1.5           Frontend

  **T-215**   Status update propagates immediately to customer's order tracking view via React Query invalidation     Senior 4       **FE**     1             Frontend

**US-14 — Rate and Comment on Products**

  **ID**      **Task Description**                                                                                                         **Assignee**   **Type**   **Est (h)**   **Layer**
  ----------- ---------------------------------------------------------------------------------------------------------------------------- -------------- ---------- ------------- -----------
  **T-216**   Create Review SQLAlchemy model (product_id, user_id, rating 1-5, comment, approval_status, created_at); generate migration   Junior 1       **DB**     1.5           Backend

  **T-217**   Create ReviewRepository with get_approved_by_product, create, approve/reject methods                                         Junior 1       **BE**     1             Backend

  **T-218**   Create ReviewService.submit_review() — defaults to pending, validates rating 1–5                                          Junior 1       **BE**     1             Backend

  **T-219**   Create POST /api/v1/products/{id}/reviews and GET endpoints + Pydantic schemas                                               Junior 1       **BE**     1             Backend

  **T-220**   Write 3 unit tests: submission accepted, pending default status, only approved reviews returned                              Junior 1       **TEST**   1.5           Backend

  **T-221**   Add review form (star rating + text comment) to product detail page                                                          Deniz          **FE**     2             Frontend

  **T-222**   Display approved reviews list on product detail page                                                                         Deniz          **FE**     1.5           Frontend

  **T-223**   Show average rating on product listing card and detail page                                                                  Deniz          **FE**     1             Frontend

**US-15 — Moderate Product Reviews**

  **ID**      **Task Description**                                                                          **Assignee**   **Type**   **Est (h)**   **Layer**
  ----------- --------------------------------------------------------------------------------------------- -------------- ---------- ------------- -----------
  **T-224**   Create PATCH /api/v1/admin/reviews/{id} endpoint (approval_status: approved | rejected)      Junior 1       **BE**     0.5           Backend

  **T-225**   Create DELETE /api/v1/admin/reviews/{id} endpoint (hard delete)                               Junior 1       **BE**     0.5           Backend

  **T-226**   Write 2 unit tests: approve makes review visible, reject keeps it hidden                      Junior 1       **TEST**   1             Backend

  **T-227**   Create admin review moderation page listing all pending reviews with approve/reject buttons   Junior 2       **FE**     2.5           Frontend

  **T-228**   Approved review appears on product page immediately (React Query invalidation)                Junior 2       **FE**     0.5           Frontend

**US-16 — Wishlist and Discount Alerts**

  **ID**      **Task Description**                                                                                         **Assignee**   **Type**   **Est (h)**   **Layer**
  ----------- ------------------------------------------------------------------------------------------------------------ -------------- ---------- ------------- -----------
  **T-229**   Create Wishlist SQLAlchemy model (user_id, product_id); generate migration                                   Junior 2       **DB**     1             Backend

  **T-230**   Create WishlistRepository and WishlistService with add, remove, get_by_user methods                          Junior 2       **BE**     1             Backend

  **T-231**   Create GET, POST, DELETE /api/v1/wishlist/items endpoints                                                    Junior 2       **BE**     1             Backend

  **T-232**   Implement notification trigger: when discount is applied, email all users who have that product wishlisted   Junior 2       **BE**     2             Backend

  **T-233**   Create wishlist page showing saved products with current price and discount badge if active                  Junior 2       **FE**     2             Frontend

  **T-234**   Add add-to-wishlist button on product listing and detail pages                                               Junior 2       **FE**     1             Frontend

**US-23 — Concurrency & Stock Consistency**

  **ID**      **Task Description**                                                                                                      **Assignee**   **Type**   **Est (h)**   **Layer**
  ----------- ------------------------------------------------------------------------------------------------------------------------- -------------- ---------- ------------- -----------
  **T-235**   Wrap stock decrement and order creation in a single database transaction in OrderService.place_order()                    Senior BE      **BE**     2             Backend

  **T-236**   Add SELECT FOR UPDATE on product stock row during order placement to prevent race conditions                              Senior BE      **BE**     1.5           Backend

  **T-237**   Re-validate stock quantity at order placement time (not only at add-to-cart time)                                         Emir           **BE**     1             Backend

  **T-238**   Write 3 unit tests: concurrent stock decrement handled correctly, oversell prevented, transaction rolls back on failure   Junior 1       **TEST**   2             Backend

  **T-239**   Manual test: simulate two simultaneous checkouts for last item in stock — confirm exactly one succeeds                  Junior 1       **TEST**   1             Backend

**Sprint 3 — Acceptance checklist before review on April 24**

-   Customer can view order history and track status (processing / in_transit / delivered)

-   Customer can cancel an order that is still in pending or confirmed state

-   Product manager delivery queue shows all required fields including delivery address

-   Product manager can advance delivery status through the correct state sequence

-   Customer can submit a 1–5 star rating and optional comment on a product

-   Product manager can approve or reject reviews from the admin panel

-   Approved reviews are visible on the product detail page; pending/rejected are not

-   Wishlist page works — products can be added and removed

-   Simultaneous checkout test passes — no negative stock values possible

-   At least 15 new unit tests added this sprint (cumulative 40+)

# **6. Sprint 4 — Detailed Task Breakdown**

**Dates:** April 24 – May 8, 2026 | **Stories: US-13, US-17, US-18, US-19 + Progress Demo polish**

**Sprint 4 Warning — Progress demo is May 1, mid-sprint**

-   Sprint 4 starts April 24. Progress demo is May 1. That is 7 days into a 2-week sprint.

-   Features 1, 3, 4, 5, 7, 9 must be fully polished and demo-ready by April 30.

-   The team must allocate the first half of Sprint 4 to integration, polish, and demo rehearsal.

-   New feature work (discounts, refunds, invoice export) starts after the demo on May 1.

-   Do not try to ship new features the day before the demo.

**Progress Demo Polish (April 24 – April 30)**

  **ID**      **Task Description**                                                                             **Assignee**   **Type**   **Est (h)**   **Layer**
  ----------- ------------------------------------------------------------------------------------------------ -------------- ---------- ------------- -----------
  **T-301**   End-to-end walkthrough: browse → add to cart → login → checkout → invoice → order tracking       All            **TEST**   2             Both

  **T-302**   Fix any broken flows found during walkthrough — assign fixes to responsible member             All            **BE**     3             Both

  **T-303**   Ensure product detail page shows all 9 course-required fields plus supplement fields             Junior 2       **FE**     1             Frontend

  **T-304**   Ensure out-of-stock products appear in search results with disabled add-to-cart button           Deniz          **FE**     0.5           Frontend

  **T-305**   Ensure order status page shows processing / in_transit / delivered correctly                     Junior 1       **FE**     0.5           Frontend

  **T-306**   Verify invoice PDF is generated and email is received after order placement                      Junior 1       **TEST**   1             Backend

  **T-307**   Verify review submission and product manager approval flow works end-to-end                      Junior 1       **TEST**   1             Both

  **T-308**   Basic UI review: no broken layouts, readable fonts, consistent spacing on all demo pages         Deniz          **FE**     2             Frontend

  **T-309**   Seed database with realistic supplement products for demo (at least 20 products, 5 categories)   Junior 2       **BE**     1.5           Backend

**US-17 — Sales Manager: Set Initial Price and Manage Discounts**

  **ID**       **Task Description**                                                                                                              **Assignee**   **Type**   **Est (h)**   **Layer**
  ------------ --------------------------------------------------------------------------------------------------------------------------------- -------------- ---------- ------------- -----------
  **T-309b**   Create PATCH /api/v1/admin/products/{id}/price endpoint — accessible to sales managers only, sets base price field on product   Senior BE      **BE**     1             Backend

  **T-309c**   Write 2 unit tests: sales manager can set price, product manager or customer cannot (403)                                         Junior 1       **TEST**   0.5           Backend

  **T-309d**   Add initial price set/edit action to the admin product list in the sales manager panel                                            Junior 2       **FE**     1             Frontend

  **T-310**    Create Discount SQLAlchemy model (product_ids, discount_rate, original_prices, created_by, created_at); generate migration        Senior BE      **DB**     1.5           Backend

  **T-311**    Create DiscountService.apply_discount(): recalculates product prices and stores original price for restoration                    Senior BE      **BE**     2             Backend

  **T-312**    Create DiscountService.remove_discount(): restores original prices from stored values                                             Senior BE      **BE**     1             Backend

  **T-313**    Wire wishlist notification into DiscountService.apply_discount() — emails wishlisted users                                      Junior 2       **BE**     1.5           Backend

  **T-314**    Create POST /api/v1/admin/discounts and DELETE /api/v1/admin/discounts/{id} endpoints                                             Senior BE      **BE**     1             Backend

  **T-315**    Write 3 unit tests: price recalculation, price restoration on delete, notification triggered                                      Senior BE      **TEST**   1.5           Backend

  **T-316**    Create admin discount management page — select products, set discount %, apply/remove                                           Junior 2       **FE**     2.5           Frontend

  **T-317**    Show discounted price and original price (strikethrough) on product listing and detail pages                                      Deniz          **FE**     1             Frontend

**US-18 — Request a Refund for a Purchased Item**

  **ID**      **Task Description**                                                                                                                                                                                  **Assignee**   **Type**   **Est (h)**   **Layer**
  ----------- ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- -------------- ---------- ------------- -----------
  **T-318**   Create RefundRequest SQLAlchemy model (order_id, order_item_id, status, reason, refund_amount, created_at); generate migration                                                                        Emir           **DB**     1.5           Backend

  **T-319**   Create RefundService.request_refund(): validates 30-day window, calculates discount-inclusive refund amount                                                                                           Emir           **BE**     2             Backend

  **T-320**   Create POST /api/v1/orders/{order_id}/items/{item_id}/refund-requests endpoint                                                                                                                        Emir           **BE**     1             Backend

  **T-321**   Write 4 unit tests: 30-day boundary, discount-inclusive amount, duplicate prevention, state defaults to requested                                                                                     Junior 1       **TEST**   2             Backend

  **T-322**   Add refund request button to order history — visible only for items whose status is delivered AND whose purchase date is within the last 30 days (these two conditions are checked independently)   Junior 1       **FE**     2             Frontend

  **T-323**   Show refund request status on order detail page (requested / approved_waiting_return / returned_received / refunded / rejected)                                                                       Junior 1       **FE**     1             Frontend

**US-19 — Evaluate and Process Refund Requests**

  **ID**      **Task Description**                                                                                                                                                                **Assignee**   **Type**   **Est (h)**   **Layer**
  ----------- ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- -------------- ---------- ------------- -----------
  **T-324**   Create GET /api/v1/admin/refund-requests endpoint with status filter                                                                                                                Senior 4       **BE**     1             Backend

  **T-325**   Create PATCH /api/v1/admin/refund-requests/{id} supporting all state transitions: requested → approved_waiting_return → returned_received → refunded, and → rejected at any stage   Senior 4       **BE**     2             Backend

  **T-326**   On transition to refunded: restore item stock quantity and credit refund amount to customer account record                                                                          Senior 4       **BE**     1.5           Backend

  **T-327**   Write 3 unit tests: state transitions, stock restored on refunded, reject at any stage                                                                                              Senior 4       **TEST**   1.5           Backend

  **T-328**   Create admin refund management page: list all requests with customer, product, order date, amount, reason, current state                                                            Senior 4       **FE**     2.5           Frontend

  **T-329**   Add state-change action buttons on refund row: approve, mark returned, authorize refund, reject                                                                                     Senior 4       **FE**     1.5           Frontend

**US-13 — Invoice Export for Sales Manager**

  **ID**      **Task Description**                                                                                       **Assignee**   **Type**   **Est (h)**   **Layer**
  ----------- ---------------------------------------------------------------------------------------------------------- -------------- ---------- ------------- -----------
  **T-330**   Create GET /api/v1/admin/invoices?from=&to= endpoint with pagination                                       Senior BE      **BE**     1             Backend

  **T-331**   Create GET /api/v1/admin/invoices/{id}/pdf endpoint returning PDF binary (Content-Type: application/pdf)   Senior BE      **BE**     1.5           Backend

  **T-332**   Create admin invoices page with date range picker and paginated invoice list                               Junior 2       **FE**     2             Frontend

  **T-333**   Add download PDF and print buttons to invoice detail view                                                  Junior 2       **FE**     1             Frontend

  **T-334**   Verify invoice list shows: invoice ID, customer name, total amount, order date                             Junior 2       **TEST**   0.5           Backend

**Sprint 4 — Acceptance checklist before review on May 8**

-   Progress demo on May 1 passed — features 1, 3, 4, 5, 7, 9 all demonstrated successfully

-   Sales manager can apply a discount rate to products; prices update automatically

-   Discount notification email is sent to customers who have the product wishlisted

-   Removing a discount restores original prices correctly

-   Customer can request a refund for a specific item within 30 days of purchase

-   Refund request is blocked after 30 days from purchase date

-   Sales manager can advance refund through all four states to completion

-   Stock is restored when refund is finalized

-   Sales manager can view invoices filtered by date range and download PDF

-   At least 15 new unit tests added this sprint (cumulative 55+)

# **7. Sprint 5 — Detailed Task Breakdown**

**Dates:** May 15 – May 22, 2026 | **Stories: US-20, US-22 + UI polish + Deployment + Final prep**

**Sprint 5 Goal**

-   Revenue and profit chart is live in the admin panel.

-   Security hardening complete: token expiry, HTTPS in production, input validation.

-   Application is deployed on a shared server — not just running on one laptop.

-   Every feature from the full requirements list is working and demo-ready.

-   UI is polished and professional-looking across all customer and admin pages.

**US-20 — Revenue and Profit Chart**

  **ID**      **Task Description**                                                                            **Assignee**   **Type**   **Est (h)**   **Layer**
  ----------- ----------------------------------------------------------------------------------------------- -------------- ---------- ------------- -----------
  **T-401**   Create GET /api/v1/admin/reports/revenue?from=&to= endpoint                                     Senior BE      **BE**     1             Backend

  **T-402**   Implement revenue query: sum of order totals in date range, excluding refunded amounts          Senior BE      **BE**     2.5           Backend

  **T-403**   Calculate profit: revenue minus estimated cost (cost field on product or configurable margin)   Senior BE      **BE**     1.5           Backend

  **T-404**   Return chart_data array: array of { date, revenue, profit } objects for chart rendering         Senior BE      **BE**     1             Backend

  **T-405**   Write 2 unit tests: revenue calculation excludes refunded orders, date range filter works       Senior BE      **TEST**   1             Backend

  **T-406**   Create admin revenue report page with date range picker                                         Junior 2       **FE**     1.5           Frontend

  **T-407**   Render revenue / profit chart using a charting library (recharts or chart.js)                   Junior 2       **FE**     2             Frontend

  **T-408**   Display total revenue, total profit, and margin summary alongside chart                         Junior 2       **FE**     1             Frontend

**US-22 — Security Hardening**

  **ID**       **Task Description**                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    **Assignee**   **Type**   **Est (h)**   **Layer**
  ------------ --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- -------------- ---------- ------------- -----------
  **T-409**    Set JWT token expiry (e.g. 24 hours) in token creation — verify expired tokens are rejected                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           Emir           **BE**     1             Backend

  **T-410**    Verify refresh token or re-login flow handles expiry gracefully on the frontend                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         Emir           **FE**     1             Frontend

  **T-411**    Audit all response schemas: confirm no sensitive fields (password_hash, full card data) leak in any endpoint                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            Junior 1       **TEST**   1.5           Backend

  **T-412**    Confirm all SQL queries go through SQLAlchemy ORM or parameterized queries — no string interpolation                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  Junior 1       **BE**     1             Backend

  **T-413**    Verify GitHub Secrets are used in CI — no credentials committed to repo                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               Senior 4       **CI**     0.5           GitHub

  **T-414**    Configure HTTPS on production server (use free SSL cert via Let's Encrypt or hosting provider)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         Senior 4       **CI**     2             DevOps

  **T-415**    Write 2 unit tests: expired token returns 401, /admin/ route with customer token returns 403                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            Junior 1       **TEST**   1             Backend

  **T-415b**   Verify and document that the plan satisfies the course brief's encryption requirement for sensitive data: (1) passwords are bcrypt-hashed — never stored plain text; (2) full credit card numbers are never persisted — only last4 + brand stored; (3) invoice PDFs stored in encrypted-at-rest server-side storage, accessible only via authenticated endpoints with ownership check — never via public URLs; (4) sensitive user-account fields (address, tax_id) stored encrypted at rest in the database — confirm field-level encryption or confirm that the database volume itself uses encryption at rest and document which approach is used; (5) RBAC applied on top of all the above. Add explicit confirmation of each point to the architecture security section.   Emir           **TEST**   1.5           Backend

**UI Polish**

  **ID**      **Task Description**                                                                        **Assignee**   **Type**   **Est (h)**   **Layer**
  ----------- ------------------------------------------------------------------------------------------- -------------- ---------- ------------- -----------
  **T-416**   Audit all pages for visual consistency: spacing, font sizes, button styles, color palette   Deniz          **FE**     2             Frontend

  **T-417**   Ensure mobile responsiveness on product listing, product detail, cart, and checkout pages   Deniz          **FE**     2             Frontend

  **T-418**   Add loading states and empty states to all React Query-powered pages                        Deniz          **FE**     1.5           Frontend

  **T-419**   Add error handling UI: toast notifications or inline errors for failed API calls            Deniz          **FE**     1.5           Frontend

  **T-420**   Review and polish admin panel layout — navigation, tables, action buttons                 Junior 2       **FE**     2             Frontend

**Deployment & Final Demo Preparation**

  **ID**      **Task Description**                                                                             **Assignee**   **Type**   **Est (h)**   **Layer**
  ----------- ------------------------------------------------------------------------------------------------ -------------- ---------- ------------- -----------
  **T-421**   Select and configure a shared deployment environment (Railway / Render / VPS)                    Emir           **CI**     2             DevOps

  **T-422**   Set up production PostgreSQL instance and run alembic upgrade head                               Emir           **DB**     1             DevOps

  **T-423**   Configure production environment variables as secrets in deployment platform                     Emir           **CI**     0.5           DevOps

  **T-424**   Deploy FastAPI backend to production and verify all endpoints respond correctly                  Senior 4       **CI**     1.5           DevOps

  **T-425**   Deploy Next.js frontend to production and verify API connection                                  Senior 4       **CI**     1.5           DevOps

  **T-426**   Seed production database with demo-ready supplement products and user accounts                   Junior 2       **BE**     1             Backend

  **T-427**   Full end-to-end test on production: all three roles (customer, product manager, sales manager)   All            **TEST**   2             Both

  **T-428**   Prepare demo script: step-by-step walkthrough covering all features in the course requirements   Deniz          **CI**     1.5           Both

**Sprint 5 / Final Demo — Acceptance checklist**

-   Revenue chart renders correctly for any given date range

-   Refunded orders are excluded from revenue calculations

-   JWT tokens expire after 24 hours — expired token returns 401

-   No sensitive fields appear in any API response

-   Application is live on a shared URL — not running on a local machine

-   All three roles can be demonstrated: customer full flow, product manager admin, sales manager admin

-   Every course requirement is covered: features 1–17 from the requirements list

-   UI is professional-looking across all pages

-   Total unit tests across all sprints: 55+ (well above the 25 per demo requirement)

# **8. Jira Setup Instructions**

Complete this before the first sprint planning meeting. Takes approximately 1 hour.

**Story point** — görevin karmaşıklığını, belirsizliğini ve eforunun büyüklüğünü temsil eden görece bir puandır. Fibonacci skalası kullanılır: 1, 2, 3, 5, 8, 13.

**Pratikte nasıl düşünmeli:**

  **Karmaşıklık**                                   **Örnek**                          **Story Point**
  ------------------------------------------------- ---------------------------------- -----------------
  Trivial — bilinen, net, bağımsız                T-001 repo kurma                   **1**

  Küçük — birkaç adım, düşük belirsizlik          T-009 Next.js init                 **2**

  Orta — birden fazla katman, biraz belirsizlik   T-026 JWT encode/decode            **3**

  Büyük — karmaşık logic, bağımlılıklar var       T-126 OrderService.place_order()   **5**

  Çok büyük — yüksek belirsizlik, çok katmanlı    Nadir, genelde story seviyesinde   **8+**

**Rough mapping for your project:**

  **Est (h)**   **Story Points**   **Reasoning**
  ------------- ------------------ ----------------------------------------------
  0.5           **1**              Trivial, mechanical, no uncertainty

  1             **1**              Small, clear, straightforward

  1.5           **2**              Small-medium, a couple of steps

  2             **2**              Medium, clear scope

  2.5           **3**              Medium, some moving parts

  3             **3**              Larger, but well understood

  3+            **5**              Complex, multiple layers or some uncertainty

## **8.1 Create all 25 user stories in the Product Backlog**

-   Create a story in Jira for each of US-01 through US-23 (including US-06A, US-06B, US-11A, US-11B as separate stories)

-   Use the story template from the Tooling Guide (As a / I want / So that / Acceptance Criteria)

-   Note: US-06A and US-06B are counted as two separate stories (split from original US-06)

-   Note: US-11A and US-11B are counted as two separate stories (split from original US-11)

-   Set priority: Must Have / Should Have / Could Have

-   Assign to the appropriate team member per the assignee column in Section 2

-   Do NOT add stories to a sprint yet — they stay in the backlog until sprint planning

## **8.2 Sprint 1 — Move tasks to the sprint board**

-   Create Sprint 1 in Jira with dates March 13 – March 27

-   Create all Sprint 1 tasks listed in Section 3 as sub-tasks or tasks under their parent stories

-   Assign each task to the appropriate team member

-   Set story points or hour estimates where shown

## **8.3 Naming convention for Jira tickets**

> Stories: CS308-US01, CS308-US02, \...
>
> Tasks: CS308-T001, CS308-T002, \...
>
> Bugs: CS308-BUG001, CS308-BUG002, \...

Reference ticket IDs in PR titles:

> feat(auth): implement login with JWT cookie [CS308-T028]

## **8.4 Bug reporting discipline**

**Bug Report Reminder — 5 per demo is graded**

-   File a bug immediately when something breaks during development. Do not fix it silently.

-   Use the Jira bug template from the Tooling Guide.

-   During sprint review, walk through the app together and deliberately look for edge cases.

-   Target: at least 2 bugs per sprint filed and tracked to resolution.

-   Bugs that are fixed count — the requirement is for filed reports, not open bugs.

*— Product Backlog & Sprint Plan · Ready for Jira —*
