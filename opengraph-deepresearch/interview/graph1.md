flowchart TD
  A["START"] --> B["supervisor_node\n(content_supervisor_agent)"]
  B -->|plan or route| C["requirement_alignment_node"]
  C -->|sufficient or max rounds| D["content_search_node"]
  C -->|not enough| C
  D -->|completed| E["content_writing_node"]
  D -->|continue| D
  E -->|completed| F["END"]
  E -->|need human review| H["human_confirmation_node\ninterrupt"]
  H -->|resume: requirement_alignment| C
  H -->|resume: content_search| D
  H -->|resume: content_writing| E
  H -->|resume: END| F