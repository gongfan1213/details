### 03 上下文与记忆架构（参考答案）

- 关键参考: `agents/graph/state/**`, `agents/graph/redis_checkpoint.py`, `agents/graph/workflows/**`, `utils/database/**`

### 一、state vs memory 的边界
- 执行期 state：一次工作流执行的短期上下文，包含最新指令、路由位点、子任务中间产物（如 `state.req.spec`, `state.search.evidence`）。
- 长期 memory：跨会话/跨执行保留的信息，如用户偏好、历史任务摘要、知识库索引、工具调用画像等。
- 原则：短期尽量小、结构化；长期要可检索（倒排/向量）、可裁剪（时间窗/重要性）。

### 二、检查点（Checkpoint）存储粒度
- 粒度：保存“最小可恢复状态”（当前位置+必要上下文快照），避免保存冗余大文档；
- MemorySaver：进程内存态，适用于开发与小流量；
- AsyncRedisSaver：集中存储，结构化键空间（会话ID/图ID/step），支持 `serde` 与 `WRITES_IDX_MAP` 索引快速定位；
- 回放：恢复后仅重放无副作用步骤；对外部写操作需幂等键或补偿逻辑。

### 三、写入与清理策略
- TTL：对短期 state 设较短 TTL（分钟/小时级）；
- LRU/热度淘汰：按访问频率清理长期 memory 的低价值条目；
- 任务完成清理：在 END 边界执行批量清理钩子（清理中间态/大对象缓存）；
- 元数据：为每条 memory 标注来源、重要性与过期策略，便于统一任务。

### 四、语义记忆与向量检索
- 结合 Milvus：将高价值历史输出/证据转写为向量，按主题/Agent/领域建分区；
- 检索注入：在进入写作/决策前，按 `query → retrieve → rerank → compress` 注入合适上下文；
- 去重与压缩：同源近重复结果合并，保留代表性片段降低 token 成本。

### 五、Agentic/KV Memory 的落地建议
- Agentic Memory：
  - 结构：按 Agent 类型与任务阶段维护语义记忆桶（如“检索证据桶”“写作风格桶”）；
  - 编排：进入节点前先检索对应桶，裁剪后注入 Prompt；
  - 写回：节点结束后按可信度/重要性写回有限条目。
- KV Memory：
  - 结构：Redis Hash/Sorted Set 按 key 组织（如 `ctx:{session}:{phase}`），记录最常用 prompt 片段、工具参数模板、少样本示例；
  - 命中：直接拼装，显著降低 token 与延迟。

### 六、多租户与隔离
- 命名空间：key 前缀包含租户/用户/会话；
- 访问控制：在 apis 中注入身份上下文，工具与存储访问时做权限校验；
- 脱敏：长期记忆写入前做 PII 识别与掩码；敏感字段用 KMS 加密存储。

### 七、实操走查要点
- `redis_checkpoint.py`：关注 `serde`、写入索引、错误恢复与数据兼容策略；
- `compile_*_with_*`：检查点注入点与 debug 模式开关；
- `state/*`：字段粒度与可扩展性（避免巨型对象直接入 state）。

### 八、典型一致性问题与对策
- 写后读延迟：读到旧值→在关键更新后强制刷新或版本号推进；
- 重放漂移：恢复点后上游外部状态已变→通过“快照 + 幂等/补偿”收敛差异；
- 并发写：同一会话并行任务写同 key→加租约/版本冲突检测并回退重试。

### 附录：Redis Checkpoint 关键实现片段

- 写入检查点（节选）：
```253:282:agents/graph/redis_checkpoint.py
thread_id = config["configurable"]["thread_id"]
checkpoint_id = checkpoint["id"]
key = _make_redis_checkpoint_key(thread_id, checkpoint_ns, checkpoint_id)
type_, serialized_checkpoint = self.serde.dumps_typed(checkpoint)
data = {"checkpoint": serialized_checkpoint, "type": type_, ...}
await self.conn.hset(key, mapping=data)
await self.conn.expire(key, settings.memory.checkpoint_ttl)
return {"configurable": {"thread_id": thread_id, "checkpoint_ns": checkpoint_ns, "checkpoint_id": checkpoint_id}}
```

### 样例回答/评分标准
- 样例回答要点：
  - state vs memory 边界、TTL/LRU/任务完成清理的组合；
  - Milvus 结合语义记忆、注入前压缩与去重；
  - 多租户隔离与隐私脱敏；
  - 检查点最小可恢复 + 幂等/补偿 + 版本/乐观锁。
- 评分标准：
  - 优秀：能落到字段级粒度与 key 命名规范，给出一致性与隐私方案；
  - 合格：讲清策略组合与读写路径；
  - 待提高：缺少策略权衡与异常路径处理。

### 参考答案（示例）
- 边界与结构：
  - 短期 state：仅承载当前执行必要上下文（路由、阶段输出、消息片段），字段命名空间化；
  - 长期 memory：用户画像/偏好/历史摘要/知识库索引；按主题/时间/重要性分桶，支持向量检索；
- 写入/清理：
  - state 结束即清理或短 TTL；长期 memory 加权淘汰（LRU+热度+时间窗），END 边界触发批量清理钩子；
  - 记录来源/重要性/到期策略元数据，便于统一治理；
- 与向量检索结合：
  - 把高价值输出/证据入库到 Milvus（分区：领域/Agent/时间）；
  - 在写作/决策前用 `retrieve→rerank→compress` 注入；近重复合并；
- 一致性与恢复：
  - 检查点保存“最小可恢复状态 + 路由位点 + 父指针”；
  - 恢复后仅重放无副作用节点；外部写操作用幂等/补偿；
  - 乐观锁/版本字段处理并发写；

### 常见错误与改进建议
- 错误：长期记忆无限增长，查询与注入成本飙升。
  - 改进：TTL/权重淘汰/时间窗压缩；只保留高价值摘要与引用。
- 错误：检查点包含大文档与二进制，导致 Redis 压力大。
  - 改进：保存引用与必要元数据，大对象存 OSS/DB。
- 错误：恢复后外部状态变化导致“漂移”。
  - 改进：恢复前做快照校验与再验证，不一致时降级或触发人审。

- 写入中间结果（节选）：
```303:323:agents/graph/redis_checkpoint.py
for idx, (channel, value) in enumerate(writes):
  key = _make_redis_checkpoint_writes_key(..., WRITES_IDX_MAP.get(channel, idx))
  type_, serialized_value = self.serde.dumps_typed(value)
  if all(w[0] in WRITES_IDX_MAP for w in writes):
    await self.conn.hset(key, mapping={...})
  else:
    await self.conn.hsetnx(key, field, value)
  await self.conn.expire(key, settings.memory.checkpoint_ttl)
```

- 读取并解析（节选）：
```338:359:agents/graph/redis_checkpoint.py
checkpoint_key = await self._aget_checkpoint_key(...)
checkpoint_data = await self.conn.hgetall(checkpoint_key)
pending_writes = await self._aload_pending_writes(thread_id, checkpoint_ns, checkpoint_id)
return _parse_redis_checkpoint_data(self.serde, checkpoint_key, checkpoint_data, pending_writes=pending_writes)
```