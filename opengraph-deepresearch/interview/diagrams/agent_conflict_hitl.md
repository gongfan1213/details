flowchart LR
  A[Requirement Alignment] -->|conflict| B{Auto resolve?}
  B -- yes --> C[Re-search & Align]
  C --> A
  B -- no --> H[Human Review interrupt]
  H -->|resume approve| D[Content Search]
  D --> E[Content Writing]
  E --> F[END]
