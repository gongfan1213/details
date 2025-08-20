flowchart TD
  A[Agent calls Tool] --> B[IToolExecutor Decorator]
  B --> C{Auth/Quota}
  C -->|ok| D[Param Sanitize]
  C -->|deny| X[Reject]
  D --> E[Timeout/Retry/Backoff]
  E --> F[Call API]
  F --> G[Metrics + Audit]
  G --> H[Return]
