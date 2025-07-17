- 推荐系统-召回+排序+精排

检索，多路召回

重点是文档结构和对应文本解析

chunk,标点和长度

普通文档场景bge-v3


bm25 和dense rerank


上下文拼接： 召回是chunk，拼接式chunk对应的content，依赖于一个好的文档结构解析来界定chunk对应的content

多跳:agentic rag

嵌入前对文件进行处理

第三人称换成具体的名词


chunk分块，固定分块，文本结构正则分块，文件内容少的，相对独立的，一个文件一个块，

语义分块优化，根据文件需求场景切分数据，原先数据做一层梳理，切分后维护标签做分块分组

多跳，top-k太松，看场景试配的召回方式


rerank处理，

多跳的压缩上下文，摘要聚合，结合query改写回答


sestancetransfomer

BAAI

text-embedding-002/large/small

图片多模态ebedding

用多模态的llm或者ocr等把图片转换成为文本

# 分块策略适合绝大部分

1.固定长度+滑动窗口

2.递归字符切分（按照段落-》句子->字符）

3.基于句子的语义切分

4.Markdown结构感知切分

5.基于查询的动态切分，query-aware






