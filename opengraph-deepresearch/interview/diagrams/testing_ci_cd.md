flowchart TD
  C[Commit/PR] --> CI[CI Pipeline]
  CI --> U[Unit Tests]
  CI --> I[Integration/E2E]
  CI --> P[Prompt/Eval Suite]
  CI --> L[Load/Stress]
  U --> R1{Gates}
  I --> R1
  P --> R1
  L --> R1
  R1 -- pass --> DEP[Deploy]
  R1 -- fail --> BLK[Block + Report]
