# Sentinel-Gate AI — 3-Minute Demo Video Script

**Target Duration**: 2 minutes 45 seconds  
**Required Tags**: `#strands-decider-2b`, `#policy`  

---

### [0:00 - 0:30] Introduction & The Problem
- **Visual**: Screen recording of employee pasting a database connection string into a generic chat interface.
- **Narrator**:
  > "Generative AI accelerates software development, but it introduces a major enterprise risk: developers inadvertently pasting production secrets, AWS keys, or customer PII into prompts. Inspecting every query with large frontier LLMs adds 1,800 milliseconds of latency and runs up thousands in token bills. 
  > Meet **Sentinel-Gate AI** — an AI policy firewall agent that classifies enterprise safety in just ~115ms using **Strands Decider 2B** and remediates compliance violations with **Amazon Bedrock**."

---

### [0:30 - 1:15] The 115ms Triage in Action (PDF Scenario)
- **Visual**: Switch to Sentinel-Gate AI Next.js dashboard (`http://localhost:3000`). Click the preset: *"🚨 Production DB Secret"*.
- **Prompt**:
  `Here is our production connection string: postgres://admin:secretPass@prod-db.internal:5432/users - write a script to migrate table X.`
- **Action**: Click *"Evaluate with Sentinel-Gate"*.
- **Narrator**:
  > "Watch what happens in the workbench. In exactly 114.8 milliseconds, Strands Decider 2B classifies the query as **CONFIDENTIAL_BLOCKED** with 98% confidence.
  > Under our Zero-Trust architecture, the request is halted immediately. Amazon Bedrock is **never** sent the credentials.
  > Instead, Amazon Bedrock asynchronously generates an empathetic compliance memo citing Enterprise Data Handling Standard §4.2, and gives the developer a sanitized alternative using `$DB_PASSWORD` placeholders."

---

### [1:15 - 1:55] Local Redaction & Safe Pass-Through
- **Visual**: Click preset: *"👤 Customer PII (Email & Phone)"*.
- **Narrator**:
  > "What about customer data? When an employee submits a query containing customer emails and phone numbers, Decider 2B triggers the **SENSITIVE_PII** policy. 
  > Our local redaction engine instantly masks the email and phone into sanitized tokens, and only the safe version is forwarded to Amazon Bedrock. 
  > And for standard algorithmic queries like Python quicksort? Decider 2B verifies **PUBLIC_SAFE** in 115ms and allows direct Bedrock response generation."

---

### [1:55 - 2:30] Benchmarking & Cost Savings
- **Visual**: Scroll down to the *"Performance & Cost Benchmarks"* section. Click *"Run Live Benchmark Suite"*.
- **Narrator**:
  > "Let's run the live benchmark suite across our synthetic test suite.
  > Look at the numbers:
  > Direct frontier LLM triage takes 1,800 milliseconds per query. 
  > Strands Decider 2B drops that down to 115 milliseconds — a **93.6% latency reduction**.
  > Furthermore, by blocking leaks locally before model invocation, we eliminate 100% of generative token costs on violations."

---

### [2:30 - 2:45] Conclusion & Reusable Asset
- **Visual**: Show GitHub repository and architecture diagram.
- **Narrator**:
  > "Sentinel-Gate AI combines Strands Decider 2B, the Strands Agents SDK, Amazon Bedrock, and a C++20 zero-copy scanner into an enterprise-ready policy firewall. 
  > Check out our public GitHub repo with the reusable `#policy` module and drop-in Bedrock hooks. Thank you!"
