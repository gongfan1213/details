flowchart TD
  IN[Request] --> A[AuthN/AuthZ]
  A --> B{Scope OK?}
  B -- no --> X[Reject]
  B -- yes --> C[Input Validation]
  C --> D[Tool Sandbox]
  D --> E[Audit Log]
  E --> F[Response]
