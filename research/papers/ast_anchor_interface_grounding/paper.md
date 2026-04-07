# AST-Anchor Reranking for Interface-Grounded Code Synthesis

## Core Idea

Use AST-level interface grounding as an explicit training-time signal so the model learns to emit the correct top-level API shape before optimizing harder behavioral details.

## Why It Matters

- Many near-miss failures are interface or export-shape failures
- Interface grounding is cheap to compute
- It complements verifier reward without requiring new infrastructure

## Initial Implementation

- Prompt-level interface emphasis
- Mild weight boost for interface-heavy tasks
- Conservative reward boost when syntax and interface are both strong
- Optional use through `--research-methods ast_anchor_interface_grounding`
