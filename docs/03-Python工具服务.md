# Python工具服务

## 功能概述

Python工具服务是JoyAgent-JDGenie的核心执行引擎，提供代码执行、报告生成、深度搜索和文件管理等核心能力。服务基于FastAPI构建，支持流式SSE响应和非流式返回，为智能体提供强大的工具执行能力。

## 业务功能实现

### 1. 代码执行服务（Code Interpreter）

#### 1.1 核心功能
**功能**：执行Python代码，支持数据处理、可视化、文件操作等
**特点**：
- 安全的沙箱执行环境
- 支持多种Python库（pandas、numpy、matplotlib等）
- 流式执行反馈
- 文件上传和结果输出

#### 1.2 API接口
```python
@router.post("/code_interpreter")
async def post_code_interpreter(body: CIRequest):
    async def _stream():
        acc_content = ""
        try:
            # 执行代码逻辑
            result = await code_interpreter_agent(body)
            # 流式返回结果
            yield ServerSentEvent(data=result)
        except Exception as e:
            yield ServerSentEvent(data=f"Error: {str(e)}")
        finally:
            yield ServerSentEvent(data="[DONE]")
    
    return EventSourceResponse(_stream())
```

#### 1.3 安全机制
```python
# 白名单化的导入库
additional_authorized_imports = [
    "pandas", "numpy", "matplotlib", "seaborn", 
    "sklearn", "requests", "json", "csv"
]

# 临时工作目录隔离
temp_dir = f"/tmp/code_interpreter/{request_id}"
output_dir = f"/tmp/output/{request_id}"
```

### 2. 报告生成服务（Report）

#### 2.1 支持格式
- **HTML报告**：交互式网页报告
- **PPT报告**：PowerPoint演示文稿
- **Markdown报告**：结构化文档

#### 2.2 生成流程
```python
@router.post("/report")
async def post_report(body: ReportRequest):
    async def _stream():
        try:
            # 根据文件类型选择生成策略
            if body.file_type == "html":
                result = await generate_html_report(body)
            elif body.file_type == "ppt":
                result = await generate_ppt_report(body)
            else:
                result = await generate_markdown_report(body)
            
            yield ServerSentEvent(data=result)
        except Exception as e:
            yield ServerSentEvent(data=f"Error: {str(e)}")
        finally:
            yield ServerSentEvent(data="[DONE]")
    
    return EventSourceResponse(_stream())
```

### 3. 深度搜索服务（Deep Search）

#### 3.1 搜索能力
**功能**：执行深度网络搜索和信息检索
**特点**：
- 多搜索引擎支持（Google、Bing等）
- 智能结果聚合和分析
- 实时搜索进度反馈
- 搜索结果结构化处理

#### 3.2 搜索流程
```python
@router.post("/deepsearch")
async def post_deepsearch(body: DeepSearchRequest):
    async def _stream():
        try:
            # 初始化搜索组件
            search_engine = DeepSearch()
            
            # 执行搜索
            results = await search_engine.search(
                query=body.query,
                max_loop=body.max_loop,
                search_engines=body.search_engines
            )
            
            # 流式返回搜索结果
            for result in results:
                yield ServerSentEvent(data=json.dumps(result))
                
        except Exception as e:
            yield ServerSentEvent(data=f"Error: {str(e)}")
        finally:
            yield ServerSentEvent(data="[DONE]")
    
    return EventSourceResponse(_stream())
```

### 4. 文件管理服务（File Tool）

#### 4.1 文件操作接口
```python
# 文件上传
@router.post("/upload_file")
async def upload_file(body: FileUploadRequest):
    return await upload_file_content(body)

# 文件下载
@router.get("/download/{file_id}/{file_name}")
async def download_file(file_id: str, file_name: str):
    return await download_file_content(file_id, file_name)

# 文件预览
@router.get("/preview/{file_id}/{file_name}")
async def preview_file(file_id: str, file_name: str):
    return await preview_file_content(file_id, file_name)

# 文件列表
@router.post("/get_file_list")
async def get_file_list(body: FileListRequest):
    return await get_files_by_request_id(body.request_id, body.filters)
```

#### 4.2 文件存储管理
```python
class FileManager:
    def __init__(self):
        self.storage_path = "/data/files"
        self.db_engine = DatabaseEngine()
    
    async def save_file(self, file_info: FileInfo):
        # 保存文件到存储系统
        file_path = f"{self.storage_path}/{file_info.file_id}/{file_info.file_name}"
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(file_info.content)
        
        # 保存元数据到数据库
        await self.db_engine.save_file_info(file_info)
```

## 技术方案支撑

### 1. 流式响应机制

#### 1.1 SSE协议实现
```python
from sse_starlette import ServerSentEvent, EventSourceResponse

async def stream_response():
    async def _stream():
        # 发送心跳
        yield ServerSentEvent(data="heartbeat", event="ping")
        
        # 发送数据
        for chunk in data_chunks:
            yield ServerSentEvent(data=chunk)
        
        # 发送结束标记
        yield ServerSentEvent(data="[DONE]")
    
    return EventSourceResponse(_stream())
```

#### 1.2 心跳保活机制
```python
# 定期发送心跳包
async def heartbeat_generator():
    while True:
        await asyncio.sleep(15)  # 15秒心跳间隔
        yield ServerSentEvent(data="heartbeat", event="ping")
```

### 2. 异步执行架构

#### 2.1 异步任务处理
```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

class AsyncTaskExecutor:
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=10)
    
    async def execute_code(self, code: str):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, self._run_code, code)
    
    def _run_code(self, code: str):
        # 在独立线程中执行代码
        return exec(code, globals(), locals())
```

#### 2.2 任务队列管理
```python
from asyncio import Queue

class TaskQueue:
    def __init__(self):
        self.queue = Queue()
        self.running_tasks = {}
    
    async def add_task(self, task_id: str, task_func):
        await self.queue.put((task_id, task_func))
    
    async def process_tasks(self):
        while True:
            task_id, task_func = await self.queue.get()
            try:
                result = await task_func()
                self.running_tasks[task_id] = result
            except Exception as e:
                self.running_tasks[task_id] = f"Error: {str(e)}"
```

### 3. 数据库集成

#### 3.1 文件元数据管理
```python
class DatabaseEngine:
    def __init__(self):
        self.connection_string = os.getenv("DATABASE_URL")
    
    async def save_file_info(self, file_info: FileInfo):
        async with aiosqlite.connect(self.connection_string) as db:
            await db.execute("""
                INSERT INTO files (file_id, file_name, description, request_id, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (file_info.file_id, file_info.file_name, 
                  file_info.description, file_info.request_id, 
                  datetime.now()))
            await db.commit()
```

## 常见问题

### 1. 代码执行安全
**问题**：恶意代码执行风险
**解决方案**：
- 沙箱环境隔离
- 导入库白名单
- 资源使用限制
- 超时控制机制

### 2. 内存管理
**问题**：大文件处理内存溢出
**解决方案**：
- 流式文件处理
- 内存使用监控
- 自动垃圾回收
- 分块处理机制

### 3. 并发控制
**问题**：高并发请求处理
**解决方案**：
- 异步任务队列
- 连接池管理
- 负载均衡
- 限流机制

## 系统设计

### 1. 架构层次
```
API层
├── FastAPI路由          // RESTful API接口
├── 中间件处理           // 请求/响应处理
└── 异常处理             // 统一异常处理

业务层
├── 代码执行引擎         // Python代码执行
├── 报告生成器           // 多格式报告生成
├── 搜索组件             // 深度搜索实现
└── 文件管理器           // 文件操作管理

数据层
├── 文件存储             // 文件系统存储
├── 数据库               // 元数据管理
└── 缓存系统             // 性能优化
```

### 2. 配置管理
```python
# config.py
class Config:
    # 服务配置
    HOST = "0.0.0.0"
    PORT = 1601
    
    # 数据库配置
    DATABASE_URL = "sqlite:///genie_tool.db"
    
    # 文件存储配置
    STORAGE_PATH = "/data/files"
    
    # 安全配置
    ALLOWED_IMPORTS = ["pandas", "numpy", "matplotlib"]
    MAX_EXECUTION_TIME = 300  # 5分钟
    MAX_MEMORY_USAGE = 1024   # 1GB
```

### 3. 监控指标
- 请求响应时间
- 代码执行成功率
- 内存使用情况
- 并发请求数量
- 错误率统计

## 可扩展性

### 1. 新工具扩展
```python
# 自定义工具实现
class CustomTool:
    def __init__(self):
        self.name = "custom_tool"
        self.description = "自定义工具"
    
    async def execute(self, params: dict):
        # 工具执行逻辑
        return {"result": "success"}

# 注册新工具
@router.post("/custom_tool")
async def custom_tool(body: CustomToolRequest):
    tool = CustomTool()
    result = await tool.execute(body.params)
    return result
```

### 2. 插件化架构
- 支持动态加载工具插件
- 插件生命周期管理
- 插件间依赖处理

### 3. 配置扩展
- 支持环境变量配置
- 配置文件热更新
- 多环境配置支持

## 高可用性

### 1. 服务健康检查
```python
@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }
```

### 2. 故障恢复
- 自动重启机制
- 状态持久化
- 故障转移策略

### 3. 负载均衡
- 多实例部署
- 请求分发策略
- 会话保持机制

## 通用性

### 1. 跨平台支持
- 支持Linux、Windows、macOS
- Docker容器化部署
- 云原生架构

### 2. 标准化接口
- RESTful API设计
- OpenAPI规范
- 统一响应格式

### 3. 多语言支持
- Python工具生态
- 外部工具集成
- 协议兼容性
