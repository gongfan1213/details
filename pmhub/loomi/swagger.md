好的。我给出两部分输出：
- Swagger 级别的接口参数说明表（精简、可直接映射到 OpenAPI）
- 数据库 ER 图（Mermaid 可视化）

### 接口参数说明（Swagger 风格）

- 核心多智能体图（v1）`/graph`
  - POST `/graph/chat`
    - 入参Body:
      - user_id string 必填
      - session_id string 必填
      - query string 必填 长度1-2000
      - file_ids string[] 可选
      - enable_human_review boolean 可选 默认false
    - 返回:
      - status string: completed|interrupted|partial|error
      - thread_id string
      - current_stage string 可空
      - stages [{stage,status,events_count,processed_at?}] 可空
      - final_output object 可空
      - message string 可空
      - interrupt_reason string 可空
  - POST `/graph/chat/stream` (SSE)
    - 入参Body: 同上
    - 事件类型:
      - graph_start, stage_summary, final_result, interrupt, graph_end, error
  - POST `/graph/resume`
    - 入参Body:
      - user_id string 必填
      - session_id string 必填
      - approved boolean 必填
      - feedback string 可选
      - action string 可选: approve|reject|modify
      - additional_instructions string 可选
    - 返回: 同 `/graph/chat`
  - POST `/graph/status`
    - 入参Body:
      - user_id string 必填
      - session_id string 必填
    - 返回:
      - success boolean
      - data.thread_id string
      - data.current_stage string
      - data.need_human_review boolean
      - data.has_checkpoint boolean
      - data.last_updated string (ISO) 可空
      - data.stages_completed {alignment,research,writing} (boolean) 或 “流程尚未开始”
  - GET `/graph/health`
    - 返回: status, service, timestamp, graph_compiled, checkpoint_type(memory|redis)
  - POST `/graph/test/simple`
    - 返回: {success, data, message}

- 内容创作图（v2）`/graph_v2`
  - POST `/graph_v2/chat/stream` (SSE)
    - 入参Body:
      - user_id string 必填
      - session_id string 必填
      - query string 必填
      - file_ids string[] 可选
      - enable_human_review boolean 可选
    - 事件类型:
      - graph_start, system(graph_trace), stage_change, node_execution, node_event, final_result, graph_end, error
    - 备注: 会从现有 state 读取历史消息并追加

- 断网恢复/混合流 `/api/loomi`
  - POST `/api/loomi/heartbeat`
    - 入参Body:
      - user_id string 必填
      - session_id string 必填
    - 返回: {success, timestamp, message|error}
  - GET `/api/loomi/stream/{user_id}/{session_id}` (SSE)
    - 智能模式:
      - 无需回放: 输出 no_replay 后 [DONE]
      - 纯回放: replay_start → 逐条事件 → replay_complete → [DONE]
      - 混合（回放+实时）: hybrid_start(replay) → 回放 → hybrid_transition(realtime) → 实时事件 → task_complete/timeout_stop → [DONE]
      - 纯实时: realtime_start → 实时事件 → task_complete/timeout_stop → [DONE]
    - 事件字段:
      - event_type, agent_source, timestamp, payload{id, content_type, data, metadata{is_replay,is_realtime,hybrid_phase?,replay_progress?,is_after_disconnect?}}
  - GET `/api/loomi/debug/status/{session_id}`
    - 返回: {success, session_id, recovery_info, timestamp}
  - GET `/api/loomi/debug/disconnect/{session_id}`
    - 返回: {success, total_events, disconnect_events, disconnect_percentage, events[], timestamp}
  - GET `/api/loomi/debug/completion/{session_id}`
    - 返回: {success, completion_diagnosis, task_status, timestamp}

- 鉴权/限流
  - `apis/app.py` 中间件对白名单接口校验 Supabase Token，基于用户ID做 Redis 限流，返回 `X-RateLimit-*` 响应头。

### 数据库表结构与关键索引（摘要）

- contexts
  - 列: id(uuid, PK), user_id(text), session_id(text), action(text), context_data(jsonb), metadata(jsonb), created_at(timestamptz), updated_at(timestamptz)
  - 唯一: (user_id, session_id)
  - 索引: (user_id, session_id), action, user_id, session_id, created_at, updated_at, (user_id, action), GIN(context_data)
  - RLS: 用户隔离策略 + service_role 全量策略

- notes
  - 列: id(uuid, PK), user_id(text), session_id(text), action(text), name(text), title(text?), context(text), select_status(int 0/1), metadata(jsonb), created_at, updated_at
  - 唯一: (user_id, session_id, name)
  - 检查: select_status IN (0,1)
  - 索引: (user_id, session_id), action, user_id, session_id, name, select_status, created_at, updated_at, (user_id, action), (user_id, name), (session_id, action), (action, select_status), 全文(context), GIN(metadata)
  - RLS: 用户隔离策略 + service_role 全量策略

- loomi_stream_events
  - 列: id(bigserial, PK), session_id(varchar64), user_id(varchar64), event_type(varchar32), content_type(varchar64), agent_source(varchar64), event_data(jsonb), event_metadata(jsonb), created_at(timestamptz default now), is_replayed(bool), user_last_seen(timestamptz), is_after_disconnect(bool), is_session_complete(bool), task_phase(varchar32)
  - 索引: (session_id, created_at), (session_id, is_replayed, is_after_disconnect), user_id, session_id, event_type, content_type, agent_source, created_at, is_replayed, is_after_disconnect, (user_id, session_id), (user_id, created_at), (session_id, created_at), GIN(event_data), GIN(event_metadata)
  - 触发器: 插入时更新 user_last_seen
  - RLS: 用户隔离策略 + service_role 全量策略

- uploaded_files
  - 列: id(uuid, PK), file_id(text UNIQUE), user_id(text), session_id(text), original_filename(text), file_type(text), file_size(bigint), mime_type(text?), description(text?), upload_mode(text in ai_parse|storage_only), oss_url(text), oss_object_name(text), oss_bucket_name(text), gemini_file_uri(text?), gemini_file_name(text?), processing_status(text), metadata(jsonb), created_at, updated_at
  - 索引: user_id, session_id, (user_id, session_id), file_id, upload_mode, created_at, processing_status
  - RLS: 用户隔离策略 + service_role 全量策略

- Supabase auth.users（外部）
  - 通过 RPC 读取：`search_users_with_auth`、`get_auth_user_by_id`、`check_auth_user_exists`、`get_daily_new_users_count`、`get_user_retention_count`

### ER 图（Mermaid）

```mermaid
erDiagram
  USERS ||--o{ CONTEXTS : "by user_id"
  USERS ||--o{ NOTES : "by user_id"
  USERS ||--o{ LOOMI_STREAM_EVENTS : "by user_id"
  USERS ||--o{ UPLOADED_FILES : "by user_id"

  SESSIONS {
    string session_id PK
  }
  SESSIONS ||--o{ CONTEXTS : "by session_id"
  SESSIONS ||--o{ NOTES : "by session_id"
  SESSIONS ||--o{ LOOMI_STREAM_EVENTS : "by session_id"
  SESSIONS ||--o{ UPLOADED_FILES : "by session_id"

  USERS {
    uuid id PK
    text email
    timestamptz created_at
  }

  CONTEXTS {
    uuid id PK
    text user_id
    text session_id
    text action
    jsonb context_data
    jsonb metadata
    timestamptz created_at
    timestamptz updated_at
    unique (user_id, session_id)
  }

  NOTES {
    uuid id PK
    text user_id
    text session_id
    text action
    text name
    text title
    text context
    int select_status
    jsonb metadata
    timestamptz created_at
    timestamptz updated_at
    unique (user_id, session_id, name)
  }

  LOOMI_STREAM_EVENTS {
    bigint id PK
    varchar session_id
    varchar user_id
    varchar event_type
    varchar content_type
    varchar agent_source
    jsonb event_data
    jsonb event_metadata
    timestamptz created_at
    timestamptz user_last_seen
    bool is_replayed
    bool is_after_disconnect
    bool is_session_complete
    varchar task_phase
  }

  UPLOADED_FILES {
    uuid id PK
    text file_id UNIQUE
    text user_id
    text session_id
    text original_filename
    text file_type
    bigint file_size
    text mime_type
    text description
    text upload_mode
    text oss_url
    text oss_object_name
    text oss_bucket_name
    text gemini_file_uri
    text gemini_file_name
    text processing_status
    jsonb metadata
    timestamptz created_at
    timestamptz updated_at
  }
```

### 补充说明
- API 与表的映射
  - `/graph*` 与 `/graph_v2*` 主要围绕运行状态，事件会写入 `loomi_stream_events`，中间状态可持久在 `contexts`，中间产物/分析在 `notes`。
  - `/api/loomi/*` 用于断网回放与实时流切换，严格依赖 `loomi_stream_events` 的 `is_replayed`、`user_last_seen`、`is_after_disconnect`、`is_session_complete`。
  - 文件上传（若前端接入）对应 `uploaded_files`。

需要我把这些表/接口转换成 OpenAPI 3.1 的 `yaml` 文件（可直接导入 Swagger UI）或导出成 `.md` 文档吗？我也可以补充各接口的示例请求/响应。
