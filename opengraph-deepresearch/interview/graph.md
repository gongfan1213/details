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

  Client->>API: POST /graph/chat (user_id, session_id, query)
  API->>Graph: app.invoke(input_state)
  Graph->>Sup: content_supervisor_node(state)
  Sup-->>Graph: Command(goto=requirement_alignment)
  Graph->>Align: requirement_alignment_node(state)
  Align-->>Graph: state.update(requirement_output)
  alt need human review
    Graph->>Human: interrupt(state)
    Note over Graph,Human: 流程暂停等待人工审核
    Client->>API: POST /graph/resume (approved/feedback)
    API->>Graph: Command(resume={...})
  end
  Graph->>Search: content_search_node(state)
  Search-->>Graph: state.update(search_output)
  Graph->>Write: content_writing_node(state)
  Write-->>Graph: state.update(writing_output)
  Graph-->>API: status=completed, final_output
  API-->>Client: SSE/JSON 响应