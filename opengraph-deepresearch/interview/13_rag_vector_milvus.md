### 13 RAG / 向量检索 / Milvus 面试题（RAG & Vector Search with Milvus）

- 关注点：数据摄取、切分、嵌入、索引、召回、重排、缓存、质量评估
- 关键参考：`agents/graph/tool/vector_search.py`, `agents/graph/examples/vector_search_demo.py`, `agents/graph/tool/validate_milvus_config.py`, `pymilvus`

#### 基础题
- 向量库的角色：为何引入 Milvus？与关键词检索的互补性是什么？
- 文档切分与嵌入：切分粒度、重叠、模型选择如何影响召回/成本？
- 索引与参数：IVF/HNSW 的关键参数如何取舍（nlist/efConstruction/efSearch）？

#### 进阶题
- 召回与重排：初筛 TopK + MMR/Rerank；如何结合元数据过滤（时间、来源、语言）？
- 数据质量：如何避免脏数据与重复片段；如何做去重/压缩/版本化？
- 结果融合：多源召回（Web/库/结构化）如何统一评分并融合？

#### 实操题
- 走读 `vector_search.py` 的查询/插入关键路径，指出失败回退与异常映射点；给出“查询缓存键规范”。
- 执行 `validate_milvus_config.py` 之前后置哪些健康检查？如何在 CI 中阻断配置不当的上线？

#### 附录：代码片段引用
- 本地/远程 Embedding 回退（节选）：
```36:90:agents/graph/tool/vector_search.py
def get_text_embedding(self, text: str, max_retries: int = 3) -> List[float]:
  if self.use_local_embedding:
      return self._get_local_embedding(text)
  else:
      return self._get_openai_embedding(text, max_retries)
```

- Milvus 连接与搜索（节选）：
```178:219:agents/graph/tool/vector_search.py
self.client = MilvusClient(uri=self.hosted_url, token=self.hosted_token, db_name=self.database)
results = self.client.search(
  collection_name=self.collection_name,
  data=[query_vector], anns_field="vector",
  search_params={"metric_type": "IP", "params": {"nprobe": 10}},
  limit=top_k,
  output_fields=[...]
)
```

#### 场景题
- 大规模更新：索引重建与在线服务如何共存？是否需要“双写 + 灰度切换”？
- 多租户：集合/分区如何按租户/业务线隔离？访问控制如何落地？

#### 追问
- 向量质量度量：离线评测集、在线 A/B、人工对齐如何结合？
- 成本优化：冷数据下沉、按热度分层、召回阈值自适应。

#### 作业
- 设计“RAG 质量看板”：覆盖检索命中率、知识时效、引用一致性、答案自信度分布。

#### 图稿
- 参见：`interview/diagrams/rag_milvus_flow.md`。

#### 样例回答/评分标准
- 样例回答要点：
  - 切分/嵌入/索引参数取舍与质量-成本平衡；
  - 召回 + 重排 + 压缩链路与多源融合策略；
  - 键规范与多级缓存、错误回退与健康检查；
  - 多租户隔离与访问控制。
- 评分标准：
  - 优秀：能结合代码位点说明关键路径，提出可观测指标与降级策略；
  - 合格：能覆盖主要环节与参数，给出基本监控；
  - 待提高：停留在概念层，缺少工程实践。

### 常见错误与改进建议
- 错误：切分粒度过大/过小，召回与成本都差。
  - 改进：按语义边界切分，适度重叠；对不同来源配置差异化策略。
- 错误：索引与参数未监控，更新后退化不知。
  - 改进：上线前后跑离线评测与在线 A/B，设退化阈值与报警。
- 错误：检索结果直接拼接，造成冗长上下文。
  - 改进：rerank + compress，保留高价值句段与引用。

### 参考答案（示例）
- 数据管道：
  - 切分：按语义句段，长度 200~500 字，重叠 10%~20%；
  - 嵌入：统一模型（如 `text-embedding-3-small`），对多语种文本先语言检测再嵌入；
  - 索引：Milvus HNSW（M=32, efC=200, efS=64）或 IVF（nlist=2048）；
- 查询链路：
  - Embed Query → TopK 召回 → 元数据过滤（领域/时间/语言）→ Rerank（MMR/跨模型）→ Compress（句级抽取/摘要）→ 注入；
  - 结果缓存：`embedding_hash|filters|topk|version`，TTL 30~120s，防抖与请求合并；
- 质量评估：
  - 离线：标注小样本评测，计算命中率/一致性/引用率；
  - 在线：A/B 对比转化/用户满意度/追问率；退化阈值触发回滚与告警；
- 多租户：
  - 集合/分区按租户隔离；访问控制与查询限额；
