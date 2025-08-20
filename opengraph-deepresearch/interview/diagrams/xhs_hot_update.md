flowchart LR
  Dev[Push new JS] --> CI[CI Build & Test]
  CI --> Can[Canary Deploy subset]
  Can -->|ok| Ramp[Increase Traffic]
  Can -->|fail| Rollback[Auto Rollback]
  Ramp --> Prod[Full Deploy]
