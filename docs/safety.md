# Safety and Threat Model

## Protected assets

- Merchant prices and offer rules
- Product availability
- Customer purchase intent and confirmation
- Order integrity
- Payment-link uniqueness
- Audit history

## Trust boundaries

The customer query, merchant uploads, product descriptions and LLM output are untrusted. Structured database records become authoritative only after validation. The policy engine and workflow state machine are trusted deterministic components.

## Main threats

### Prompt injection in catalogue text

A product description may attempt to override the system, change a price or request an unauthorized tool call. Catalogue text is data, not instruction. The model has no arbitrary execution tool, and prices are read from typed fields.

### Hallucinated products and variants

A plausible response may reference a non-existent item. The backend requires a valid product and variant identifier returned by controlled search.

### Stale price or inventory

Data can change after recommendation. The workflow performs final deterministic revalidation before execution. Production also requires stock reservation and atomic transactions.

### Confirmation bypass

Direct execution calls are rejected unless the workflow is in the confirmed state and its confirmation flag is true.

### Duplicate execution

Network retries may repeat a request. The adapter stores an execution against an idempotency key and returns the same result.

### Excessive discount or order value

The policy engine blocks offers above 50 percent and orders above the configured merchant ceiling.

### Sensitive-data exposure

The MVP requires no card, CVV, UPI PIN or bank-account input. Customer identifiers are absent from the public demo.

## Known limitations

The in-memory adapter is process-local, the public demo has no authentication, and the fake link is not a real payment instrument. These are acceptable constraints for a synthetic internship prototype but not for production.

