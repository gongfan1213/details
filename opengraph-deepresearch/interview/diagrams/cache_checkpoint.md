flowchart LR
  User --> API
  API --> L1[In-Memory Cache]
  L1 -->|miss| L2[Redis Cache]
  L2 -->|miss| L3[Vector Store]
  L3 --> Tools
  Tools --> L2
  subgraph Graph Checkpoint
    CP[(State Snapshot)]
  end
  API --> CP
  CP --> API
