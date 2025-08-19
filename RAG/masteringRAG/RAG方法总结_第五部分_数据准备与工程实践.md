# RAG方法总结 - 第五部分：数据准备与工程实践

## 概述
本文档补充MasteringRAG项目中遗漏的重要知识点，包括数据准备、工程实践、产品化部署等关键内容。

---

## 数据准备与预处理

### 1. PDF解析与QA抽取 (00_PDF解析与QA抽取_v1.ipynb, 00_PDF解析与QA抽取_v1.1.ipynb)

#### 方法描述
PDF解析与QA抽取是RAG系统的基础数据准备阶段，通过解析PDF文档并抽取问答对来构建训练和评估数据集。

#### 核心作用
- **文档解析**：从PDF中提取文本内容
- **QA生成**：自动生成问答对
- **数据标注**：为RAG系统提供训练数据

#### 技术实现
```python
from langchain_community.document_loaders import PyPDFLoader
from langchain.schema import Document
import re

def parse_pdf_document(pdf_path):
    """
    PDF文档解析
    """
    # 加载PDF文档
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()
    
    # 清理文档内容
    pattern = r"^全球经济金融展望报告\n中国银行研究院 \d+ 2024年"
    cleaned_docs = []
    
    for doc in documents:
        cleaned_content = re.sub(pattern, '', doc.page_content)
        cleaned_docs.append(Document(
            page_content=cleaned_content,
            metadata=doc.metadata
        ))
    
    return cleaned_docs

def generate_qa_pairs(documents, llm):
    """
    生成问答对
    """
    qa_pairs = []
    
    for doc in documents:
        # 使用LLM生成问答对
        prompt = f"""
        基于以下文档内容，生成3个高质量的问答对：
        
        文档内容：
        {doc.page_content[:1000]}
        
        要求：
        1. 问题应该具体且有针对性
        2. 答案应该准确且完整
        3. 涵盖文档中的关键信息
        """
        
        response = llm.generate(prompt)
        qa_pairs.extend(parse_qa_from_response(response))
    
    return qa_pairs
```

#### 数据质量保证
- **内容清洗**：去除页眉页脚等无关内容
- **格式标准化**：统一文档格式
- **质量检查**：验证问答对的质量

---

### 2. 嵌入样本构建 (build_embedding_sample_v1.ipynb, build_embedding_sample_v2.ipynb)

#### 方法描述
嵌入样本构建是为嵌入模型微调准备训练数据的过程，通过构建正负样本对来训练更好的嵌入模型。

#### 核心作用
- **样本构建**：构建训练样本
- **负样本生成**：生成负样本提高模型性能
- **数据格式化**：将数据格式化为训练格式

#### 技术实现
```python
def build_embedding_samples(qa_df, documents, negative_ratio=7):
    """
    构建嵌入训练样本
    """
    samples = []
    
    for _, row in qa_df.iterrows():
        # 正样本
        positive_sample = {
            "query": row['question'],
            "positive": row['context'],
            "negatives": []
        }
        
        # 生成负样本
        negative_samples = generate_negative_samples(
            row['question'], 
            documents, 
            row['context'],
            negative_ratio
        )
        
        positive_sample["negatives"] = negative_samples
        samples.append(positive_sample)
    
    return samples

def generate_negative_samples(query, documents, positive_context, num_negatives):
    """
    生成负样本
    """
    # 计算查询与所有文档的相似度
    similarities = []
    for doc in documents:
        if doc.page_content != positive_context:
            similarity = calculate_similarity(query, doc.page_content)
            similarities.append((similarity, doc.page_content))
    
    # 选择相似度较低的作为负样本
    similarities.sort(key=lambda x: x[0])
    negative_samples = [content for _, content in similarities[:num_negatives]]
    
    return negative_samples
```

#### 样本策略
1. **随机负样本**：随机选择不相关文档
2. **困难负样本**：选择相似度较高的不相关文档
3. **跨设备负样本**：在多GPU训练中共享负样本

---

## 工程实践

### 1. 基线系统 (01_baseline.ipynb)

#### 方法描述
基线系统是RAG系统的基础实现，提供了完整的RAG流程，包括文档加载、分块、嵌入、检索和生成。

#### 核心组件
- **文档加载器**：PyPDFLoader等
- **文本分割器**：RecursiveCharacterTextSplitter
- **嵌入模型**：BGE系列模型
- **向量数据库**：ChromaDB
- **检索器**：相似度检索
- **生成模型**：大语言模型

#### 实现示例
```python
from langchain_community.vectorstores import Chroma
from langchain.embeddings import HuggingFaceBgeEmbeddings
from langchain.llms import Ollama

def setup_baseline_rag(documents):
    """
    设置基线RAG系统
    """
    # 1. 文档分割
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    chunks = splitter.split_documents(documents)
    
    # 2. 嵌入模型
    embeddings = HuggingFaceBgeEmbeddings(
        model_name="BAAI/bge-large-zh-v1.5",
        model_kwargs={'device': 'cuda'},
        encode_kwargs={'normalize_embeddings': True}
    )
    
    # 3. 向量数据库
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings
    )
    
    # 4. 检索器
    retriever = vectorstore.as_retriever(
        search_kwargs={"k": 5}
    )
    
    # 5. 生成模型
    llm = Ollama(model="qwen2:7b-instruct")
    
    return retriever, llm

def baseline_rag_query(query, retriever, llm):
    """
    基线RAG查询
    """
    # 检索相关文档
    docs = retriever.get_relevant_documents(query)
    
    # 构建提示
    context = "\n\n".join([doc.page_content for doc in docs])
    prompt = f"""
    基于以下信息回答问题：
    
    信息：{context}
    
    问题：{query}
    
    回答：
    """
    
    # 生成答案
    response = llm.generate(prompt)
    
    return response
```

---

### 2. 模型微调脚本 (finetune_bge_embedding_v*.sh)

#### 方法描述
模型微调脚本提供了完整的嵌入模型微调流程，包括参数配置、训练执行和结果保存。

#### 核心功能
- **参数配置**：学习率、批次大小、训练轮数等
- **分布式训练**：多GPU训练支持
- **实验管理**：版本控制和实验记录
- **结果保存**：模型和日志保存

#### 脚本示例
```bash
#!/bin/bash

# 环境配置
export TRAIN_DATASET=outputs/v1_20240713/emb_samples_qa_v1.jsonl
export N_EPOCH=5
export TRAIN_GROUP_SIZE=8
export GRADIENT_ACCUMULATION_STEPS=32
export PER_DEVICE_TRAIN_BATCH_SIZE=1
export N_DEVICE=1

# 版本控制
export VERSION=ft_v1_bge_large_epoch_${N_EPOCH}_bz_${BATCH_SIZE}_$(date +"%Y%m%d_%H%M")
export OUTPUT_DIR=experiments/embedding/finetune/${VERSION}

# 训练执行
torchrun --nproc_per_node ${N_DEVICE} \
-m FlagEmbedding.baai_general_embedding.finetune.run \
--output_dir ${OUTPUT_DIR} \
--model_name_or_path BAAI/bge-large-zh-v1.5 \
--train_data ${TRAIN_DATASET} \
--learning_rate 1e-5 \
--fp16 \
--num_train_epochs ${N_EPOCH} \
--per_device_train_batch_size ${PER_DEVICE_TRAIN_BATCH_SIZE} \
--gradient_accumulation_steps ${GRADIENT_ACCUMULATION_STEPS} \
--normlized True \
--temperature 0.02 \
--query_max_len 64 \
--passage_max_len 512 \
--train_group_size ${TRAIN_GROUP_SIZE} \
--negatives_cross_device \
--logging_steps 5 \
--save_steps 50 \
--save_total_limit 10 \
--warmup_ratio 0.05 \
--lr_scheduler_type cosine
```

#### 关键参数说明
- **learning_rate**：学习率，通常设置为1e-5
- **temperature**：对比学习温度参数
- **train_group_size**：训练组大小，影响负样本数量
- **query_max_len/passage_max_len**：查询和文档的最大长度
- **negatives_cross_device**：跨设备负样本共享

---

## 产品化部署

### 1. Flowise产品化 (products/01_flowise_basic_rag.ipynb)

#### 方法描述
Flowise是一个可视化的RAG系统构建平台，支持拖拽式构建RAG流程，便于产品化部署。

#### 核心功能
- **可视化构建**：拖拽式流程设计
- **API接口**：提供RESTful API
- **部署简化**：一键部署RAG系统
- **监控管理**：系统监控和管理

#### 实现示例
```python
import requests

def setup_flowise_rag():
    """
    设置Flowise RAG系统
    """
    # Flowise API配置
    API_URL = "http://192.168.31.92:3000/api/v1/prediction/8e7a0311-69be-4fee-979c-d57ee3726ceb"
    
    return API_URL

def flowise_rag_query(question, api_url):
    """
    Flowise RAG查询
    """
    payload = {
        "question": question
    }
    
    response = requests.post(api_url, json=payload)
    return response.json()

def batch_flowise_evaluation(test_questions, api_url):
    """
    批量Flowise评估
    """
    results = []
    
    for question in test_questions:
        response = flowise_rag_query(question, api_url)
        results.append({
            'question': question,
            'answer': response['text'],
            'metadata': response.get('metadata', {})
        })
    
    return results
```

#### 产品化优势
- **快速部署**：无需复杂配置
- **易于维护**：可视化界面管理
- **可扩展性**：支持多种组件
- **用户友好**：降低技术门槛

---

### 2. HyDE产品化 (products/02_flowise_hyde.ipynb)

#### 方法描述
HyDE产品化将假设性文档嵌入技术集成到Flowise平台中，提供更智能的检索能力。

#### 技术特点
- **查询理解**：通过生成假设性文档理解查询
- **语义增强**：提高检索的语义匹配度
- **产品化集成**：在Flowise中实现HyDE

---

### 3. RRF产品化 (products/03_flowise_rrf.ipynb)

#### 方法描述
RRF（Reciprocal Rank Fusion）产品化将多检索策略融合技术集成到Flowise平台中。

#### 技术特点
- **多策略融合**：结合多种检索策略
- **排序优化**：通过RRF算法优化排序
- **产品化部署**：在Flowise中实现RRF

---

## 实验管理与评估

### 1. 实验版本控制

#### 版本命名规范
```python
def generate_experiment_version(experiment_type, model_name, params):
    """
    生成实验版本号
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    version = f"{experiment_type}_{model_name}_{params}_{timestamp}"
    return version

# 示例
expr_version = 'retrieval_v1_bge_large_chunk500_overlap50_20240713_1430'
```

#### 实验目录结构
```
experiments/
├── retrieval/
│   ├── retrieval_v1_baseline/
│   ├── retrieval_v2_reranker/
│   └── retrieval_v3_hyde/
├── embedding/
│   ├── finetune/
│   └── evaluation/
└── generation/
    ├── finetune/
    └── evaluation/
```

### 2. 结果保存与加载

#### 缓存机制
```python
def cache_results(func):
    """
    结果缓存装饰器
    """
    def wrapper(*args, **kwargs):
        cache_file = generate_cache_filename(func.__name__, args, kwargs)
        
        if os.path.exists(cache_file):
            print('Found cache, loading...')
            return pickle.load(open(cache_file, 'rb'))
        
        result = func(*args, **kwargs)
        pickle.dump(result, open(cache_file, 'wb'))
        return result
    
    return wrapper

@cache_results
def expensive_computation(data, params):
    """
    昂贵的计算，使用缓存
    """
    # 复杂计算逻辑
    return result
```

---

## 性能优化

### 1. 计算资源优化

#### GPU内存优化
```python
def optimize_gpu_memory():
    """
    GPU内存优化
    """
    import torch
    
    # 清理GPU缓存
    torch.cuda.empty_cache()
    
    # 设置内存分配策略
    torch.cuda.set_per_process_memory_fraction(0.8)
    
    # 使用混合精度训练
    from torch.cuda.amp import autocast, GradScaler
    scaler = GradScaler()
    
    return scaler
```

#### 批处理优化
```python
def batch_processing(items, batch_size=32):
    """
    批处理优化
    """
    results = []
    
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        batch_results = process_batch(batch)
        results.extend(batch_results)
    
    return results
```

### 2. 检索性能优化

#### 索引优化
```python
def optimize_vector_index(vectorstore):
    """
    向量索引优化
    """
    # 设置索引参数
    vectorstore._collection.create_index(
        "embedding",
        index_type="hnsw",
        metric_type="cosine",
        params={
            "m": 16,
            "ef_construction": 200
        }
    )
```

#### 缓存策略
```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def cached_embedding(text):
    """
    嵌入缓存
    """
    return embedding_model.encode(text)

@lru_cache(maxsize=100)
def cached_retrieval(query):
    """
    检索缓存
    """
    return vectorstore.similarity_search(query, k=5)
```

---

## 监控与日志

### 1. 系统监控

#### 性能监控
```python
import time
import logging

def monitor_performance(func):
    """
    性能监控装饰器
    """
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        logging.info(f"{func.__name__} took {end_time - start_time:.2f} seconds")
        return result
    
    return wrapper

@monitor_performance
def rag_query(query):
    """
    带性能监控的RAG查询
    """
    # RAG查询逻辑
    return result
```

#### 质量监控
```python
def quality_monitoring(query, answer, context):
    """
    质量监控
    """
    metrics = {
        'query_length': len(query),
        'answer_length': len(answer),
        'context_length': len(context),
        'answer_relevance': calculate_relevance(query, answer),
        'context_relevance': calculate_relevance(query, context)
    }
    
    logging.info(f"Quality metrics: {metrics}")
    return metrics
```

### 2. 日志管理

#### 结构化日志
```python
import logging
import json

def setup_structured_logging():
    """
    设置结构化日志
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('rag_system.log'),
            logging.StreamHandler()
        ]
    )

def log_rag_interaction(query, answer, metadata):
    """
    记录RAG交互
    """
    log_entry = {
        'timestamp': time.time(),
        'query': query,
        'answer': answer,
        'metadata': metadata
    }
    
    logging.info(json.dumps(log_entry))
```

---

## 总结

这部分文档补充了MasteringRAG项目中的重要工程实践内容：

### 数据准备
1. **PDF解析与QA抽取**：基础数据准备
2. **嵌入样本构建**：训练数据准备

### 工程实践
1. **基线系统**：完整的RAG实现
2. **模型微调脚本**：自动化训练流程

### 产品化部署
1. **Flowise产品化**：可视化RAG构建
2. **HyDE产品化**：智能检索集成
3. **RRF产品化**：多策略融合

### 实验管理
1. **版本控制**：实验版本管理
2. **结果缓存**：性能优化

### 性能优化
1. **计算资源优化**：GPU内存和批处理
2. **检索性能优化**：索引和缓存

### 监控与日志
1. **系统监控**：性能和质量监控
2. **日志管理**：结构化日志记录

这些内容为RAG系统的工程化实现和产品化部署提供了全面的指导。
