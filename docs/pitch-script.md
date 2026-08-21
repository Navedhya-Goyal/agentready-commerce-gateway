# Five-Minute Pitch Script

## 0:00–0:30 — Hook

AI can recommend a product in seconds, but a confident recommendation is not necessarily a valid transaction. A merchant catalogue may contain an old price, unavailable stock, an expired offer or even malicious text. If an AI agent acts on that information without controls, agentic commerce becomes agentic error.

## 0:30–1:10 — Problem

Payments are only the last step. Before a customer can safely pay, the merchant must verify the product, variant, price, inventory, delivery, policies and customer approval. Smaller merchants often store those facts across spreadsheets and disconnected tools. AgentReady is the merchant trust layer between AI shopping intent and payment execution.

## 1:10–1:50 — Solution

AgentReady turns merchant data into a governed commerce manifest. An intent agent understands the customer request, controlled search finds real products, deterministic rules validate the transaction, and the workflow stops for confirmation before execution. The model never calculates money and never creates an unrestricted payment.

## 1:50–3:20 — Live demo

The dashboard openly labels all data synthetic. The catalogue screen identifies invalid prices, negative inventory, duplicate SKUs, expired offers and malicious product text. Products with serious failures are excluded from the manifest.

I will request black running shoes, size 9, below three thousand rupees, delivered to Bengaluru. AgentReady extracts only those explicit constraints and retrieves a real catalogue product. After selection, the policy engine calculates the order and validates the offer, stock and delivery. The execution button is still unavailable.

I confirm the simulated order. Only now can the workflow perform a final validation and create an idempotent fake payment link. The audit screen records every transition.

Now I will request red shoes in size 12 below five hundred rupees. Nothing matches, so AgentReady refuses. It does not invent a product merely to produce a pleasant answer.

## 3:20–4:00 — Engineering

FastAPI exposes the backend, the frontend has no build dependency, and the core is divided into intent, catalogue, policy, workflow and payment-adapter services. Deterministic demo mode runs without a key; optional LLM mode uses schema-constrained output. The tests verify confirmation, policy and idempotency failures.

## 4:00–4:30 — Business impact

AgentReady is designed to reduce merchant integration effort, increase catalogue readiness and prevent invalid AI-generated orders. I do not claim real conversion improvement because the data and outcomes are synthetic. The measurable prototype outcomes are safety and correctness.

## 4:30–5:00 — Closing

The core lesson is that an LLM is not a payment authority. Credible agentic commerce needs grounded product truth, bounded permissions, explicit consent, deterministic financial logic, idempotent execution and auditability. AgentReady demonstrates that complete control path.

