# Architecture and Engineering Decisions

## System boundary

AgentReady begins when a merchant supplies catalogue and policy information. It ends after returning a simulated hosted payment-link identifier. Authentication and payment processing remain outside the prototype.

## Components

### Catalogue quality gate

The quality gate checks product identity, SKU uniqueness, price validity, inventory, variants, delivery coverage, return windows, offer limits and expiry. Critical and high-severity failures block a product from the generated commerce manifest.

### Commerce manifest

The manifest is a versioned snapshot containing only approved product records and transaction policies. A production implementation would cryptographically sign it and give it a strict time-to-live.

### Intent provider

The provider transforms natural language into explicit fields. The deterministic implementation makes the demo reproducible. The optional OpenAI implementation uses Structured Outputs. Both return the same domain object and have no payment capability.

### Controlled catalogue search

Retrieval uses structured product records. Product recommendations are never accepted unless they carry a valid product identifier returned by the search service.

### Policy engine

The policy engine performs all transaction-sensitive operations. It checks active status, price, quantity, stock, delivery, order ceiling, offer percentage and offer expiry. It calculates subtotal, discount, delivery and total using integers representing INR.

### Commerce workflow

The workflow permits only explicit state transitions. Product selection can occur only after search. Confirmation can occur only after validation. Execution can occur only after explicit confirmation. A repeated action cannot silently create a second order.

### Simulated Razorpay adapter

The adapter has an intentionally narrow contract: receive a validated amount and idempotency key, then return a fake order ID and `example.invalid` link. It does not transmit customer data or money.

## Why a database would replace memory in production

The MVP uses an in-memory session store to remain simple. Production requires PostgreSQL transactions and row locks so state survives process restarts and concurrent requests cannot oversell inventory.

## Why no vector database

The transaction-critical constraints are structured. A semantic index may improve discovery for subjective requests, but it cannot be authoritative for price, stock, size or delivery. A future hybrid search layer could retrieve candidates semantically and then apply the same deterministic filters.

