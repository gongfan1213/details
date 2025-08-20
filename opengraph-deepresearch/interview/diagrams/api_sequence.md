sequenceDiagram
  autonumber
  participant Client
  participant API as FastAPI /graph
  participant Graph as LangGraph App
  participant Sup as supervisor_node
  participant Align as requirement_alignment_node
  participant Search as content_search_node
  participant Write as content_writing_node
  participant Human as human_confirmation_node

  Client->>API: POST /graph/chat
  API->>Graph: app.invoke(input_state)
  Graph->>Sup: content_supervisor_node
  Sup-->>Graph: Command(goto=requirement_alignment)
  Graph->>Align: requirement_alignment_node
  Align-->>Graph: update(requirement_output)
  alt need human review
    Graph->>Human: interrupt
    Client->>API: POST /graph/resume
    API->>Graph: Command(resume={...})
  end
  Graph->>Search: content_search_node
  Search-->>Graph: update(search_output)
  Graph->>Write: content_writing_node
  Write-->>Graph: update(writing_output)
  Graph-->>API: status=completed
  API-->>Client: SSE/JSON
```
