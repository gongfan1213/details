flowchart TD
  subgraph Registry
    D[Tool Catalog]
    P[Policy Center]
  end
  L[Loader]
  A[Agent]
  U[Users/Tenants]
  D --> L
  P --> L
  L --> A
  U -->|quota/visibility| P
  A --> M[Metrics]
  M --> G[Dashboards]
