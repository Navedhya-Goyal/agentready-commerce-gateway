# Synthetic Data Dictionary

## Product identity

- `product_id` is the internal immutable identifier.
- `sku` is the merchant-facing stock-keeping unit and must be unique.
- `name` is the customer-facing name.
- `category` supports controlled product retrieval.
- `description` is untrusted explanatory text.

## Commerce fields

- `price_inr` is stored as an integer INR amount in the MVP.
- `stock` is the current available unit count.
- `color` and `size` are structured variant attributes.
- `delivery_cities` is an allow-list of supported normalized cities.
- `return_days` is the disclosed return window.
- `active` controls catalogue eligibility.
- `offer_percent` is the potential discount percentage.
- `offer_expires_at` is an ISO 8601 timestamp.

## Workflow fields

- `session_id` identifies one customer commerce workflow.
- `state` records the current allowed workflow state.
- `selected_product_id` links the proposal to catalogue truth.
- `customer_confirmed` is the explicit human-in-the-loop gate.
- `order_id` and `payment_link` are simulated identifiers.
- `audit` contains timestamped state-transition evidence.

