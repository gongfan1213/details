# 向量检索与Milvus系统｜技术面试话术

## 一句话定位
- 基于 Milvus 的语义检索，为选题/灵感/证据提供“相似内容召回+重排+趋势分析”。

## 架构要点
- 客户端：`agents/graph/tool/vector_search.py`（TextEmbeddingService + MilvusVectorSearcher）。
- 模式：语义/关键词/混合检索；IP 距离 + nprobe；过滤字段（作者/时间/标签）。
- 工具化：`@tool search_xiaohongshu_content` 供 Agent 调用。

## 难点与解决
- 向量不可用：OpenAI embedding 失败→本地降级；Milvus异常→关键词回退。
- 噪声与重复：MMR/去重合并；阈值与权重动态调参，按场景切配置。
- 成本与时延：缓存向量/批量嵌入/并发查询；TopK 后再重排压缩。

## 指标与收益
- 相关性点击率↑；写作参考的可用率↑；端到端检索P95 < 1-2s（缓存命中场景）。

## 可扩展 & 高可用
- 新平台集合接入：统一schema与索引规范；分区按主题/时间。

## Demo 话术
- 同一主题下展示“语义 vs 关键词 vs 混合”对比列表，解释为何混合更稳。

## 追问与答法
- Q：向量漂移怎么办？
  - A：定期重嵌入与索引重建；双写灰度切换，观测召回质量再切主。
