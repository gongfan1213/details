### 11 检查点与恢复进阶面试题（Checkpoint & Recovery Advanced）

- 关注点：序列化/反序列化、索引/扫描策略、部分恢复、重复副作用治理、跨实例一致性
- 关键参考：`agents/graph/redis_checkpoint.py`, `apis/graph_routes*.py`

#### 基础题
- 为什么采用 Redis 实现检查点？相对内存方案的优劣与适用场景？
- `WRITES_IDX_MAP` 的作用是什么？为什么需要对中间写入分配稳定索引？

#### 进阶题
- 扫描策略：为什么使用 `SCAN` 而非 `KEYS`？分页/限流下如何避免阻塞？
- 部分恢复：如何仅重放无副作用节点？外部副作用节点如何幂等/补偿？
- 多租户/跨实例：如何设计 key 命名空间、TTL、版本号/乐观锁，保障一致性？

#### 实操题
- 扩展 `alist(before, limit)` 的过滤能力，支持按时间/阶段/用户筛选；写出 key 规范与索引方案。
- 在 `graph_routes_v2.py` 的流式接口中，加入“消息历史累积与恢复”逻辑，请给出伪代码与异常处理。

#### 附录：代码片段引用
- 消息历史累积（节选）：
```208:229:apis/graph_routes_v2.py
# 尝试获取现有状态中的消息历史
current_state = await app.aget_state(config)
existing_messages = current_state.values.get("messages", []) if current_state.values else []
updated_messages = existing_messages + [{"role": "user", "content": request.query}]
input_state = { ... , "messages": updated_messages, "need_human_review": request.enable_human_review }
```

- 事件流输出与中断恢复（节选）：
```236:276:apis/graph_routes_v2.py
async for chunk in app.astream(input_state, config=config_with_limits):
  node_name = list(chunk.keys())[0]
  node_state = list(chunk.values())[0] or {}
  new_stage = node_state.get("current_stage", current_stage)
  if node_state.get("need_human_review", False):
    yield human_review_required ...; break
  if new_stage == "completed": yield final_result ...; break
```

#### 图稿
- 参见：`interview/diagrams/cache_checkpoint.md`（缓存与检查点关系）。

### 最小可运行示例（curl）
- 触发流式执行并观察阶段：
```bash
curl -N -X POST \
  http://localhost:8000/graph_v2/chat/stream \
  -H 'Content-Type: application/json' \
  -d '{"user_id":"u2","session_id":"sess-recover","query":"写一篇运营方案","enable_human_review":true}'
```
- 当返回 human_review_required 事件后，通过恢复接口继续：
```bash
curl -X POST http://localhost:8000/graph/resume \
  -H 'Content-Type: application/json' \
  -d '{"user_id":"u2","session_id":"sess-recover","approved":true,"action":"approve"}'
```

### 样例回答/评分标准
- 样例回答要点：
  - SCAN 扫描、键空间命名与 before/limit 过滤；
  - 最小可恢复状态 + 无副作用重放 + 幂等/补偿；
  - 多实例一致性（版本/乐观锁）、降级到内存检查点策略；
  - 观测指标（命中率/恢复时长/失败率）。
- 评分标准：
  - 优秀：引用具体方法与键规范，覆盖异常与降级路径；
  - 合格：能清楚描述流程与关键点；
  - 待提高：缺少一致性与风险控制。

### 参考答案（示例）
- 序列化/反序列化（serde）：
  - Checkpoint 存储 `type` 与二进制 `checkpoint`，通过 `serde.dumps_typed/loads_typed` 保持前后兼容；
  - Metadata 单独 JSON 存储，便于增量演进。
- 索引与扫描：
  - Key 规范：`checkpoint$thread$ns$checkpoint_id` 与 `writes$thread$ns$checkpoint_id$task$idx`；
  - 列表查询使用 `SCAN` + 本地排序 + `before/limit` 过滤，避免 `KEYS` 阻塞。
- 部分恢复：
  - 保存“最小可恢复状态 + 路由位点 + 父指针”；
  - 恢复后仅重放无副作用步骤（LLM/只读）；外部副作用步骤使用幂等键或补偿。
- 一致性与降级：
  - 乐观锁/版本号用于并发写；
  - Redis 故障时降级为内存检查点并提示用户，恢复后自动切回并对齐；

### 常见错误与改进建议
- 错误：使用 KEYS 扫描导致阻塞与抖动。
  - 改进：使用 SCAN 分批遍历，结合 before/limit 过滤。
- 错误：检查点保存全量状态，恢复/网络放大。
  - 改进：只保存最小可恢复状态与指针，必要时补回上下文。
- 错误：恢复后重复外部副作用。
  - 改进：幂等键与补偿；恢复逻辑仅重放无副作用节点。

#### 场景题
- 恢复点漂移：当外部世界已发生变化（索引更新/第三方侧变更），如何通过“快照 + 再验证 + 降级输出”收敛差异？
- 高可用：Redis 故障或数据丢失时，如何降级到内存检查点并提示用户，再在恢复后自动切回？

#### 追问
- 若要改造成“可插拔存储”，需要抽象哪些接口？对对象存储/SQL 的差异化适配点在哪里？
- 指标：如何统计 checkpoint 命中率、恢复平均时长、恢复失败率，并将其纳入 SLO？
