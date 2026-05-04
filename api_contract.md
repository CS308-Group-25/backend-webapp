**CS308 Online Store**

**API Contract --- v1 FINAL**

*Reviewed and confirmed across three external review rounds*

**Base URL: /api/v1 | Backend: FastAPI | Auth: JWT in httpOnly Cookie**

# **1. Core Contract Rules**

## **1.1 URL Design --- Resources, Not Actions**

URLs are nouns. HTTP methods are the verbs. Never put action words in a URL.

  ------------------------------------------------------------------------------------------------
  **❌ Wrong --- action in URL**      **✅ Correct --- noun URL + method**
  ----------------------------------- ------------------------------------------------------------
  POST /getProducts                   GET /products

  POST /createOrder                   POST /orders

  GET /deleteProduct/5                DELETE /admin/products/5

  PUT /orders/5/cancel                PATCH /orders/5 body: { status: cancelled }

  PUT /comments/3/approve             PATCH /admin/reviews/3 body: { approval_status: approved }
  ------------------------------------------------------------------------------------------------

## **1.2 Versioning**

Every route is prefixed with /api/v1/. Set once in FastAPI router configuration, applied globally.

```json
app.include_router(products_router, prefix="/api/v1")
```

## **1.3 Admin Namespace & RBAC**

All endpoints requiring a manager role live under /api/v1/admin/. One dependency protects the entire namespace.

**RBAC Rule by URL Prefix**

-   /api/v1/auth/... → Anyone (public)

-   /api/v1/products, /categories (GET) → Anyone (public)

-   /api/v1/cart, /orders, /wishlist, /reviews → Authenticated customers

-   /api/v1/admin/... → Managers only (product_manager or sales_manager)

-   One FastAPI dependency --- Depends(require_admin) --- protects every /admin/ route

-   Depends(require_product_manager) and Depends(require_sales_manager) for role-specific admin routes
## **1.4 HTTP Methods**

  ------------------------------------------------------------------------------------------------
  **Method**   **Semantics**                            **Example**
  ------------ ---------------------------------------- ------------------------------------------
  **GET**      Retrieve resource or list                GET /products

  **POST**     Create a new resource                    POST /orders

  **PATCH**    Partial update --- one or a few fields   PATCH /orders/5 → { status: in_transit }

  **DELETE**   Remove a resource                        DELETE /admin/products/5

  **PUT**      Full replacement --- rarely used here    Avoid unless replacing entire resource
  ------------------------------------------------------------------------------------------------

## **1.5 HTTP Status Codes**

  ------------------------------------------------------------------------------------------------------------------------------------
  **Status Code**                 **Meaning**                                      **Notes**
  ------------------------------- --------------------------------- -------------- ---------------------------------------------------
  **200 OK**                      Success, returns data                            

  **201 Created**                 Resource successfully created                    

  **204 No Content**              Success, nothing to return                       

  **400 Bad Request**             Semantic / business logic error                  *e.g. order already cancelled, refund \> 30 days*

  **401 Unauthorized**            No valid JWT cookie                              *Not authenticated*

  **403 Forbidden**               Wrong role for this endpoint                     *Authenticated but not permitted*

  **404 Not Found**               Resource does not exist                          

  **422 Unprocessable Entity**    Pydantic validation failure                      *FastAPI default --- do not override*

  **500 Internal Server Error**   Unexpected server-side failure                   
  ------------------------------------------------------------------------------------------------------------------------------------

## **1.6 Response Format**

Consistency comes from the Pydantic response_model, not from a cosmetic wrapper. Do not force every endpoint into a { data, message } envelope.

  -----------------------------------------------------------------------------------------------------
  **Case**               **Format**               **Example**
  ---------------------- ------------------------ -----------------------------------------------------
  **Single resource**    Return object directly   { "id": 1, "name": "Laptop", ... }

  **List**               Return array directly    [{ "id": 1 }, { "id": 2 }]

  **Paginated list**     Pagination wrapper       { "items": [...], "total": 50, "page": 1 }

  **Created resource**   Return created object    { "id": 5, ... } → 201

  **Error**              FastAPI detail field     { "detail": "Product not found" }

  **Validation error**   FastAPI 422 automatic    { "detail": [{ "loc":..., "msg":... }] }
  -----------------------------------------------------------------------------------------------------

## **1.7 Never Expose the Database Model Directly**

The Pydantic response_model is a deliberate contract --- not a dump of the ORM row. Always declare response_model on every endpoint. The User model contains password_hash --- that field must never appear in any response.

```json
# UserPublicSchema exposes: id, name, email, role --- never password_hash
```

## **1.8 Team Workflow --- Schema First**

Follow this order for every new endpoint. Do not skip steps.

-   Step 1 --- Agree on the endpoint: URL, method, request shape, response shape. Record it in this document first.

-   Step 2 --- Backend writes Pydantic schemas (schema.py). No business logic yet.

-   Step 3 --- FastAPI auto-generates /docs. Frontend can inspect the contract immediately.

-   Step 4 --- Frontend mocks the response with hardcoded data matching the agreed schema. UI work does not block on backend.

-   Step 5 --- Backend implements service and repository logic.

-   Step 6 --- Frontend connects to the real endpoint. Test together.

**Rule:** if it is not visible in /docs, it does not exist. The frontend never calls an undocumented endpoint.

# **2. Authentication Strategy**

JWT tokens stored in httpOnly cookies. The browser sends the cookie automatically --- no manual Authorization header needed on the frontend.

-   On login: FastAPI creates a signed JWT (user_id + role), sets it as an httpOnly cookie

-   On every protected request: FastAPI reads the cookie, decodes the JWT, injects the current user via Depends(get_current_user)

-   On logout: FastAPI clears the cookie server-side --- this is why the logout endpoint exists

-   httpOnly cookies are inaccessible to JavaScript, protecting against XSS attacks

**Auth Dependencies Used in Routes**

-   Depends(get_current_user) → any authenticated user

-   Depends(require_customer) → customer role only

-   Depends(require_admin) → product_manager or sales_manager

-   Depends(require_product_manager) → product_manager only

-   Depends(require_sales_manager) → sales_manager only
# **3. Order State Machine**

Orders are never deleted. They transition through statuses. Invalid transitions are rejected with 400.

**Normal delivery flow:**

> pending → confirmed → processing → in_transit → delivered

**Customer cancellation (allowed while pending or confirmed only):**

> pending or confirmed → cancelled

**Refund flow (item-level, within 30 days of delivery):**

> delivered item → refund_requested → refunded
Status transitions are enforced in the Order service layer using a Python Enum. The status field in PATCH request bodies is validated against this enum automatically by Pydantic.

# **4. Cart --- Guest vs Authenticated**

**Critical Rule --- Guest Cart Behaviour (Redline #2)**

-   The course requires users to add products to cart WITHOUT logging in.

-   Guest cart is client-side only --- managed in Zustand on the frontend before login.

-   The /api/v1/cart/... endpoints are for authenticated users only.

-   On login: the frontend merges the Zustand guest cart into the server cart via POST /api/v1/cart/items.

-   This behaviour is frontend responsibility --- the backend cart API assumes an authenticated user in every call.
# **5. Endpoint Reference**

Color legend: GET = green | POST = blue | PATCH = yellow | DELETE = red

## **5.1 Auth**

  -----------------------------------------------------------------------------------------------------------------------------------------------------------
  **Method**   **Path**                **Role**        **Request Body**                         **Response Body**                **Notes**
  ------------ ----------------------- --------------- ---------------------------------------- -------------------------------- ----------------------------
  **POST**     /api/v1/auth/register   Anyone          name, email, password, address, tax_id   user object (no password_hash)   *201*

  **POST**     /api/v1/auth/login      Anyone          email, password                          user object                      *Sets httpOnly JWT cookie*

  **POST**     /api/v1/auth/logout     Authenticated   —                                      —                              *Clears cookie. 204.*

  **GET**      /api/v1/auth/me         Authenticated   —                                      user object                      *Reads from JWT cookie*
  -----------------------------------------------------------------------------------------------------------------------------------------------------------

## **5.2 Products**

Public GET endpoints require no authentication. Admin write endpoints require product_manager role.

  --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  **Method**   **Path**                      **Role**          **Request Body**                                                                        **Response Body**        **Notes**
  ------------ ----------------------------- ----------------- --------------------------------------------------------------------------------------- ------------------------ --------------------------------------------------------
  **GET**      /api/v1/products              Anyone            ?search= &sort= &category= &page=                                                       paginated product list   *Out-of-stock items included; cannot be added to cart*

  **GET**      /api/v1/products/{id}         Anyone            —                                                                                     product detail           *Includes stock count and average rating*

  **POST**     /api/v1/admin/products        product_manager   name, model, serial_no, description, price, stock, warranty, distributor, category_id   created product          *201*

  **PATCH**    /api/v1/admin/products/{id}   product_manager   any subset of product fields                                                            updated product          *Partial update*

  **DELETE**   /api/v1/admin/products/{id}   product_manager   —                                                                                     —                      *Soft delete --- sets deleted_at. 204.*
  --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

## **5.3 Categories**

  -----------------------------------------------------------------------------------------------------------------------------------------------------------
  **Method**   **Path**                        **Role**          **Request Body**    **Response Body**   **Notes**
  ------------ ------------------------------- ----------------- ------------------- ------------------- ----------------------------------------------------
  **GET**      /api/v1/categories              Anyone            —                 category list       

  **POST**     /api/v1/admin/categories        product_manager   name, description   created category    *201*

  **PATCH**    /api/v1/admin/categories/{id}   product_manager   name, description   updated category    

  **DELETE**   /api/v1/admin/categories/{id}   product_manager   —                 —                 *400 if products still assigned to category. 204.*
  -----------------------------------------------------------------------------------------------------------------------------------------------------------

## **5.4 Cart (authenticated users only --- see Section 4 for guest cart)**

  -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  **Method**   **Path**                          **Role**   **Request Body**       **Response Body**          **Notes**
  ------------ --------------------------------- ---------- ---------------------- -------------------------- -----------------------------------------------------------------
  **GET**      /api/v1/cart                      Customer   —                    cart with items + totals   

  **POST**     /api/v1/cart/items                Customer   product_id, quantity   updated cart               *400 if out of stock. Used also for guest cart merge on login.*

  **PATCH**    /api/v1/cart/items/{product_id}   Customer   quantity               updated cart               *quantity: 0 removes the item*

  **DELETE**   /api/v1/cart/items/{product_id}   Customer   —                    —                        *204*
  -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------

## **5.5 Orders**

**Payment note:** The UI collects the full credit card number. The backend passes it transiently to the mock payment function and immediately discards it. Only card_last4 and card_brand are persisted. Full card numbers are never stored in the database.

  -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  **Method**   **Path**                    **Role**          **Request Body**                                                    **Response Body**      **Notes**
  ------------ --------------------------- ----------------- ------------------------------------------------------------------- ---------------------- -------------------------------------------------------------------------------------------
  **POST**     /api/v1/orders              Customer          delivery_address, card_number (transient), card_last4, card_brand   order + invoice_id     *Mock payment runs synchronously. Stock decremented. Invoice generated. Email sent. 201.*

  **GET**      /api/v1/orders              Customer          —                                                                 own orders list        *Customer sees own orders only*

  **GET**      /api/v1/orders/{id}         Customer          —                                                                 order detail           *403 if not own order*

  **PATCH**    /api/v1/orders/{id}         Customer          status: cancelled                                                   updated order          *400 if not in pending or confirmed state*

  **GET**      /api/v1/admin/orders        Admin             ?status= &from= &to= &page=                                         all orders paginated   *Also serves as delivery queue for product_manager --- see Section 6*

  **PATCH**    /api/v1/admin/orders/{id}   product_manager   status: processing | in_transit | delivered                       updated order          *Delivery progression. 400 on invalid transition.*
  -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

## **5.6 Reviews (Comments + Ratings unified)**

A review contains both a numeric rating (1--5 stars) and an optional text comment. Reviews are hidden from the public until approved by a product_manager.

  ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  **Method**   **Path**                        **Role**          **Request Body**                        **Response Body**       **Notes**
  ------------ ------------------------------- ----------------- --------------------------------------- ----------------------- ---------------------------------------------------
  **GET**      /api/v1/products/{id}/reviews   Anyone            —                                     approved reviews list   *Pending/rejected reviews not returned to public*

  **POST**     /api/v1/products/{id}/reviews   Customer          rating (1-5), comment (optional)        created review          *201. Approval status defaults to pending.*

  **PATCH**    /api/v1/admin/reviews/{id}      product_manager   approval_status: approved | rejected   updated review          *Approved review becomes publicly visible*

  **DELETE**   /api/v1/admin/reviews/{id}      product_manager   —                                     —                     *Hard delete. 204.*
  ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

## **5.7 Wishlist**

Follows the same /items sub-resource pattern as cart for naming consistency.

  --------------------------------------------------------------------------------------------------------------------------------------------------------------------
  **Method**   **Path**                              **Role**   **Request Body**   **Response Body**   **Notes**
  ------------ ------------------------------------- ---------- ------------------ ------------------- ---------------------------------------------------------------
  **GET**      /api/v1/wishlist/items                Customer   —                wishlist items      *Includes current price and active discount flag*

  **POST**     /api/v1/wishlist/items                Customer   product_id         updated wishlist    *201. Backend uses this list to send discount notifications.*

  **DELETE**   /api/v1/wishlist/items/{product_id}   Customer   —                —                 *204*
  --------------------------------------------------------------------------------------------------------------------------------------------------------------------

## **5.8 Refund Requests (item-level --- Redline #1)**

**Why item-level, not order-level**

-   The course brief explicitly requires selective product return within an order.

-   Example: a customer buys 3 items in one order and wants to return only 1 of them.

-   An order-level endpoint cannot support this --- a refund request must target a specific order item.

-   Endpoint: POST /api/v1/orders/{order_id}/items/{item_id}/refund-requests

-   On approval: that item's stock is restored, and the item's purchase price (discount-inclusive) is refunded.
  ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  **Method**   **Path**                                                    **Role**        **Request Body**               **Response Body**        **Notes**
  ------------ ----------------------------------------------------------- --------------- ------------------------------ ------------------------ --------------------------------------------------------------------------------
  **POST**     /api/v1/orders/{order_id}/items/{item_id}/refund-requests   Customer        reason (optional)              refund request object    *400 if \> 30 days since order delivery. 201.*

  **GET**      /api/v1/admin/refund-requests                               sales_manager   ?status= &page=                all refund requests      *Includes order_id, item_id, customer, amount, purchase_date*

  **PATCH**    /api/v1/admin/refund-requests/{id}                          sales_manager   status: approved | rejected   updated refund request   *On approve: restores item stock, refunds purchase price (discount-inclusive)*
  ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

## **5.9 Discounts**

Sales manager applies a discount rate to one or more products. The system recalculates prices and notifies wishlist users automatically.

  ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  **Method**   **Path**                       **Role**        **Request Body**                            **Response Body**   **Notes**
  ------------ ------------------------------ --------------- ------------------------------------------- ------------------- -----------------------------------------------
  **POST**     /api/v1/admin/discounts        sales_manager   product_ids (list), discount_rate (0-100)   discount object     *Triggers wishlist email notifications. 201.*

  **DELETE**   /api/v1/admin/discounts/{id}   sales_manager   —                                         —                 *Restores original prices. 204.*
  ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

## **5.10 Invoices**

Invoices are generated automatically when an order is placed. Customers access their own invoices. Sales managers access all invoices with date-range filtering.

  --------------------------------------------------------------------------------------------------------------------------------------------------------------------
  **Method**   **Path**                          **Role**        **Request Body**     **Response Body**    **Notes**
  ------------ --------------------------------- --------------- -------------------- -------------------- -----------------------------------------------------------
  **GET**      /api/v1/orders/{id}/invoice       Customer        —                  invoice object       *403 if not own order*

  **GET**      /api/v1/admin/invoices            sales_manager   ?from= &to= &page=   paginated invoices   *Date range filter for reporting period*

  **GET**      /api/v1/admin/invoices/{id}       sales_manager   —                  invoice detail       

  **GET**      /api/v1/admin/invoices/{id}/pdf   sales_manager   —                  PDF binary           *Content-Type: application/pdf. Can be printed or saved.*
  --------------------------------------------------------------------------------------------------------------------------------------------------------------------

## **5.11 Reports**

  ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  **Method**   **Path**                        **Role**        **Request Body**   **Response Body**                           **Notes**
  ------------ ------------------------------- --------------- ------------------ ------------------------------------------- ------------------------------------------------------------
  **GET**      /api/v1/admin/reports/revenue   sales_manager   ?from= &to=        { revenue, cost, profit, chart_data[] }   *Used to render the revenue / profit chart in admin panel*

  ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# **6. Delivery Queue --- Product Manager View (Redline #3)**

The course brief requires a delivery list with specific fields: delivery ID, customer ID, product ID, quantity, total price, delivery address, and a completed flag. This is implemented through the existing GET /api/v1/admin/orders endpoint --- no separate resource is needed.

**How Admin Orders endpoint serves as the Delivery Queue**

-   GET /api/v1/admin/orders?status=processing → items ready to ship

-   GET /api/v1/admin/orders?status=in_transit → items currently in transit

-   The response includes all required delivery fields (see below)

-   PATCH /api/v1/admin/orders/{id} → product_manager marks as in_transit or delivered

-   This satisfies the brief without opening a redundant deliveries resource
Delivery fields included in the admin orders response object:

  -----------------------------------------------------------------------------------------
  **order_id**           Serves as delivery ID
  ---------------------- ------------------------------------------------------------------
  **customer_id**        Customer who placed the order

  **customer_name**      For display in delivery list

  **delivery_address**   Shipping destination

  **items[]**          Array of { product_id, product_name, quantity, unit_price }

  **total_price**        Order total

  **status**             processing | in_transit | delivered --- acts as completed flag

  **created_at**         Order placement date
  -----------------------------------------------------------------------------------------

# **7. Standard Query Parameters**

  -------------------------------------------------------------------------------------------------------------------------------------------
  **Parameter**       **Example**                      **Behaviour**
  ------------------- -------------------------------- --------------------------------------------------------------------------------------
  **?search=**        ?search=laptop                   Case-insensitive match on product name and description. Out-of-stock items included.

  **?sort=**          ?sort=price_asc                  Options: price_asc | price_desc | popularity_desc | newest

  **?category=**      ?category=3                      Filter by category ID

  **?page=**          ?page=2                          Pagination. Default page size: 20 items.

  **?from= / ?to=**   ?from=2026-01-01&to=2026-03-31   ISO date range for invoices and revenue reports

  **?status=**        ?status=processing               Filter orders or refund requests by status enum value
  -------------------------------------------------------------------------------------------------------------------------------------------

# **8. Progress Demo Priority (May 1)**

Course requires features 1, 3, 4, 5, 7, and 9 to be working at the progress demo.

**Minimum Endpoints Live by May 1**

-   Feature 1 --- Browse & cart: GET /products, GET /products/{id}, POST /cart/items, GET /cart

-   Feature 3 --- Stock & status: POST /orders, PATCH /admin/orders/{id}, GET /orders/{id}

-   Feature 4 --- Login + payment + invoice: POST /auth/login, POST /orders (mock), GET /orders/{id}/invoice

-   Feature 5 --- Reviews: POST /products/{id}/reviews, PATCH /admin/reviews/{id}

-   Feature 7 --- Search & sort: GET /products?search=&sort= (out-of-stock shown, not addable to cart)

-   Feature 9 --- Product fields: All required fields present: id, name, model, serial_no, description, stock, price, warranty, distributor
# **9. Request & Response Examples**

## **POST /api/v1/orders --- Place an Order**

**Request Body**

```json
{
"delivery_address": "123 Main St, Istanbul",
"card_number": "4111111111111111", // transient --- never persisted
"card_last4": "1111",
"card_brand": "Visa"
}
```

**Response --- 201 Created**

```json
{
"id": 88,
"status": "confirmed",
"total": 1299.99,
"invoice_id": 42,
"items": [{ "product_id": 5, "name": "Laptop", "quantity": 1, "price": 1299.99 }],
"delivery_address": "123 Main St, Istanbul",
"created_at": "2026-03-18T14:30:00Z"
}
```

## **POST /api/v1/orders/{order_id}/items/{item_id}/refund-requests**

**Request Body**

```json
{
"reason": "Item arrived damaged"
}
```

**Response --- 201 Created**

```json
{
"id": 7,
"order_id": 88,
"order_item_id": 3,
"product_name": "Laptop",
"refund_amount": 1299.99,
"status": "pending",
"created_at": "2026-04-01T10:00:00Z"
}
```

## **PATCH /api/v1/admin/orders/{id} --- Update Delivery Status**

**Request Body**

```json
{
"status": "in_transit"
}
```

**Response --- 200 OK**

```json
{
"id": 88,
"status": "in_transit",
"updated_at": "2026-03-19T09:00:00Z"
}
```

## **POST /api/v1/products/{id}/reviews**

**Request Body**

```json
{
"rating": 8,
"comment": "Great product, arrived on time."
}
```

**Response --- 201 Created**

```json
{
"id": 12,
"product_id": 5,
"rating": 8,
"comment": "Great product, arrived on time.",
"approval_status": "pending",
"created_at": "2026-03-18T15:00:00Z"
}
```

## **Error Responses**

**400 --- Business Logic Error**

```json
{
"detail": "Refund request must be submitted within 30 days of delivery"
}
```

**422 --- Pydantic Validation Failure (FastAPI automatic)**

```json
{
"detail": [
  {
    "loc": ["body", "rating"],
    "msg": "value is not a valid integer",
    "type": "type_error.integer"
  }
]
}
```

*--- API Contract v1 FINAL --- Ready for team distribution ---*
