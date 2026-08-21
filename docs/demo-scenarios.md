# Demonstration Scenarios

## Successful grounded purchase

Use: `Find me black running shoes in size 9 under ₹3,000 for delivery to Bengaluru`.

Expected result: the request maps to the synthetic AeroStride product. The valid ten-percent offer is applied by the policy engine. The system waits for confirmation before exposing the execution control.

## Honest refusal

Use: `Red running shoes size 12 below ₹500 in Delhi`.

Expected result: no approved product matches. The workflow enters the rejected state and does not create a substitute.

## Catalogue attack

Open catalogue readiness and inspect `prd_bad_001`. Its description contains a malicious instruction, its price and stock are negative, its offer is unsafe and expired, and it shares a duplicate SKU. The product is absent from the commerce manifest.

## Duplicate execution

Run the workflow tests. The simulated adapter receives the same idempotency key twice and returns the existing order identifier on the second request.

