const state = { session: null, analysis: null };
const $ = (selector) => document.querySelector(selector);
const money = (value) => new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 }).format(value);

async function api(path, options = {}) {
  const response = await fetch(path, { headers: { "Content-Type": "application/json" }, ...options });
  const payload = await response.json();
  if (!response.ok) throw new Error(payload.detail || "Request failed");
  return payload;
}

async function loadAnalysis() {
  state.analysis = await api("/api/catalogue/analysis");
  $("#readiness-score").textContent = `${state.analysis.readiness_score}%`;
  $("#ready-products").textContent = state.analysis.ready_products;
  $("#blocked-products").textContent = state.analysis.blocked_products;
  $("#issue-count").textContent = state.analysis.issues.length;
  const issues = state.analysis.issues;
  $("#issues-list").innerHTML = issues.map(issue => `<div class="issue-row"><span class="severity ${issue.severity}">${issue.severity}</span><strong>${issue.code.replaceAll("_", " ")}</strong><span>${issue.message} <small>(${issue.product_id})</small></span></div>`).join("");
  const counts = issues.reduce((acc, issue) => ({ ...acc, [issue.severity]: (acc[issue.severity] || 0) + 1 }), {});
  $("#severity-summary").innerHTML = ["critical", "high", "medium", "low"].map(level => `<div class="severity-line"><span class="severity ${level}">${level}</span><strong>${counts[level] || 0}</strong></div>`).join("");
}

function renderSession(session) {
  state.session = session;
  $("#workflow-state").textContent = session.state.replaceAll("_", " ");
  $("#intent-output").classList.remove("empty");
  const intent = session.intent;
  const tags = [
    `Terms: ${intent.product_terms.join(", ") || "not specified"}`,
    `Colour: ${intent.color || "any"}`,
    `Size: ${intent.size || "any"}`,
    `Budget: ${intent.max_price_inr ? money(intent.max_price_inr) : "any"}`,
    `City: ${intent.city || "any"}`,
    `Quantity: ${intent.quantity}`
  ];
  $("#intent-output").innerHTML = `<div class="intent-tags">${tags.map(tag => `<span>${tag}</span>`).join("")}</div>`;
  $("#product-results").innerHTML = session.matches.map(product => `<div class="product-card"><div><h3>${product.name}</h3><p>${product.color} · size ${product.size} · ${product.stock} in stock · ${product.return_days}-day returns</p></div><div><div class="price">${money(product.price_inr)}<small>${product.offer_percent ? `${product.offer_percent}% eligible offer` : "No offer"}</small></div><button class="button secondary select-product" data-product-id="${product.product_id}">Select</button></div></div>`).join("");
  document.querySelectorAll(".select-product").forEach(button => button.addEventListener("click", () => selectProduct(button.dataset.productId)));
  if (session.policy_decision) renderOrderSummary(session);
  renderAudit(session.audit);
  if (session.state === "rejected" && !session.matches.length) {
    $("#product-results").innerHTML = `<div class="notice">No approved catalogue product satisfies every constraint. AgentReady refused to invent an alternative.</div>`;
  }
}

async function selectProduct(productId) {
  try {
    const session = await api(`/api/commerce/${state.session.session_id}/select`, { method: "POST", body: JSON.stringify({ product_id: productId }) });
    renderSession(session);
  } catch (error) { $("#search-error").textContent = error.message; }
}

function renderOrderSummary(session) {
  const decision = session.policy_decision;
  const product = session.matches.find(item => item.product_id === session.selected_product_id);
  $("#order-summary").classList.remove("hidden");
  $("#order-summary").innerHTML = `<h3>${product.name}</h3><div class="summary-line"><span>Subtotal</span><strong>${money(decision.subtotal_inr)}</strong></div><div class="summary-line"><span>Approved discount</span><strong>− ${money(decision.discount_inr)}</strong></div><div class="summary-line"><span>Delivery</span><strong>${money(decision.delivery_inr)}</strong></div><div class="summary-line total"><span>Total</span><strong>${money(decision.total_inr)}</strong></div>${decision.reasons.length ? `<p class="error-message">${decision.reasons.join(" ")}</p>` : ""}`;
  if (session.state === "awaiting_confirmation") {
    $("#execution-actions").innerHTML = `<button id="review-confirmation" class="button primary">Review and confirm</button>`;
    $("#review-confirmation").addEventListener("click", () => openConfirmation(decision.total_inr));
  } else if (session.state === "confirmed") {
    $("#execution-actions").innerHTML = `<button id="execute-order" class="button primary">Create simulated payment link</button>`;
    $("#execute-order").addEventListener("click", executeOrder);
  } else if (session.state === "payment_link_created") {
    $("#execution-actions").innerHTML = `<span class="status-pill">${session.order_id}</span><button class="button secondary" disabled>Simulated link created</button>`;
  }
}

function openConfirmation(total) {
  $("#confirmation-copy").textContent = `Confirm the simulated order total of ${money(total)}. This does not move money or contact a customer.`;
  $("#confirmation-dialog").showModal();
}

async function confirmOrder() {
  const session = await api(`/api/commerce/${state.session.session_id}/confirm`, { method: "POST", body: JSON.stringify({ confirmed: true }) });
  renderSession(session);
}

async function executeOrder() {
  const session = await api(`/api/commerce/${state.session.session_id}/execute`, { method: "POST", body: "{}" });
  renderSession(session);
}

function renderAudit(events) {
  $("#audit-timeline").innerHTML = events.map(event => `<div class="timeline-event"><strong>${event.event_type.replaceAll("_", " ")}</strong><span>${event.detail}</span></div>`).join("");
}

async function startSearch() {
  $("#search-error").textContent = "";
  $("#order-summary").classList.add("hidden");
  $("#execution-actions").innerHTML = "";
  try {
    const session = await api("/api/commerce/search", { method: "POST", body: JSON.stringify({ query: $("#query-input").value }) });
    renderSession(session);
  } catch (error) { $("#search-error").textContent = error.message; }
}

document.querySelectorAll(".nav-item").forEach(button => button.addEventListener("click", () => {
  document.querySelectorAll(".nav-item,.page-section").forEach(element => element.classList.remove("active"));
  button.classList.add("active");
  $(`#${button.dataset.section}`).classList.add("active");
  $("#page-title").textContent = button.textContent;
}));
document.querySelectorAll(".example-chip").forEach(button => button.addEventListener("click", () => { $("#query-input").value = button.textContent; }));
$("#search-button").addEventListener("click", startSearch);
$("#refresh-button").addEventListener("click", loadAnalysis);
$("#manifest-button").addEventListener("click", async () => {
  const panel = $("#manifest-output");
  if (panel.classList.contains("hidden")) panel.textContent = JSON.stringify(await api("/api/catalogue/manifest"), null, 2);
  panel.classList.toggle("hidden");
});
$("#confirmation-dialog").addEventListener("close", event => { if (event.target.returnValue === "confirm") confirmOrder(); });
loadAnalysis().catch(error => { $("#search-error").textContent = error.message; });

