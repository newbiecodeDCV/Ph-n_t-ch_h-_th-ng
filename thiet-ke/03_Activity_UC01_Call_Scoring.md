# Activity Diagram – UC01 Call Scoring (Re-Spec)

Luồng hoạt động chi tiết, tách khỏi CRM compliance. Có áp dụng context-aware rules.

```mermaid
flowchart TD
  subgraph Ingest
    A[Nhận audio + metadata từ PBX]
    B[Call Type (đã có từ UC03)]
  end

  subgraph STT
    C[ASR + Diarization]
  end

  C --> C1[Detect Call Type (audio-only)\n(call_type_pred, confidence)]

  subgraph Analysis
    D[Extract Features\n(wpm, pause, interrupts, sentiment)]
    E[Detect Evidence\n(segments, keywords)]
  end

  subgraph Scoring
    F[Evaluate KNGT]
    G[Evaluate KNBH/KNSV]
    H[Context-aware Adjustments]
    I[Aggregate to 0-10]
  end

  subgraph Post
    J[Generate Summary\n(3-5 câu)]
    K[Build Recommendations]
    L[Map Suggested Scripts]
    M[Persist Score + Evidence + Summary]
    N[Deliver Report to UI]
  end

  A --> C --> C1 --> D --> F
  B --> F
  D --> G
  E --> F
  E --> G
  F --> H
  G --> H --> I --> J --> K --> L --> M --> N

  C -- quality_low --> Q[Flag hạn chế penalize]
  H -- context_ok --> R[Không phạt]
```
