# RAG方法总结 - 第二部分：文档处理与分块方法

## 概述
本文档继续总结MasteringRAG项目中的文档处理、分块技术和高级检索方法，包括父文档检索、上下文压缩、RAPTOR、上下文嵌入等创新技术。

---

## 9. 父文档检索器 (09_parent_document_retriever.ipynb)

### 方法描述
父文档检索器是一种分层检索方法，首先检索小的文档片段，然后返回包含这些片段的更大父文档，以提供更完整的上下文信息。

### 核心作用
- **分层检索**：先检索小片段，再获取父文档
- **上下文增强**：提供更完整的背景信息
- **信息完整性**：避免信息碎片化

### 技术原理
1. 将文档分割成小的子文档片段
2. 建立子文档到父文档的映射关系
3. 检索时先找到相关的子文档
4. 返回对应的父文档作为最终结果

### 实现示例
```python
from langchain.retrievers import ParentDocumentRetriever
from langchain.text_splitter import RecursiveCharacterTextSplitter

def setup_parent_document_retriever(documents, vectorstore):
    """
    设置父文档检索器
    """
    # 子文档分割器（小片段）
    child_splitter = RecursiveCharacterTextSplitter(
        chunk_size=200,
        chunk_overlap=20
    )
    
    # 父文档分割器（大片段）
    parent_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100
    )
    
    # 创建父文档检索器
    retriever = ParentDocumentRetriever(
        vectorstore=vectorstore,
        child_splitter=child_splitter,
        parent_splitter=parent_splitter
    )
    
    # 添加文档
    retriever.add_documents(documents)
    
    return retriever
```

### 优势
- 提供更完整的上下文信息
- 减少信息碎片化
- 提高检索结果的可读性

---

## 10. 上下文压缩 (10_contextual_compression.ipynb)

### 方法描述
上下文压缩是一种动态压缩检索到的文档内容的技术，只保留与查询最相关的部分，减少噪声并提高生成质量。

### 核心作用
- **内容压缩**：动态压缩文档内容
- **相关性过滤**：只保留相关部分
- **噪声减少**：去除无关信息

### 技术实现
```python
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor

def setup_contextual_compression(base_retriever, llm):
    """
    设置上下文压缩检索器
    """
    # 创建压缩器
    compressor = LLMChainExtractor.from_llm(llm)
    
    # 创建上下文压缩检索器
    compression_retriever = ContextualCompressionRetriever(
        base_compressor=compressor,
        base_retriever=base_retriever
    )
    
    return compression_retriever
```

### 压缩策略
1. **提取式压缩**：提取最相关的文本片段
2. **摘要式压缩**：生成文档摘要
3. **过滤式压缩**：过滤掉不相关的内容

### 优势
- 减少上下文长度
- 提高生成质量
- 降低计算成本

---

## 11. N-Chunks检索 (11_1_baseline_n_chunks.ipynb, 11_2_full_proc_n_chunks.ipynb)

### 方法描述
N-Chunks检索是一种基于多个文档片段进行检索的方法，通过检索多个相关片段来提供更全面的信息。

### 核心作用
- **多片段检索**：同时检索多个相关片段
- **信息覆盖**：提供更全面的信息覆盖
- **上下文丰富**：增加上下文信息的丰富度

### 技术实现
```python
def n_chunks_retrieval(query, vectorstore, n_chunks=5):
    """
    N-Chunks检索实现
    """
    # 检索多个文档片段
    docs = vectorstore.similarity_search(query, k=n_chunks)
    
    # 合并文档内容
    combined_content = "\n\n".join([doc.page_content for doc in docs])
    
    return combined_content, docs
```

### 变体方法
- **Baseline N-Chunks**：基础的多片段检索
- **Full Processing N-Chunks**：完整处理的多片段检索

### 优势
- 提供更全面的信息
- 减少信息遗漏
- 提高检索召回率

---

## 12. RAPTOR (12_raptor.ipynb)

### 方法描述
RAPTOR（Recursive Abstractive Processing for Tree-Organized Retrieval）是一种基于树状结构的文档组织和检索方法，通过递归抽象处理来构建层次化的文档表示。

### 核心作用
- **层次化组织**：构建树状文档结构
- **递归抽象**：逐层抽象文档内容
- **结构化检索**：基于结构进行检索

### 技术原理
1. **文档分割**：将文档分割成基础片段
2. **递归聚类**：使用聚类算法组织文档片段
3. **抽象生成**：为每个聚类生成抽象表示
4. **树状构建**：构建层次化的文档树
5. **检索导航**：在树状结构中导航检索

### 实现示例
```python
def raptor_processing(documents, embedding_model):
    """
    RAPTOR处理流程
    """
    # 1. 文档分割
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    chunks = splitter.split_documents(documents)
    
    # 2. 递归聚类
    tree = build_raptor_tree(chunks, embedding_model)
    
    # 3. 抽象生成
    tree = generate_abstractions(tree, llm)
    
    return tree

def raptor_retrieval(query, tree, embedding_model):
    """
    RAPTOR检索
    """
    # 在树状结构中检索
    relevant_nodes = search_tree(query, tree, embedding_model)
    
    # 收集相关文档
    documents = collect_documents(relevant_nodes)
    
    return documents
```

### 优势
- 提供结构化的文档组织
- 支持多层次的检索
- 提高检索的精确性

---

## 13. 上下文嵌入 (13_1_contextual_embeddings.ipynb, 13_2_contextual_embeddings_deepseek.ipynb)

### 方法描述
上下文嵌入是一种考虑文档上下文信息的嵌入方法，通过将文档片段与其上下文信息结合来生成更准确的嵌入表示。

### 核心作用
- **上下文感知**：考虑文档的上下文信息
- **语义增强**：提升语义理解的准确性
- **检索优化**：改善检索的精确性

### 技术实现
```python
def contextual_embedding(text, context, embedding_model):
    """
    上下文嵌入生成
    """
    # 构建上下文感知的文本
    contextual_text = f"Context: {context}\nText: {text}"
    
    # 生成嵌入
    embedding = embedding_model.encode(contextual_text)
    
    return embedding

def contextual_retrieval(query, documents, embedding_model):
    """
    上下文检索
    """
    # 为每个文档生成上下文嵌入
    contextual_embeddings = []
    for doc in documents:
        context = get_document_context(doc)
        embedding = contextual_embedding(doc.page_content, context, embedding_model)
        contextual_embeddings.append(embedding)
    
    # 查询嵌入
    query_embedding = embedding_model.encode(query)
    
    # 相似度计算
    similarities = cosine_similarity([query_embedding], contextual_embeddings)[0]
    
    # 排序和返回
    ranked_docs = sorted(zip(documents, similarities), 
                        key=lambda x: x[1], reverse=True)
    
    return [doc for doc, score in ranked_docs]
```

### 变体方法
- **基础上下文嵌入**：使用基本的上下文信息
- **DeepSeek上下文嵌入**：使用DeepSeek模型的上下文嵌入

### 优势
- 提高语义理解的准确性
- 改善检索的精确性
- 支持复杂的上下文关系

---

## 14. CRAG (14_crag.ipynb)

### 方法描述
CRAG（Corrective RAG）是一种纠错式检索增强生成方法，通过外部知识验证和纠正检索结果，提高RAG系统的准确性。

### 核心作用
- **知识验证**：使用外部知识验证检索结果
- **错误纠正**：纠正检索中的错误信息
- **质量提升**：提高RAG系统的整体质量

### 技术原理
1. **初始检索**：进行初步的文档检索
2. **外部验证**：使用外部知识源验证检索结果
3. **错误检测**：检测检索结果中的错误
4. **结果纠正**：纠正检测到的错误
5. **最终生成**：基于纠正后的结果生成答案

### 实现示例
```python
def crag_pipeline(query, vectorstore, external_knowledge, llm):
    """
    CRAG管道实现
    """
    # 1. 初始检索
    initial_docs = vectorstore.similarity_search(query, k=5)
    
    # 2. 外部知识检索
    external_docs = search_external_knowledge(query, external_knowledge)
    
    # 3. 知识验证
    verified_docs = verify_knowledge(initial_docs, external_docs, llm)
    
    # 4. 错误纠正
    corrected_docs = correct_errors(verified_docs, external_docs, llm)
    
    # 5. 最终生成
    final_answer = generate_answer(query, corrected_docs, llm)
    
    return final_answer

def verify_knowledge(docs, external_docs, llm):
    """
    知识验证
    """
    verified_docs = []
    for doc in docs:
        # 检查文档内容与外部知识的一致性
        consistency_score = check_consistency(doc, external_docs, llm)
        if consistency_score > threshold:
            verified_docs.append(doc)
    
    return verified_docs
```

### 优势
- 提高信息的准确性
- 减少幻觉和错误
- 增强系统的可信度

---

## 总结

这部分文档涵盖了RAG系统中的高级文档处理和检索方法：

1. **父文档检索器**：适用于需要完整上下文的场景
2. **上下文压缩**：适用于需要减少噪声的场景
3. **N-Chunks检索**：适用于需要全面信息覆盖的场景
4. **RAPTOR**：适用于需要结构化检索的场景
5. **上下文嵌入**：适用于需要深度语义理解的场景
6. **CRAG**：适用于需要高准确性的场景

这些方法代表了RAG技术的最新发展，每种方法都有其特定的应用场景和优势。在实际应用中，可以根据具体需求选择最适合的方法或组合多种方法。
