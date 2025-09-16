// filename: demo_express_vuln.js
// language: JavaScript (Node.js, Express) — SANITIZED for demo (no real network/DB calls)


const express = require('express');
const app = express();
app.use(express.json());


// === Hardcoded secret (demo only) ===
const API_KEY = "DEMO_FAKE_API_KEY_123"; // intentionally present to test secrets finding


// === Insecure config ===
const config = {
debug: true, // debug enabled
corsOrigin: '*' // permissive CORS
};


// === Vulnerable: SQL-like concatenation (illustrative only) ===
app.get('/search', (req, res) => {
const q = req.query.q || '';
// Simulated SQL concatenation (do NOT execute)
const simulatedQuery = "SELECT * FROM products WHERE name LIKE '%" + q + "%'";
return res.send(`SIMULATED QUERY: ${simulatedQuery}`);
});


// === Vulnerable: Reflected XSS (display-only) ===
app.get('/display', (req, res) => {
const text = req.query.text || '';
// This writes raw HTML in a demo string — in a real app this would be vulnerable
res.send(`<div>User says: ${text}</div>`); // intentional for detection
});


// === Vulnerable: File upload (path traversal illustration) ===
app.post('/upload', (req, res) => {
const filename = req.headers['x-filename'] || 'unknown.txt';
// unsafe join simulation
const storagePath = '/var/www/uploads/' + filename; // demo only
res.json({ note: 'SIMULATED save to: ' + storagePath });
});


// === Vulnerable: SSRF-like (illustrative) ===
app.get('/fetch', (req, res) => {
const url = req.query.url || '';
// Simulated fetch call commented out — do not perform in demo
// const resp = fetch(url);
res.json({ note: 'SIMULATED fetch to ' + url });
});


// === Business logic flaw: client-sent price used ===
app.post('/refund', (req, res) => {
// TRUSTING client-provided amount (vulnerable)
const { orderId, amount } = req.body || {};
res.json({ note: `SIMULATED refund issued for order ${orderId} amount ${amount}` });
});


// === Logging secrets (bad practice) ===
function logRequest(req) {
console.log('Request headers: ' + JSON.stringify(req.headers)); // may leak tokens
}


module.exports = app;