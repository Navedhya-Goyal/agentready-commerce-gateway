# Razorpay Application Form Copy

## Selected track

Track 1: AI Growth & Agentic Commerce

## Project title

AgentReady: Merchant Trust and Transaction Gateway for Agentic Commerce

## Project objectives

AgentReady is a merchant-side trust and transaction-governance platform designed to help businesses participate safely in AI-led commerce. It solves the problem that merchant product, price, inventory, delivery, offer and policy data is frequently fragmented across spreadsheets and disconnected systems. An AI shopping agent acting on incomplete or stale information could recommend an unavailable product, quote an incorrect price, apply an invalid discount or create a duplicate and unauthorized order.

The platform validates merchant catalogue data and generates a machine-readable commerce manifest containing only approved products. It then converts a customer's natural-language request into structured constraints and searches the controlled catalogue. Every recommendation must reference a valid product identifier. A deterministic policy engine revalidates price, inventory, delivery, offer eligibility, quantity and order limits. The customer must explicitly confirm the proposal before the system creates an idempotent simulated order and payment link.

The project separates probabilistic AI reasoning from transaction authority. The AI layer understands intent and explains recommendations. Deterministic code performs product retrieval, monetary calculations, policy enforcement and execution controls. The MVP uses synthetic data and a simulated Razorpay adapter; it does not claim access to Razorpay production data or private APIs.

The prototype is evaluated through catalogue issue detection, grounded retrieval, unsupported-product refusal, policy blocking, confirmation enforcement and duplicate-action prevention. Its intended impact is to reduce the effort required for merchants to become ready for AI-commerce channels while preserving merchant control, customer consent and payment safety.

## Build challenges and technical obstacles

The first challenge was establishing a reliable boundary between natural-language interpretation and transactional truth. I addressed this by allowing the intent agent to extract only explicit constraints while forcing products, prices, inventory and offers to come from structured records and deterministic functions.

The fallback intent parser initially mistook the letter "s" in the word "shoes" for a product size. The automated tests caught the issue. I changed the parser so a size is accepted only when the customer explicitly uses a size label. A second test found that the parser converted ₹3,000 into 3 because it replaced the comma with a space. I corrected the normalization so digit-grouping separators are removed without changing the numeric value. These failures reinforced why transaction-oriented parsers require adversarial tests rather than visual inspection alone.

Catalogue data created a separate challenge because it can contain invalid prices, negative inventory, duplicate SKUs, expired offers and malicious instructions inside descriptions. I created a quality gate that classifies these failures and excludes critical or high-risk products from the generated commerce manifest. Catalogue descriptions remain untrusted and cannot override structured price or policy fields.

Workflow reliability was addressed with explicit states for request, product match, policy validation, confirmation and execution. Direct execution before confirmation returns an error. An idempotency key ensures that a retried request returns the existing simulated order instead of creating a duplicate.

Because the project has no access to confidential Razorpay merchant data, I created a reproducible synthetic-data generator containing 500 products and deliberately planted anomalies. The payment layer is a simulated adapter returning an `example.invalid` link, making it impossible to confuse the demo with a real payment integration.

The final test suite contains sixteen passing tests covering intent extraction, catalogue validation, controlled retrieval, policy enforcement, confirmation bypass, impossible-product refusal, workflow completion and duplicate-action prevention. Linting and an end-to-end API integration test also pass.

