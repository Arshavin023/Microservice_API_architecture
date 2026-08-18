# Pizzasale API

A microservices-based ecommerce platform for a pizza restaurant, built with **FastAPI**, **PostgreSQL**, **RabbitMQ**, and a **React** frontend.

Users can register, verify their email, and authenticate securely. A new registration triggers an asynchronous, event-driven workflow that creates a user profile in a separate service. Profiles can be read and updated through a JWT-protected API. A separate catalog service exposes a public, browsable menu — categories and products with size-based pricing — while keeping all writes restricted to staff accounts. Users can add items to a persistent cart, check out with real-time price verification, and pay through Paystack's hosted checkout page — with webhook-driven order status updates flowing back through the system automatically. Once paid, staff dispatch and deliver orders through a dedicated shipping service, with the order state machine advancing automatically via RabbitMQ events, and customers receiving email notifications at every stage via AWS SES. The entire flow is accessible through a React single-page application served by nginx, which proxies API calls to the appropriate backend service so the frontend never knows the system is split across eight separate services. No service touches another's database, and no service calls another's API except where synchronous communication is the correct architectural choice.

---

## Architecture

This project follows eight complementary patterns:

**1. Database-per-service** — each microservice owns its own PostgreSQL database and is the only service allowed to read/write it directly.

**2. Event-driven communication** — services don't call each other's APIs synchronously to propagate side effects. Instead, a service publishes an event when something happens, and any number of other services can independently react to it, without the publisher knowing or caring who's listening.

**3. Shared-secret JWT verification across services** — `auth-service` issues JWTs; `user-service`, `product-service`, `order-service`, and `shipping-service` independently verify them using the same signing secret, without ever calling back into `auth-service`. Each service trusts the token's signature, not a network round-trip.

**4. Public reads, claim-gated writes** — `product-service`'s menu is openly browsable by anyone, but creating, updating, or deleting catalog data requires a JWT carrying `is_staff: true`. The same pattern applies to `shipping-service` — customers can track their own shipment, but only staff can create or advance one. Authentication (who you are) and authorization (what you're allowed to do) are enforced as two distinct, separately-tested checks.

**5. Synchronous service-to-service calls where correctness requires it** — checkout verifies live prices against `product-service` and initializes payment via `payment-service` synchronously. This is a deliberate exception to the event-driven default: a user sitting at the checkout screen needs an immediate answer, and a failed payment must fail the whole checkout atomically rather than leaving an order in an ambiguous state.

**6. Webhook-driven external integration** — `payment-service` receives Paystack webhooks, verifies every request's HMAC-SHA512 signature before processing, re-verifies the transaction with Paystack's API (never trusting the webhook body alone), then updates the order status and publishes a `payment.succeeded` event — all without any polling or user-initiated confirmation. The webhook handler acknowledges with `200` immediately after signature verification and processes the actual payment update in a background task, since Paystack times out each delivery attempt after 30 seconds and would otherwise re-deliver the same webhook on a slow response.

**7. Saga pattern with reconciliation, not distributed transactions** — a payment confirmation and its corresponding order status update live in two separate databases, so true atomicity across both is not achievable (and 2PC was deliberately rejected as the wrong tool for this scale). Instead: `payment-service` writes its own state first (the durable source of truth for "was this charged"), then synchronously calls `order-service` with retry-with-backoff. If that exhausts all retries, a standalone reconciliation script (`scripts/reconcile_payments.py`) detects and repairs the gap on a cron schedule. This was deliberately tested against a real induced mismatch, not just designed and assumed correct.

**8. Nginx as a unified frontend gateway** — the React SPA makes all API calls to `/api/*` on the same origin (port 3000). nginx routes each prefix to the correct backend service internally. The frontend has no knowledge of the microservice split; from its perspective, it's talking to one API.

**9. Pure-consumer workers for decoupled side effects** — `user-service-worker`, `order-service-worker`, and `notification-service` have no HTTP endpoints of their own. They exist solely to consume events and act on them: creating profiles, advancing order state, and sending emails respectively. This means adding a new consumer (e.g. analytics, SMS) requires zero changes to any publishing service.

```text
                    ┌──────────────────────────────────┐
                    │   frontend (React + nginx)       │
                    │   port 3000                      │
                    │   /api/auth/*     → auth-service │
                    │   /api/users/*    → user-service │
                    │   /api/products/* → product-svc  │
                    │   /api/orders/*   → order-service│
                    │   /api/payments/* → payment-svc  │
                    └──────────────┬───────────────────┘
                                   │ same-origin proxy (no CORS)
                                   ▼
┌──────────────┐   ┌──────────────┐   ┌────────────────────┐   ┌───────────────────┐   ┌──────────────────────┐
│ auth-service │   │ user-service │   │ product-service    │   │  order-service    │   │  payment-service     │
│  (port 8001) │   │  (port 8002) │   │  (port 8003)       │   │  (port 8004)      │   │  (port 8005)         │
│              │   │              │   │                    │   │                   │   │  ← Paystack webhook  │
│ on register: │   │ GET/PATCH    │   │ GET: public        │   │ cart, checkout    │   │  HMAC-SHA512 verify  │
│ publishes    │   │ /users/{id}  │   │ POST/PATCH/DELETE: │   │ sync→product-svc  │   │  re-verify Paystack  │
│ user.regist- │   │ (JWT,        │   │ staff only         │   │ sync→payment-svc  │   │  retry-with-backoff  │
│ ered event   │   │ self-only)   │   │                    │   │                   │   │  background task ack │
└──────┬───────┘   └──────┬───────┘   └──────────┬─────────┘   └────────┬──────────┘   └──────────┬───────────┘
       │                  │                       │                      │                          │
       ▼                  ▼                       ▼                      ▼                          ▼
┌──────────────┐  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────────┐
│auth_service  │  │ user_service_db  │  │ product_service  │  │ order_service_db │  │ payment_service_db   │
│    _db       │  │                  │  │     _db          │  │                  │  │                      │
└──────────────┘  └──────────────────┘  └──────────────────┘  └──────────────────┘  └──────────────────────┘

       │ publishes user.registered               │ publishes order.placed    │ publishes payment.succeeded
       │                                         │                           │ publishes payment.failed
       ▼                                         ▼                           │
┌────────────────────────────────────────────────────────────────────────────┼──────────────────────────────┐
│                               RabbitMQ                                     │                              │
│   exchanges: user_events · order_events · payment_events · shipping_events │                              │
└────┬───────────────────────────────────────────────────────────────────────┘                              │
     │                                                                                                       │
     │ user.registered                          shipment.dispatched                                         │
     ▼                                          shipment.delivered                                          │
┌─────────────────────┐   ┌──────────────────────────────────────┐   ┌──────────────────────────────────────┘
│ user-service-worker │   │   order-service-worker               │   │   shipping-service (port 8006)
│ (aio-pika consumer) │   │   (aio-pika consumer)                │   │   auto-created on payment.succeeded
│ creates UserProfile │   │   shipment.dispatched                │   │   staff: PATCH /{id}/dispatch
│ idempotently        │   │     → order: paid → shipped          │   │         PATCH /{id}/notify-customer
└──────────┬──────────┘   │   shipment.delivery_pending          │   │   customer: GET /order/{id}
           │              │     → order: shipped →               │   │            PATCH /orders/{id}/confirm-delivery
           ▼              │         awaiting_confirmation        │   │   publishes shipment.dispatched
┌──────────────────┐      │   shipment.delivered                 │   │            shipment.delivery_pending
│ user_service_db  │      │     → order: delivered               │   │            shipment.delivered
│ (profile row)    │      └──────────────────────────────────────┘   └──────────────┬───────────────
└──────────────────┘                                                                 │
                                                                                     ▼
                                                                   ┌──────────────────────┐
                                                                   │  shipping_service_db │
                                                                   └──────────────────────┘

     │ payment.succeeded · payment.failed
     │ shipment.dispatched · shipment.delivery_pending · shipment.delivered
     ▼
┌──────────────────────────────────────────────────────────────────────┐
│   notification-service (pure consumer, no HTTP port)                  │
│   fetches recipient email via user-service GET /users/internal/{id}   │
│   payment.succeeded   → "✅ Payment confirmed — order being prepared" │
│   payment.failed      → "❌ Payment failed"                           │
│   shipment.dispatched → "🛵 Your order is on the way!"               │
│   delivery_pending    → "📦 Did you receive your order?"             │
│   idempotency guard — checks notification_service_db before sending   │
└──────────────────────────────────┬───────────────────────────────────┘
                                   │
                                   ▼
                    ┌──────────────────────────┐
                    │  notification_service_db  │
                    │  (audit log of all sends) │
                    └──────────────────────────┘

All 7 databases run on a single host-managed PostgreSQL instance
(outside Docker Compose — containers connect via host.docker.internal)
```

**Why event-driven instead of a direct API call?** A direct call (`auth-service` → `POST user-service/users`) would couple the two services' uptime together — if `user-service` is down or slow, registration breaks too, even though registration itself succeeded. Publishing an event instead means `auth-service` doesn't wait on anyone; `user-service` consumes the event whenever it's able to, and the same event can later be consumed by other services (e.g. a future `notification-service`) without ever touching `auth-service`'s code.

**Why a separate worker container, not a background task inside the API?** Running the consumer as its own process means the API and the event-processing workload can be deployed, restarted, and scaled independently — a slow consumer doesn't affect API latency, and an API redeploy doesn't interrupt event processing.

**At-least-once delivery, handled idempotently.** RabbitMQ can redeliver a message more than once (consumer crash mid-process, network blip). `user-service-worker` doesn't assume each event arrives exactly once — `user_profiles.user_id` has a `UNIQUE` constraint, and a duplicate `user.registered` event is caught and safely ignored rather than creating a duplicate row.

**Why verify JWTs independently instead of calling back to `auth-service`?** A request that had to call `auth-service` to validate every token would reintroduce the exact synchronous coupling the event-driven design was meant to avoid. Every service that needs to verify identity shares `JWT_SECRET` and validates a token's signature and claims locally — no network call, no shared point of failure. Each service also registers a handler for `AuthJWTException` so a missing or invalid token returns a clean `401`/`403` with a real error body, not an unhandled `500`.

**Authorization, not just authentication.** A valid JWT proves *who* the caller is — it doesn't by itself mean they're allowed to do something. `user-service` checks that the authenticated username matches the profile being requested (self-only access, `403` otherwise). `product-service` checks the token's `is_staff` claim before allowing any write, while leaving every read endpoint completely public. Both boundaries have been tested against real failing cases — an unrelated user's token, a missing token, a non-staff token — not just assumed correct by inspection.

**Why a relational catalog (categories → products → variants) instead of one flat table?** A flat `category` string column on `products` means renaming a category is a bulk text update with real risk of inconsistent spelling across rows. A real `categories` table makes renaming, reordering, and deactivating a category a single-row change. Size-based pricing is modeled as its own `product_variants` table (one row per size/price pair) rather than fixed price columns on `products`, so adding a new size or temporarily 86'ing just the "large" of one product doesn't require a schema change. Prices are stored as `Numeric(10,2)`, not `Float` — `Float` introduces real floating-point rounding error for currency values.

**Why synchronous HTTP for checkout price verification and payment, when the rest of the system is event-driven?** This is a deliberate architectural choice, not an inconsistency. The event-driven pattern is correct when a side effect can happen eventually — profile creation, order notifications, payment confirmation emails. Checkout is different: the user is actively waiting for an answer, a stale price could mean charging the wrong amount, and a failed payment must roll back the order immediately. Defaulting to async everywhere regardless of the use case would be as wrong as defaulting to sync everywhere. The system uses each pattern where it fits.

**Why re-verify the Paystack transaction after receiving the webhook, rather than trusting the webhook body?** A webhook endpoint is a public URL — anyone can POST to it. Verifying the HMAC-SHA512 signature proves the request came from Paystack, but the body could still contain stale or replayed data. Re-verifying with Paystack's API (`GET /transaction/verify/{reference}`) confirms the current state of the transaction directly from the source. This is Paystack's documented best practice and prevents a class of attacks where a valid signature is replayed with a modified body.

**Why is the webhook handler's HTTP response decoupled from the actual payment processing?** Paystack times out each webhook delivery attempt after 30 seconds and will consider a slow or non-200 response a failed delivery, retrying the same webhook on a schedule (every 3 minutes for the first 4 tries in live mode, then hourly for 72 hours). If processing took long enough to risk that timeout, Paystack could re-deliver the same webhook while the first delivery was still being processed, causing duplicate work. The handler verifies the signature, returns `200` immediately, then processes the actual update (Paystack re-verification, DB writes, retry-to-order-service, event publishing) in a background task — decoupling acknowledgment from completion.

**Why isn't payment confirmation and order status update a single atomic transaction?** They live in two separate PostgreSQL databases by design (database-per-service), and there is no way to span a single ACID transaction across both. Two-phase commit could theoretically provide that atomicity, but it's fragile in practice — it blocks on coordinator failure and is rarely the right tradeoff for this scale, which is why almost no production microservice system actually uses it. The system instead implements the saga pattern: `payment-service` commits its own state first (the source of truth for "was this actually charged"), then propagates that fact to `order-service` synchronously with retry-with-backoff. If propagation exhausts all retries — `order-service` was down for the entire retry window — a standalone reconciliation script closes the gap. The honest claim here is not "this can never be inconsistent," it's "any inconsistency is always eventually detected and corrected, and the detection mechanism has been tested against a real induced failure, not just assumed to work."

**Why serve the frontend through nginx rather than a development server?** A dev server like Vite's built-in one serves React directly at `localhost:5173` while the backend APIs live at `localhost:8001–8005` — different origins, so every request triggers CORS preflight. nginx as a reverse proxy solves this cleanly: all traffic enters through `localhost:3000`, and the proxy routes `/api/*` to the right backend service based on path prefix. The frontend makes same-origin requests and knows nothing about the microservice topology behind nginx. This also mirrors exactly how a real deployment would be structured — nginx in front of multiple upstream services — so the local dev setup isn't a simplification of production, it is production-shaped.

---

## Services

| Service | Status | Port | Responsibility |
|---|---|---|---|
| `auth-service` | **Done** | `8001` | Registration, strict password validation, email verification (AWS SES), login, JWT issue/refresh, publishes `user.registered` |
| `user-service` | **Done** | `8002` | JWT-protected `GET`/`PATCH /users/{user_id}`, self-only authorization; internal endpoint for service-to-service email lookup |
| `user-service-worker` | **Done** | — | Consumes `user.registered` events, creates profile rows idempotently |
| `product-service` | **Done** | `8003` | Public menu browsing (categories, products, size-based pricing); staff-only create/update/delete |
| `order-service` | **Done** | `8004` | Persistent cart, checkout with live price verification, order lifecycle state machine (`pending_payment → paid → shipped → awaiting_confirmation → delivered`), staff endpoint for all orders |
| `order-service-worker` | **Done** | — | Consumes `shipment.dispatched`, `shipment.delivery_pending`, `shipment.delivered` events, drives order state machine forward |
| `payment-service` | **Done** | `8005` | Paystack initialize+verify flow, HMAC-SHA512 webhook verification, payment audit trail, retry-with-backoff, publishes `payment.succeeded`/`payment.failed` |
| `shipping-service` | **Done** | `8006` | Staff-only shipment dispatch/notify-customer; customer shipment tracking and delivery confirmation; auto-created on `payment.succeeded`; publishes `shipment.dispatched`, `shipment.delivery_pending`, `shipment.delivered` |
| `shipping-service-worker` | **Done** | — | Consumes `payment.succeeded`, auto-creates pending shipment for every paid order |
| `notification-service` | **Done** | — | Consumes payment + shipping events, sends transactional emails via AWS SES (payment confirmed, payment failed, on the way, delivery confirmation request, delivered); idempotency guard prevents duplicate sends |
| `frontend` | **Done** | `3000` | React SPA (Vite + Tailwind) served by nginx; proxies `/api/*` to backend services — no CORS, no hardcoded service URLs; pages: Menu, Cart, Orders, OrderDetail (tracking timeline + confirm delivery), Staff Dashboard, ForgotPassword, ResetPassword |

---

## Tech Stack

- **Framework:** FastAPI (async)
- **Database:** PostgreSQL, accessed via SQLAlchemy (async, `asyncpg` driver)
- **Migrations:** Alembic — run as an explicit, decoupled step, not automatically on container boot (see below)
- **Message broker:** RabbitMQ (topic exchange, durable queues); `aio-pika` for fully async consumers (`order-service-worker`, `notification-service`) to avoid event loop conflicts with asyncpg
- **Auth:** JWT (access + refresh tokens) via `fastapi_jwt_auth2`, verified independently in every service that needs it, via a shared secret
- **Email:** AWS SES (`boto3`) — used for both auth verification emails and transactional order/shipping notifications
- **Payments:** Paystack (initialize + verify flow, HMAC-SHA512 webhook signature verification, NGN test mode, background-task webhook processing, retry-with-backoff for cross-service status propagation, cron-scheduled reconciliation as a saga-pattern backstop)
- **Password hashing:** Werkzeug security helpers
- **Containerization:** Docker + Docker Compose, BuildKit cache mounts for fast rebuilds
- **Webhook tunneling (dev):** ngrok — exposes `payment-service` webhook endpoint to Paystack during local development
- **Frontend:** React 18 (Vite), Tailwind CSS, React Router v6, axios
- **Frontend serving:** nginx (multi-stage Docker build — Node builds the bundle, nginx serves the static files and proxies `/api/*` to backend services)

---

## Local Development Setup

This project simulates a production-like topology. PostgreSQL is host-managed infrastructure, outside Docker Compose entirely — app containers connect out to it. RabbitMQ, by contrast, runs containerized inside Compose, since message brokers are commonly run this way even in real deployments.

### 1. PostgreSQL (host machine, not containerized)

```bash
sudo -u postgres psql -c "CREATE USER microservices WITH PASSWORD '<password>';"
sudo -u postgres psql -c "CREATE DATABASE auth_service_db OWNER microservices;"
sudo -u postgres psql -c "CREATE DATABASE user_service_db OWNER microservices;"
sudo -u postgres psql -c "CREATE DATABASE product_service_db OWNER microservices;"
sudo -u postgres psql -c "CREATE DATABASE order_service_db OWNER microservices;"
sudo -u postgres psql -c "CREATE DATABASE payment_service_db OWNER microservices;"
sudo -u postgres psql -c "CREATE DATABASE shipping_service_db OWNER microservices;"
sudo -u postgres psql -c "CREATE DATABASE notification_service_db OWNER microservices;"
```

`postgresql.conf` needs `listen_addresses = '*'`. `pg_hba.conf` needs a rule allowing the **full Docker private address range**, not just one subnet — Compose creates a different bridge subnet per project, so scope broadly:

```
host    all             all             172.16.0.0/12            scram-sha-256
```

Restart PostgreSQL after changing either file.

### 2. Environment variables

Copy `.env.example` to `.env` (not committed) and fill in real values — Postgres credentials, RabbitMQ credentials, JWT secret, AWS SES credentials and verified sender email, and Paystack test API keys. `JWT_SECRET` must be identical across every service — it's how each one verifies tokens it never issued.

For local webhook testing, expose `payment-service` via ngrok:

```bash
ngrok http 8005
```

Register the resulting `https://` URL as the webhook URL in your Paystack dashboard (Settings → API Keys & Webhooks → Test Webhook URL), appending `/payments/webhook`.

### 3. Run everything

```bash
docker compose up -d --build
```

This starts: RabbitMQ, `auth-service`, `user-service` (API + worker), `product-service`, `order-service`, `order-service-worker`, `payment-service`, `shipping-service`, `notification-service`, and `frontend`.

### 4. Run migrations (explicit step, not automatic)

Migrations are intentionally **not** run on container boot — that pattern breaks down with multiple replicas, since they'd all race to migrate simultaneously on deploy. Run them explicitly, once:

```bash
docker compose exec auth-service         alembic upgrade head
docker compose exec user-service         alembic upgrade head
docker compose exec product-service      alembic upgrade head
docker compose exec order-service        alembic upgrade head
docker compose exec payment-service      alembic upgrade head
docker compose exec shipping-service     alembic upgrade head
docker compose exec notification-service alembic upgrade head
```

Whenever a model changes:

```bash
docker compose exec <service> alembic revision --autogenerate -m "describe the change"
# review the generated file before applying
docker compose exec <service> alembic upgrade head
```

### 5. Verify

```bash
curl http://localhost:8001/docs
curl http://localhost:8002/docs
curl http://localhost:8003/docs
curl http://localhost:8004/docs
curl http://localhost:8005/docs
curl http://localhost:8006/docs
```

Register a user (must be a real, SES-verified address while SES is in sandbox mode), verify via the emailed link, then log in:

```bash
curl -X POST http://localhost:8001/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"you@example.com","password":"TestPass123!"}'

TOKEN=$(curl -s -X POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"TestPass123!"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access'])")
```

Confirm the profile was created on the other side of the event pipeline:

```bash
curl http://localhost:8002/users/<user_id> -H "Authorization: Bearer $TOKEN"
```

Browse the public menu (no token needed):

```bash
curl http://localhost:8003/products
```

To create catalog data, a user needs `is_staff = true` (set manually for now — there's no admin-promotion endpoint yet):

```bash
sudo -u postgres psql -d auth_service_db -c "UPDATE users_auth SET is_staff = true WHERE username = 'testuser';"
# log in again — is_staff is baked into the token at login time
```

The RabbitMQ management UI (`http://localhost:15672`) is useful for watching the event flow live — the **Exchanges → user_events** page shows a publish spike on each registration, and **Queues → user_service.user_registered** shows the consumer picking it up.

### 6. Frontend

```bash
cd frontend
npm install
npm install -D tailwindcss@3 postcss autoprefixer
npm install lucide-react react-router-dom@6 axios
npx tailwindcss init -p
npm run build   # verify it compiles cleanly before Docker
```

Then start the container:

```bash
cd ..
docker compose up -d --build frontend
```

Open `http://localhost:3000` — the full user journey is available: register, verify email, log in, browse the menu, add to cart, check out, pay via Paystack, view order history with live status.

### 7. Reconciliation script (runs on the host, not in Docker)

```bash
cd scripts
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
chmod +x run_reconciliation.sh
```

Dry run (no changes):

```bash
python3 reconcile_payments.py
```

Apply fixes:

```bash
python3 reconcile_payments.py --fix
```

Schedule via cron (`crontab -e`):

```cron
*/10 * * * * /absolute/path/to/pizzasale_api/scripts/run_reconciliation.sh
```

See `scripts/README.md` for full details.

---

## Project Structure

```text
.
├── auth-service/
│   ├── alembic/
│   ├── app/
│   │   ├── api/                # Route handlers
│   │   ├── core/               # Security helpers
│   │   ├── db/                 # Engine/session setup
│   │   ├── models/             # SQLAlchemy models
│   │   ├── schemas/            # Pydantic request/response models, password validation
│   │   ├── services/           # Business logic (register, authenticate, activate)
│   │   └── utils/              # SES email sending, verification tokens, RabbitMQ publisher
│   ├── Dockerfile
│   └── start.sh
├── user-service/
│   ├── alembic/
│   ├── app/
│   │   ├── api/                # GET/PATCH /users/{user_id}; GET /users/internal/{id} (service-to-service)
│   │   ├── core/               # JWT verification config (shared secret with auth-service)
│   │   ├── db/
│   │   ├── models/             # UserProfile (unique user_id constraint)
│   │   ├── schemas/            # Read/partial-update request and response models
│   │   ├── services/           # Profile fetch, partial update, idempotent event-driven creation
│   │   ├── workers/            # RabbitMQ consumer — separate entrypoint from the API
│   │   └── main.py
│   ├── Dockerfile
│   └── start.sh
├── product-service/
│   ├── alembic/
│   ├── app/
│   │   ├── api/                # Category and product routes — public reads, staff-only writes
│   │   ├── core/               # JWT verification, require_staff dependency
│   │   ├── db/
│   │   ├── models/             # Category, Product, ProductVariant (size/price pairs)
│   │   ├── schemas/            # Create/update/response shapes, nested variant validation
│   │   ├── services/           # Category and product CRUD, eager-loaded variant queries
│   │   └── main.py
│   ├── Dockerfile
│   └── start.sh
├── order-service/
│   ├── alembic/
│   ├── app/
│   │   ├── api/                # Cart, checkout, order history, internal status update endpoint
│   │   ├── core/               # JWT verification, user_id extraction
│   │   ├── db/
│   │   ├── models/             # Cart, CartItem, Order, OrderItem; OrderStatus state machine
│   │   ├── schemas/            # Cart and order request/response shapes
│   │   ├── services/           # CartService, OrderService (checkout flow, price locking)
│   │   ├── utils/              # product_client (sync price verify), payment_client, events
│   │   └── workers/            # order-service-worker — consumes shipment.* events (aio-pika)
│   ├── Dockerfile
│   └── start.sh
├── payment-service/
│   ├── alembic/
│   ├── app/
│   │   ├── api/                # POST /payments/initialize, POST /payments/webhook
│   │   ├── db/                 # session.py exposes get_session_factory() for background tasks
│   │   ├── models/             # Payment (audit trail — every charge attempt recorded)
│   │   ├── schemas/            # Initialize request/response shapes
│   │   ├── services/           # PaymentService (initialize, webhook handling, verify)
│   │   └── utils/              # paystack (API client), webhook (HMAC verification),
│   │                           #   events, order_client (retry-with-backoff)
│   ├── Dockerfile
│   └── start.sh
├── shipping-service/
│   ├── alembic/
│   ├── app/
│   │   ├── api/                # POST /shipments, PATCH /{id}/dispatch, PATCH /{id}/deliver,
│   │   │                       #   GET /order/{order_id} (customer track), GET /{id} (staff)
│   │   ├── core/               # JWT verification, require_staff dependency
│   │   ├── db/
│   │   ├── models/             # Shipment (pending → dispatched → delivered state machine)
│   │   ├── schemas/            # Create/dispatch/deliver/response shapes
│   │   ├── services/           # ShipmentService — state transitions with event publishing
│   │   └── utils/              # events (publish shipment.dispatched / shipment.delivered)
│   ├── Dockerfile
│   └── start.sh
├── notification-service/
│   ├── alembic/
│   ├── app/
│   │   ├── db/                 # session.py for notification audit log writes
│   │   ├── models/             # Notification — audit log of every email sent/attempted
│   │   ├── utils/              # ses.py (AWS SES sender), templates.py (HTML + text email bodies)
│   │   └── workers/            # consumer.py — aio-pika async consumer for payment + shipping events
│   └── Dockerfile              # No HTTP server — pure worker, CMD runs consumer directly
├── frontend/
│   ├── src/
│   │   ├── api/                # axios client — all requests to /api/* (nginx proxy)
│   │   ├── components/         # Navbar, ProtectedRoute
│   │   ├── context/            # AuthContext — JWT storage, login/logout, user state
│   │   └── pages/              # Menu, Login, Register, ForgotPassword, ResetPassword,
│   │                           #   Cart, Orders, OrderDetail (tracking timeline + confirm delivery),
│   │                           #   Profile, StaffDashboard
│   ├── nginx.conf              # Serves React SPA; proxies /api/* to backend services
│   └── Dockerfile              # Multi-stage: node:18-alpine builds, nginx:alpine serves
├── scripts/
│   ├── reconcile_payments.py     # saga backstop — detects/fixes payment↔order mismatches
│   ├── run_reconciliation.sh     # cron wrapper — every 10 minutes
│   ├── auto_confirm_delivery.py  # auto-confirms orders stuck in awaiting_confirmation > 2hrs
│   ├── run_auto_confirm.sh       # cron wrapper — every 15 minutes
│   ├── requirements.txt          # httpx, psycopg2-binary (runs on host, not in Docker)
│   ├── logs/                     # not committed — script run history
│   └── README.md                 # setup, manual usage, crontab entries
├── docker-compose.yml
└── .env                        # not committed
```

---

## Roadmap

- [x] `auth-service`: registration, strict password validation, login, JWT issue/refresh
- [x] `auth-service`: real email verification via AWS SES, login gated on verification
- [x] `auth-service`: forgot password / reset password flow via `URLSafeTimedSerializer` tokens (1hr window), AWS SES reset emails
- [x] Event-driven communication: `auth-service` publishes, `user-service-worker` consumes
- [x] Idempotent, at-least-once event consumption (proven under real failure conditions, not just designed for it)
- [x] `user-service`: JWT-protected profile read/update endpoints, self-only authorization (proven against both an unrelated user and a self/target mismatch)
- [x] `user-service`: internal endpoint (`GET /users/internal/{id}`) for service-to-service email lookup without JWT
- [x] `product-service`: relational catalog (categories, products, size-based variants), public reads, staff-only writes (proven against missing-token and non-staff cases)
- [x] `product-service`: `image_url` column on products; Nigerian food menu (19 dishes across 5 categories) with Unsplash images
- [x] Consistent `AuthJWTException` handling across all services — clean `401`/`403` responses instead of unhandled `500`s on missing/invalid tokens
- [x] `order-service`: persistent cart, checkout with live price verification against `product-service`, order state machine (`draft → pending_payment → paid → shipped → awaiting_confirmation → delivered`), `order.placed` event published
- [x] `order-service`: staff-only `GET /orders/all` endpoint returning all users' active orders
- [x] `order-service`: customer `PATCH /orders/{id}/confirm-delivery` endpoint for delivery confirmation
- [x] `payment-service`: Paystack initialize+verify flow (test mode, NGN), HMAC-SHA512 webhook signature verification, transaction re-verification with Paystack API, `payment.succeeded`/`payment.failed` events published, order status updated via internal HTTP call
- [x] `payment-service`: full pytest suite (55 tests) — initialize, webhook security, webhook processing, retry-with-backoff
- [x] Webhook handler returns `200` immediately after signature verification and processes in a background task (Paystack's 30s delivery timeout safety)
- [x] Retry-with-backoff for the payment→order status propagation call, tested against transient failures and network errors
- [x] Reconciliation script (`scripts/reconcile_payments.py`) — detects and repairs payment/order status mismatches; tested against a real induced mismatch, not just designed
- [x] Reconciliation running on a schedule via cron (`scripts/run_reconciliation.sh`) with logging and log rotation
- [x] `shipping-service`: auto-created on `payment.succeeded` by `shipping-service-worker`; staff dispatch/notify-customer; customer tracking; state machine (`pending → dispatched → delivered`); 46 tests (service + route layer)
- [x] `shipping-service`: `PATCH /{id}/notify-customer` — sets order to `awaiting_confirmation`, sends customer confirmation email, auto-confirmed after 2hrs by cron
- [x] `shipping-service-worker`: consumes `payment.succeeded`, auto-creates pending shipment for every paid order
- [x] `order-service-worker`: consumes `shipment.dispatched`, `shipment.delivery_pending`, `shipment.delivered` via aio-pika; drives order state machine idempotently
- [x] `notification-service`: pure-consumer worker (aio-pika) — 5 email types: payment confirmed, payment failed, on the way, delivery confirmation request, delivered; idempotency guard; audit log
- [x] Auto-confirm cron (`scripts/auto_confirm_delivery.py`) — finds orders in `awaiting_confirmation` for >2hrs, marks delivered via order-service API
- [x] UUID casting at route layer — consistent across all services, fixes SQLite test compatibility
- [x] Per-service pytest suites running inside containers (367 tests across 6 services: 78 + 30 + 56 + 62 + 55 + 46 + 40)
- [x] Automated E2E test script covering full user journey across all services including shipping lifecycle and delivery confirmation
- [x] React SPA (Vite + Tailwind) — Glovo-inspired design: dark navy hero, Nigerian orange accent, warm cream background
- [x] Nigerian food menu with real food photos (Unsplash), per-product emoji fallbacks, category pills
- [x] Order tracking timeline (5-step visual progress indicator on order detail page)
- [x] Staff dashboard — all-orders view across all users, dispatch and notify-customer buttons
- [x] Customer delivery confirmation button (`awaiting_confirmation` → `delivered`)
- [x] Forgot password / reset password pages with 1-hour token expiry
- [x] nginx reverse proxy serving the React app and routing `/api/*` to all 6 backend services — same-origin, no CORS
- [ ] API gateway / service-to-service auth
- [ ] SES production access (currently sandbox — verified recipients only)
- [ ] Admin/staff-promotion endpoint (currently `is_staff` is only settable directly in Postgres)
- [ ] Reconciliation alerting — currently a failed fix only logs to stderr; no Slack/PagerDuty integration yet
- [ ] `notification-service` tests — handler unit tests, template tests, idempotency tests
- [ ] Real Nigerian food photos (current Unsplash images are generic approximations)

---

## Why This Project Exists

Built as a hands-on engineering project to practice production-relevant patterns across the full stack: async Python microservices, JWT auth and cross-service token verification, database-per-service architecture, event-driven service communication via RabbitMQ (with both pika and aio-pika, having learned the hard way that blocking consumers and async SQLAlchemy drivers cannot share an event loop), relational data modeling for a real domain, real payment gateway integration (Paystack initialize+verify with webhook signature verification), transactional email notifications (AWS SES via a pure-consumer async worker), containerized local dev that mirrors how a real deployment would be wired, and a React frontend served through an nginx reverse proxy — all connected into one working system rather than isolated demos. Several real production failure modes were deliberately worked through rather than avoided, including Postgres network/auth configuration across shifting Docker subnets, Docker layer-cache and BuildKit tuning, consumer idempotency under genuine message redelivery, an unhandled-exception gap in JWT error handling caught by testing the unhappy path rather than assuming it worked, authorization boundaries verified with actual cross-user and cross-permission requests, the deliberate choice of synchronous vs. asynchronous communication based on the actual requirements of each interaction rather than defaulting to one pattern everywhere, the explicit rejection of distributed-transaction atomicity in favor of a saga pattern with retry-with-backoff and reconciliation (tested against a real induced mismatch), the event loop conflict between pika's blocking connection model and asyncpg that forced a migration to aio-pika for all async consumers, and a delivery confirmation flow designed around real business logic — rider reports delivery, customer gets notified to confirm, 2-hour auto-confirm cron fires if they don't — rather than a simple "mark delivered" button.