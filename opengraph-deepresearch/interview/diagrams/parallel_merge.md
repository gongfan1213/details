flowchart TD
  subgraph Parallel Branches
    R[Content Search] -- evidence --> J[Join]
    W[Draft Writer] -- draft --> J
  end
  J -->|merge & resolve| OUT[Final Output]
  J -->|conflict high| R
