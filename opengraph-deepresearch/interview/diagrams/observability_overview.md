flowchart LR
  A[FastAPI] --> B[Agents/Graph]
  B --> C[Tools]
  C --> D[External APIs]
  A --> E[Tracing]\n(Langfuse/Langsmith)
  A --> F[Metrics /metrics]
  B --> F
  C --> F
  F --> G[Grafana Dashboards]
