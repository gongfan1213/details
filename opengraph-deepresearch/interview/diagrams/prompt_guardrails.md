flowchart LR
  U[User Input] --> C[Context Builder]
  C --> P[Prompt Template]
  P --> G{Guardrails}
  G -- injection detected --> D[Refuse + Safety Guidance]
  G -- safe --> L[LLM Inference]
  L --> V{Structured Output Validate}
  V -- pass --> A[Agent/Tool Routing]
  V -- fail --> R[Retry w/ corrected schema]
  A --> T[Tool Call]
  T --> O[Final Output]
