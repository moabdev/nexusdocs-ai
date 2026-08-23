# NexusDocs AI — RAG Evaluation

This directory contains the evaluation assets used to measure NexusDocs AI instead of relying only on manual chatbot demonstrations.

## Golden dataset

`datasets/golden-dataset.json` is the versioned source of truth for expected RAG behavior.

The initial dataset contains **30 evaluation cases** covering:

- `single_document`
- `semantic`
- `multi_document`
- `temporal_versioning`
- `structured_data`
- `conflicting_information`
- `unanswerable`

## Evaluation case schema

Each case contains:

- `id`: stable evaluation identifier;
- `category`: capability being evaluated;
- `question`: user query;
- `expected_answer`: reference answer used by evaluators;
- `source_documents`: knowledge-base documents expected to support the answer;
- `must_contain`: important facts or terms expected in a correct answer;
- `must_not_contain`: facts that indicate stale, conflicting, or incorrect grounding;
- `answerable`: whether the knowledge base contains sufficient evidence to answer.

## What we will measure

The evaluation pipeline should eventually report retrieval and generation metrics separately.

### Retrieval

Planned metrics include:

- Recall@K
- Hit Rate@K
- Mean Reciprocal Rank (MRR)
- source/document recall
- active-version retrieval accuracy

### Generation

Planned checks include:

- groundedness / faithfulness;
- answer correctness;
- required-fact coverage;
- prohibited-fact violations;
- citation correctness;
- abstention accuracy for unanswerable questions.

## Why retrieval and generation are evaluated separately

A correct final answer can hide poor retrieval, while good retrieval can still be followed by hallucinated generation.

NexusDocs therefore treats the RAG pipeline as multiple measurable stages:

`question -> retrieval -> reranking/context -> generation -> citations`

This allows experiments with chunking, embeddings, metadata filters, hybrid search, reranking, and prompts to be compared objectively.

## Version-aware evaluation

The knowledge base intentionally contains three Shipping Policy versions:

- KB-001 — v1.0 — SUPERSEDED
- KB-002 — v2.0 — SUPERSEDED
- KB-003 — v3.0 — ACTIVE

Several evaluation cases verify that current-policy questions use KB-003 while explicitly historical questions can still retrieve KB-001 or KB-002.

## Unanswerable questions

Some cases intentionally contain questions for which no supporting evidence exists.

The desired behavior is abstention rather than fabrication. The agent should clearly state that the available knowledge base does not contain sufficient information.

## Structured-data evaluation

KB-008 contains deterministic synthetic delivery data generated from a fixed seed. This enables analytical questions with reproducible answers, including regional delay and distribution-center exception analysis.

## Reproducibility

Evaluation datasets, source documents, and synthetic-data generators are version-controlled. Changes to the RAG pipeline should be evaluated against the same golden dataset before performance claims are made.

## Future evolution

The dataset should grow alongside the product. Future versions may add:

- paraphrase suites;
- adversarial queries;
- multilingual questions;
- authorization-sensitive retrieval;
- citation-span evaluation;
- noisy-document tests;
- OCR/document-layout cases;
- regression cases discovered from real failures.

---

The evaluation data is synthetic and exists exclusively for NexusDocs AI development and portfolio demonstration.
