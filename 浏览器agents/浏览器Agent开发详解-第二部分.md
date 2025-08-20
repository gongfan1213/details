# 浏览器Agent开发详解 - 第三部分：高级特性与实战案例分析

## 目录
1. [高级特性开发](#高级特性开发)
2. [多模态处理](#多模态处理)
3. [分布式架构](#分布式架构)
4. [安全与隐私](#安全与隐私)
5. [实战案例分析](#实战案例分析)
6. [性能调优](#性能调优)
7. [部署与运维](#部署与运维)

## 高级特性开发

### 1. 多Agent协作系统

#### 主从Agent架构
```python
import asyncio
from typing import List, Dict, Any
from dataclasses import dataclass
from enum import Enum

class AgentRole(Enum):
    COORDINATOR = "coordinator"
    NAVIGATOR = "navigator"
    EXTRACTOR = "extractor"
    VALIDATOR = "validator"

@dataclass
class AgentTask:
    role: AgentRole
    description: str
    parameters: Dict[str, Any]
    dependencies: List[str] = None

class MultiAgentSystem:
    def __init__(self):
        self.agents = {}
        self.task_queue = asyncio.Queue()
        self.results = {}
        self.coordinator = None
    
    def register_agent(self, role: AgentRole, agent_func):
        """注册Agent"""
        self.agents[role] = agent_func
    
    async def execute_task(self, task: AgentTask):
        """执行单个任务"""
        if task.role not in self.agents:
            raise ValueError(f"未注册的Agent角色: {task.role}")
        
        # 检查依赖
        if task.dependencies:
            for dep in task.dependencies:
                if dep not in self.results:
                    raise ValueError(f"依赖任务未完成: {dep}")
        
        # 执行任务
        agent_func = self.agents[task.role]
        result = await agent_func(task.parameters, self.results)
        
        # 存储结果
        self.results[task.description] = result
        return result
    
    async def coordinate_tasks(self, tasks: List[AgentTask]):
        """协调多个任务"""
        # 创建任务依赖图
        task_graph = self._build_dependency_graph(tasks)
        
        # 拓扑排序
        execution_order = self._topological_sort(task_graph)
        
        # 按顺序执行任务
        for task_name in execution_order:
            task = next(t for t in tasks if t.description == task_name)
            await self.execute_task(task)
        
        return self.results
    
    def _build_dependency_graph(self, tasks: List[AgentTask]) -> Dict[str, List[str]]:
        """构建依赖图"""
        graph = {}
        for task in tasks:
            graph[task.description] = task.dependencies or []
        return graph
    
    def _topological_sort(self, graph: Dict[str, List[str]]) -> List[str]:
        """拓扑排序"""
        in_degree = {node: 0 for node in graph}
        
        # 计算入度
        for node, deps in graph.items():
            for dep in deps:
                if dep in in_degree:
                    in_degree[dep] += 1
        
        # 拓扑排序
        queue = [node for node, degree in in_degree.items() if degree == 0]
        result = []
        
        while queue:
            node = queue.pop(0)
            result.append(node)
            
            for dep in graph[node]:
                in_degree[dep] -= 1
                if in_degree[dep] == 0:
                    queue.append(dep)
        
        return result

# 使用示例
async def navigator_agent(parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """导航Agent"""
    url = parameters["url"]
    # 实现导航逻辑
    return {"current_url": url, "page_loaded": True}

async def extractor_agent(parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """数据提取Agent"""
    # 从context中获取导航结果
    navigator_result = context.get("导航到目标页面")
    # 实现数据提取逻辑
    return {"extracted_data": ["数据1", "数据2"]}

async def validator_agent(parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """验证Agent"""
    # 从context中获取提取结果
    extractor_result = context.get("提取页面数据")
    # 实现验证逻辑
    return {"validation_result": True, "quality_score": 0.95}

# 使用多Agent系统
async def multi_agent_example():
    system = MultiAgentSystem()
    
    # 注册Agent
    system.register_agent(AgentRole.NAVIGATOR, navigator_agent)
    system.register_agent(AgentRole.EXTRACTOR, extractor_agent)
    system.register_agent(AgentRole.VALIDATOR, validator_agent)
    
    # 定义任务
    tasks = [
        AgentTask(
            role=AgentRole.NAVIGATOR,
            description="导航到目标页面",
            parameters={"url": "https://example.com"}
        ),
        AgentTask(
            role=AgentRole.EXTRACTOR,
            description="提取页面数据",
            parameters={"selectors": [".title", ".content"]},
            dependencies=["导航到目标页面"]
        ),
        AgentTask(
            role=AgentRole.VALIDATOR,
            description="验证数据质量",
            parameters={"min_quality": 0.8},
            dependencies=["提取页面数据"]
        )
    ]
    
    # 执行任务
    results = await system.coordinate_tasks(tasks)
    return results
```

#### 并行Agent执行
```python
class ParallelAgentExecutor:
    def __init__(self, max_concurrent: int = 5):
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)
    
    async def execute_parallel_tasks(self, tasks: List[Dict[str, Any]]) -> List[Any]:
        """并行执行任务"""
        async def execute_single_task(task: Dict[str, Any]):
            async with self.semaphore:
                # 创建Agent实例
                agent = Agent(
                    task=task["prompt"],
                    llm=ChatOpenAI(model=task.get("model", "gpt-4o"))
                )
                return await agent.run()
        
        # 并行执行所有任务
        results = await asyncio.gather(
            *[execute_single_task(task) for task in tasks],
            return_exceptions=True
        )
        
        return results
    
    async def execute_with_dependencies(self, tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """带依赖关系的并行执行"""
        # 构建依赖图
        dependency_graph = self._build_dependency_graph(tasks)
        
        # 分组任务
        task_groups = self._group_tasks_by_dependencies(dependency_graph)
        
        results = {}
        
        # 按组执行任务
        for group in task_groups:
            group_tasks = [task for task in tasks if task["id"] in group]
            
            # 并行执行当前组的任务
            group_results = await self.execute_parallel_tasks(group_tasks)
            
            # 存储结果
            for task, result in zip(group_tasks, group_results):
                results[task["id"]] = result
        
        return results
    
    def _build_dependency_graph(self, tasks: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """构建依赖图"""
        graph = {}
        for task in tasks:
            graph[task["id"]] = task.get("dependencies", [])
        return graph
    
    def _group_tasks_by_dependencies(self, graph: Dict[str, List[str]]) -> List[List[str]]:
        """按依赖关系分组任务"""
        groups = []
        visited = set()
        
        def get_group(node: str, current_group: List[str]):
            if node in visited:
                return
            
            visited.add(node)
            current_group.append(node)
            
            # 检查依赖
            for dep in graph.get(node, []):
                if dep not in visited:
                    get_group(dep, current_group)
        
        for node in graph:
            if node not in visited:
                group = []
                get_group(node, group)
                groups.append(group)
        
        return groups

# 使用并行执行器
async def parallel_execution_example():
    executor = ParallelAgentExecutor(max_concurrent=3)
    
    tasks = [
        {
            "id": "task1",
            "prompt": "访问网站A并提取标题",
            "model": "gpt-4o"
        },
        {
            "id": "task2",
            "prompt": "访问网站B并提取标题",
            "model": "gpt-4o"
        },
        {
            "id": "task3",
            "prompt": "比较两个网站的标题",
            "model": "gpt-4o",
            "dependencies": ["task1", "task2"]
        }
    ]
    
    results = await executor.execute_with_dependencies(tasks)
    return results
```

### 2. 动态任务规划

#### 基于LLM的任务分解
```python
class DynamicTaskPlanner:
    def __init__(self, llm: BaseChatModel):
        self.llm = llm
        self.task_history = []
    
    async def plan_tasks(self, main_task: str) -> List[Dict[str, Any]]:
        """动态规划任务"""
        # 使用LLM分解主任务
        subtasks = await self._decompose_task(main_task)
        
        # 为每个子任务分配资源
        planned_tasks = []
        for i, subtask in enumerate(subtasks):
            planned_task = {
                "id": f"subtask_{i}",
                "description": subtask,
                "priority": self._calculate_priority(subtask),
                "estimated_duration": self._estimate_duration(subtask),
                "required_resources": self._identify_resources(subtask),
                "dependencies": self._identify_dependencies(subtask, subtasks[:i])
            }
            planned_tasks.append(planned_task)
        
        return planned_tasks
    
    async def _decompose_task(self, task: str) -> List[str]:
        """使用LLM分解任务"""
        prompt = f"""
        请将以下任务分解为具体的子任务：
        
        主任务：{task}
        
        请列出完成这个任务需要的具体步骤，每个步骤应该是一个可执行的具体操作。
        格式：每行一个子任务
        
        子任务：
        """
        
        response = await self.llm.generate(prompt)
        
        # 解析响应
        subtasks = [line.strip() for line in response.split('\n') if line.strip()]
        return subtasks
    
    def _calculate_priority(self, task: str) -> int:
        """计算任务优先级"""
        priority_keywords = {
            "关键": 5,
            "重要": 4,
            "必要": 3,
            "可选": 2,
            "辅助": 1
        }
        
        for keyword, priority in priority_keywords.items():
            if keyword in task:
                return priority
        
        return 3  # 默认优先级
    
    def _estimate_duration(self, task: str) -> int:
        """估算任务时长（秒）"""
        # 基于任务复杂度估算
        if "访问" in task and "提取" in task:
            return 30
        elif "填写" in task:
            return 20
        elif "点击" in task:
            return 10
        else:
            return 15
    
    def _identify_resources(self, task: str) -> List[str]:
        """识别所需资源"""
        resources = []
        
        if "浏览器" in task or "访问" in task:
            resources.append("browser")
        
        if "LLM" in task or "分析" in task:
            resources.append("llm")
        
        if "文件" in task or "保存" in task:
            resources.append("filesystem")
        
        return resources
    
    def _identify_dependencies(self, task: str, previous_tasks: List[str]) -> List[str]:
        """识别依赖关系"""
        dependencies = []
        
        # 简单的依赖识别逻辑
        for prev_task in previous_tasks:
            if any(keyword in prev_task for keyword in ["登录", "认证"]) and "登录" in task:
                dependencies.append(prev_task)
            elif any(keyword in prev_task for keyword in ["导航", "访问"]) and "提取" in task:
                dependencies.append(prev_task)
        
        return dependencies
    
    async def execute_planned_tasks(self, planned_tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """执行计划的任务"""
        results = {}
        
        # 按优先级排序
        sorted_tasks = sorted(planned_tasks, key=lambda x: x["priority"], reverse=True)
        
        for task in sorted_tasks:
            try:
                # 检查依赖
                if task["dependencies"]:
                    for dep in task["dependencies"]:
                        if dep not in results:
                            raise Exception(f"依赖任务未完成: {dep}")
                
                # 执行任务
                agent = Agent(
                    task=task["description"],
                    llm=self.llm
                )
                
                result = await agent.run()
                results[task["id"]] = result
                
                # 记录历史
                self.task_history.append({
                    "task": task,
                    "result": result,
                    "timestamp": datetime.now()
                })
                
            except Exception as e:
                results[task["id"]] = {"error": str(e)}
        
        return results

# 使用动态任务规划
async def dynamic_planning_example():
    llm = ChatOpenAI(model="gpt-4o")
    planner = DynamicTaskPlanner(llm)
    
    main_task = "在电商网站搜索笔记本电脑，比较前5个商品的价格和评价，选择性价比最高的商品加入购物车"
    
    # 规划任务
    planned_tasks = await planner.plan_tasks(main_task)
    
    # 执行任务
    results = await planner.execute_planned_tasks(planned_tasks)
    
    return results
```

## 多模态处理

### 1. 视觉理解增强

#### 截图分析系统
```python
import base64
from PIL import Image
import io

class VisualAnalysisSystem:
    def __init__(self, vision_llm: BaseChatModel):
        self.vision_llm = vision_llm
    
    async def analyze_screenshot(self, screenshot: bytes, context: str = "") -> Dict[str, Any]:
        """分析网页截图"""
        # 编码截图
        screenshot_b64 = base64.b64encode(screenshot).decode('utf-8')
        
        # 构建多模态提示
        prompt = f"""
        请分析这个网页截图，并提供以下信息：
        
        1. 页面类型（登录页、商品页、搜索结果页等）
        2. 主要UI元素的位置和状态
        3. 可交互的元素（按钮、链接、输入框等）
        4. 页面内容的主要信息
        5. 建议的下一步操作
        
        上下文：{context}
        
        请以JSON格式返回分析结果。
        """
        
        # 调用多模态LLM
        response = await self.vision_llm.generate_with_image(
            prompt=prompt,
            image=screenshot_b64
        )
        
        # 解析响应
        try:
            analysis = json.loads(response)
            return analysis
        except json.JSONDecodeError:
            return {"error": "无法解析视觉分析结果"}
    
    async def detect_ui_elements(self, screenshot: bytes) -> List[Dict[str, Any]]:
        """检测UI元素"""
        screenshot_b64 = base64.b64encode(screenshot).decode('utf-8')
        
        prompt = """
        请识别这个网页截图中的UI元素，包括：
        
        1. 按钮（button）
        2. 输入框（input）
        3. 链接（link）
        4. 下拉菜单（select）
        5. 复选框（checkbox）
        6. 单选按钮（radio）
        
        对于每个元素，请提供：
        - 元素类型
        - 文本内容
        - 位置坐标（x, y）
        - 是否可见
        - 是否可交互
        
        请以JSON数组格式返回结果。
        """
        
        response = await self.vision_llm.generate_with_image(
            prompt=prompt,
            image=screenshot_b64
        )
        
        try:
            elements = json.loads(response)
            return elements
        except json.JSONDecodeError:
            return []
    
    async def extract_text_from_image(self, screenshot: bytes) -> str:
        """从截图中提取文本"""
        screenshot_b64 = base64.b64encode(screenshot).decode('utf-8')
        
        prompt = """
        请提取这个网页截图中的所有文本内容，包括：
        
        1. 标题和副标题
        2. 正文内容
        3. 按钮和链接文本
        4. 表单标签
        5. 错误信息或提示
        
        请按重要性顺序返回文本内容。
        """
        
        response = await self.vision_llm.generate_with_image(
            prompt=prompt,
            image=screenshot_b64
        )
        
        return response
    
    async def compare_screenshots(self, before: bytes, after: bytes) -> Dict[str, Any]:
        """比较两个截图"""
        before_b64 = base64.b64encode(before).decode('utf-8')
        after_b64 = base64.b64encode(after).decode('utf-8')
        
        prompt = """
        请比较这两个网页截图，识别：
        
        1. 页面变化（新增、删除、修改的内容）
        2. UI元素状态变化
        3. 加载状态变化
        4. 错误信息出现或消失
        
        请以JSON格式返回比较结果。
        """
        
        response = await self.vision_llm.generate_with_images(
            prompt=prompt,
            images=[before_b64, after_b64]
        )
        
        try:
            comparison = json.loads(response)
            return comparison
        except json.JSONDecodeError:
            return {"error": "无法解析比较结果"}

# 集成视觉分析到Agent
class VisionEnhancedAgent:
    def __init__(self, llm: BaseChatModel, vision_llm: BaseChatModel):
        self.llm = llm
        self.vision_system = VisualAnalysisSystem(vision_llm)
        self.browser = None
    
    async def run_with_vision(self, task: str) -> Dict[str, Any]:
        """带视觉增强的运行"""
        if not self.browser:
            self.browser = await playwright.chromium.launch(headless=False)
            self.page = await self.browser.new_page()
        
        results = []
        
        while True:
            # 获取截图
            screenshot = await self.page.screenshot()
            
            # 视觉分析
            visual_analysis = await self.vision_system.analyze_screenshot(
                screenshot, 
                context=f"当前任务：{task}"
            )
            
            # 获取页面状态
            page_state = {
                "url": self.page.url,
                "title": await self.page.title(),
                "visual_analysis": visual_analysis
            }
            
            # 生成下一步动作
            action = await self._generate_action(task, page_state, results)
            
            if action.get("action") == "done":
                break
            
            # 执行动作
            result = await self._execute_action(action)
            results.append({
                "action": action,
                "result": result,
                "visual_analysis": visual_analysis
            })
        
        return {
            "task": task,
            "results": results,
            "final_state": page_state
        }
    
    async def _generate_action(self, task: str, page_state: Dict, history: List) -> Dict[str, Any]:
        """生成下一步动作"""
        prompt = f"""
        基于当前页面状态和历史操作，决定下一步动作：
        
        任务：{task}
        当前URL：{page_state['url']}
        页面标题：{page_state['title']}
        
        视觉分析结果：
        {json.dumps(page_state['visual_analysis'], ensure_ascii=False, indent=2)}
        
        历史操作：
        {json.dumps(history[-3:], ensure_ascii=False, indent=2)}
        
        请返回JSON格式的动作：
        {{
            "action": "click|type|navigate|wait|done",
            "target": "元素选择器或描述",
            "value": "输入值（如果需要）",
            "reason": "选择此动作的原因"
        }}
        """
        
        response = await self.llm.generate(prompt)
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"action": "done", "reason": "无法解析动作"}
    
    async def _execute_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """执行动作"""
        try:
            action_type = action["action"]
            target = action.get("target", "")
            value = action.get("value", "")
            
            if action_type == "click":
                await self.page.click(target)
                return {"success": True, "action": "clicked", "target": target}
            
            elif action_type == "type":
                await self.page.fill(target, value)
                return {"success": True, "action": "typed", "target": target, "value": value}
            
            elif action_type == "navigate":
                await self.page.goto(target)
                return {"success": True, "action": "navigated", "target": target}
            
            elif action_type == "wait":
                await self.page.wait_for_timeout(int(value) * 1000)
                return {"success": True, "action": "waited", "duration": value}
            
            else:
                return {"success": False, "error": f"未知动作类型：{action_type}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
```

### 2. 多模态数据融合

#### 文本与视觉信息融合
```python
class MultimodalDataFusion:
    def __init__(self, llm: BaseChatModel):
        self.llm = llm
    
    async def fuse_text_and_vision(self, text_data: Dict[str, Any], visual_data: Dict[str, Any]) -> Dict[str, Any]:
        """融合文本和视觉数据"""
        prompt = f"""
        请融合以下文本和视觉信息，生成综合理解：
        
        文本数据：
        {json.dumps(text_data, ensure_ascii=False, indent=2)}
        
        视觉数据：
        {json.dumps(visual_data, ensure_ascii=False, indent=2)}
        
        请提供：
        1. 页面内容的综合理解
        2. 可交互元素的完整列表
        3. 页面状态评估
        4. 下一步操作建议
        
        请以JSON格式返回结果。
        """
        
        response = await self.llm.generate(prompt)
        
        try:
            fused_data = json.loads(response)
            return fused_data
        except json.JSONDecodeError:
            return {"error": "无法解析融合结果"}
    
    async def extract_structured_data(self, text: str, screenshot: bytes) -> Dict[str, Any]:
        """提取结构化数据"""
        screenshot_b64 = base64.b64encode(screenshot).decode('utf-8')
        
        prompt = f"""
        请从以下文本和截图中提取结构化数据：
        
        文本内容：
        {text}
        
        请提取：
        1. 产品信息（名称、价格、评分等）
        2. 用户信息（姓名、邮箱、电话等）
        3. 表单字段
        4. 错误信息
        5. 成功状态
        
        请以JSON格式返回提取的数据。
        """
        
        response = await self.llm.generate_with_image(
            prompt=prompt,
            image=screenshot_b64
        )
        
        try:
            structured_data = json.loads(response)
            return structured_data
        except json.JSONDecodeError:
            return {"error": "无法解析结构化数据"}
```

## 分布式架构

### 1. 微服务架构

#### Agent服务拆分
```python
# agent_service.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
import asyncio

app = FastAPI()

class AgentRequest(BaseModel):
    task: str
    model: str = "gpt-4o"
    parameters: Dict[str, Any] = {}

class AgentResponse(BaseModel):
    task_id: str
    status: str
    result: Dict[str, Any] = None
    error: str = None

class AgentService:
    def __init__(self):
        self.active_tasks = {}
        self.task_counter = 0
    
    async def create_task(self, request: AgentRequest) -> str:
        """创建新任务"""
        task_id = f"task_{self.task_counter}"
        self.task_counter += 1
        
        # 启动异步任务
        asyncio.create_task(self._execute_task(task_id, request))
        
        self.active_tasks[task_id] = {
            "status": "running",
            "request": request,
            "result": None,
            "error": None
        }
        
        return task_id
    
    async def _execute_task(self, task_id: str, request: AgentRequest):
        """执行任务"""
        try:
            # 创建Agent
            agent = Agent(
                task=request.task,
                llm=ChatOpenAI(model=request.model)
            )
            
            # 执行任务
            result = await agent.run()
            
            # 更新状态
            self.active_tasks[task_id]["status"] = "completed"
            self.active_tasks[task_id]["result"] = result
            
        except Exception as e:
            self.active_tasks[task_id]["status"] = "failed"
            self.active_tasks[task_id]["error"] = str(e)
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """获取任务状态"""
        if task_id not in self.active_tasks:
            raise HTTPException(status_code=404, detail="任务不存在")
        
        return self.active_tasks[task_id]

# 创建服务实例
agent_service = AgentService()

@app.post("/tasks", response_model=AgentResponse)
async def create_task(request: AgentRequest):
    """创建新任务"""
    task_id = await agent_service.create_task(request)
    return AgentResponse(task_id=task_id, status="created")

@app.get("/tasks/{task_id}")
async def get_task(task_id: str):
    """获取任务状态"""
    return agent_service.get_task_status(task_id)

@app.get("/tasks")
async def list_tasks():
    """列出所有任务"""
    return agent_service.active_tasks
```

#### 浏览器管理服务
```python
# browser_service.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List
import asyncio

app = FastAPI()

class BrowserSession(BaseModel):
    session_id: str
    url: str
    status: str
    created_at: str

class BrowserService:
    def __init__(self):
        self.sessions = {}
        self.browser_pool = []
        self.max_browsers = 10
    
    async def create_session(self, url: str = None) -> str:
        """创建浏览器会话"""
        session_id = f"session_{len(self.sessions)}"
        
        # 创建浏览器实例
        browser = await playwright.chromium.launch(headless=True)
        page = await browser.new_page()
        
        if url:
            await page.goto(url)
        
        self.sessions[session_id] = {
            "browser": browser,
            "page": page,
            "url": url or "",
            "status": "active",
            "created_at": datetime.now().isoformat()
        }
        
        return session_id
    
    async def navigate(self, session_id: str, url: str):
        """导航到指定URL"""
        if session_id not in self.sessions:
            raise HTTPException(status_code=404, detail="会话不存在")
        
        session = self.sessions[session_id]
        await session["page"].goto(url)
        session["url"] = url
    
    async def take_screenshot(self, session_id: str) -> bytes:
        """获取截图"""
        if session_id not in self.sessions:
            raise HTTPException(status_code=404, detail="会话不存在")
        
        session = self.sessions[session_id]
        return await session["page"].screenshot()
    
    async def execute_script(self, session_id: str, script: str) -> Any:
        """执行JavaScript"""
        if session_id not in self.sessions:
            raise HTTPException(status_code=404, detail="会话不存在")
        
        session = self.sessions[session_id]
        return await session["page"].evaluate(script)
    
    async def close_session(self, session_id: str):
        """关闭会话"""
        if session_id not in self.sessions:
            raise HTTPException(status_code=404, detail="会话不存在")
        
        session = self.sessions[session_id]
        await session["browser"].close()
        del self.sessions[session_id]

# 创建服务实例
browser_service = BrowserService()

@app.post("/sessions")
async def create_session(url: str = None):
    """创建浏览器会话"""
    session_id = await browser_service.create_session(url)
    return {"session_id": session_id}

@app.post("/sessions/{session_id}/navigate")
async def navigate(session_id: str, url: str):
    """导航"""
    await browser_service.navigate(session_id, url)
    return {"status": "success"}

@app.get("/sessions/{session_id}/screenshot")
async def get_screenshot(session_id: str):
    """获取截图"""
    screenshot = await browser_service.take_screenshot(session_id)
    return Response(content=screenshot, media_type="image/png")

@app.post("/sessions/{session_id}/execute")
async def execute_script(session_id: str, script: str):
    """执行脚本"""
    result = await browser_service.execute_script(session_id, script)
    return {"result": result}

@app.delete("/sessions/{session_id}")
async def close_session(session_id: str):
    """关闭会话"""
    await browser_service.close_session(session_id)
    return {"status": "closed"}
```

### 2. 消息队列集成

#### Redis消息队列
```python
import redis
import json
import asyncio
from typing import Dict, Any

class MessageQueueManager:
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis = redis.from_url(redis_url)
        self.agent_queue = "agent_tasks"
        self.result_queue = "agent_results"
    
    async def publish_task(self, task: Dict[str, Any]) -> str:
        """发布任务到队列"""
        task_id = f"task_{int(time.time())}"
        task["id"] = task_id
        task["timestamp"] = time.time()
        
        # 发布到队列
        self.redis.lpush(self.agent_queue, json.dumps(task))
        
        return task_id
    
    async def consume_tasks(self, callback):
        """消费任务"""
        while True:
            # 从队列获取任务
            task_data = self.redis.brpop(self.agent_queue, timeout=1)
            
            if task_data:
                task = json.loads(task_data[1])
                await callback(task)
            
            await asyncio.sleep(0.1)
    
    async def publish_result(self, task_id: str, result: Dict[str, Any]):
        """发布结果"""
        result_data = {
            "task_id": task_id,
            "result": result,
            "timestamp": time.time()
        }
        
        self.redis.lpush(self.result_queue, json.dumps(result_data))
    
    async def get_result(self, task_id: str, timeout: int = 30) -> Dict[str, Any]:
        """获取结果"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            # 检查结果队列
            result_data = self.redis.lrange(self.result_queue, 0, -1)
            
            for data in result_data:
                result = json.loads(data)
                if result["task_id"] == task_id:
                    return result["result"]
            
            await asyncio.sleep(0.5)
        
        return None

# 任务处理器
class TaskProcessor:
    def __init__(self, queue_manager: MessageQueueManager):
        self.queue_manager = queue_manager
    
    async def process_task(self, task: Dict[str, Any]):
        """处理任务"""
        try:
            # 创建Agent
            agent = Agent(
                task=task["prompt"],
                llm=ChatOpenAI(model=task.get("model", "gpt-4o"))
            )
            
            # 执行任务
            result = await agent.run()
            
            # 发布结果
            await self.queue_manager.publish_result(task["id"], {
                "success": True,
                "result": result
            })
            
        except Exception as e:
            # 发布错误结果
            await self.queue_manager.publish_result(task["id"], {
                "success": False,
                "error": str(e)
            })

# 使用消息队列
async def distributed_agent_example():
    queue_manager = MessageQueueManager()
    processor = TaskProcessor(queue_manager)
    
    # 启动任务处理器
    asyncio.create_task(
        queue_manager.consume_tasks(processor.process_task)
    )
    
    # 发布任务
    task_id = await queue_manager.publish_task({
        "prompt": "访问百度并搜索Python教程",
        "model": "gpt-4o"
    })
    
    # 等待结果
    result = await queue_manager.get_result(task_id)
    return result
```

## 安全与隐私

### 1. 数据保护

#### 敏感信息过滤
```python
import re
from typing import Dict, Any, List

class DataProtectionManager:
    def __init__(self):
        self.sensitive_patterns = {
            "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            "phone": r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            "credit_card": r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b',
            "ssn": r'\b\d{3}-\d{2}-\d{4}\b',
            "password": r'password["\']?\s*[:=]\s*["\']?[^"\']+["\']?',
            "api_key": r'[a-zA-Z0-9]{32,}',
        }
        
        self.replacement_map = {
            "email": "[EMAIL]",
            "phone": "[PHONE]",
            "credit_card": "[CREDIT_CARD]",
            "ssn": "[SSN]",
            "password": "[PASSWORD]",
            "api_key": "[API_KEY]"
        }
    
    def sanitize_data(self, data: Any) -> Any:
        """清理敏感数据"""
        if isinstance(data, str):
            return self._sanitize_string(data)
        elif isinstance(data, dict):
            return self._sanitize_dict(data)
        elif isinstance(data, list):
            return self._sanitize_list(data)
        else:
            return data
    
    def _sanitize_string(self, text: str) -> str:
        """清理字符串中的敏感信息"""
        sanitized = text
        
        for pattern_name, pattern in self.sensitive_patterns.items():
            replacement = self.replacement_map[pattern_name]
            sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)
        
        return sanitized
    
    def _sanitize_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """清理字典中的敏感信息"""
        sanitized = {}
        
        for key, value in data.items():
            # 跳过敏感键名
            if any(sensitive in key.lower() for sensitive in ["password", "token", "key", "secret"]):
                sanitized[key] = "[SENSITIVE_DATA]"
            else:
                sanitized[key] = self.sanitize_data(value)
        
        return sanitized
    
    def _sanitize_list(self, data: List[Any]) -> List[Any]:
        """清理列表中的敏感信息"""
        return [self.sanitize_data(item) for item in data]
    
    def detect_sensitive_data(self, data: Any) -> List[Dict[str, Any]]:
        """检测敏感数据"""
        detected = []
        
        if isinstance(data, str):
            detected.extend(self._detect_in_string(data))
        elif isinstance(data, dict):
            detected.extend(self._detect_in_dict(data))
        elif isinstance(data, list):
            for item in data:
                detected.extend(self.detect_sensitive_data(item))
        
        return detected
    
    def _detect_in_string(self, text: str) -> List[Dict[str, Any]]:
        """在字符串中检测敏感数据"""
        detected = []
        
        for pattern_name, pattern in self.sensitive_patterns.items():
            matches = re.finditer(pattern, text, flags=re.IGNORECASE)
            for match in matches:
                detected.append({
                    "type": pattern_name,
                    "value": match.group(),
                    "position": match.span(),
                    "replacement": self.replacement_map[pattern_name]
                })
        
        return detected
    
    def _detect_in_dict(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """在字典中检测敏感数据"""
        detected = []
        
        for key, value in data.items():
            # 检查键名
            if any(sensitive in key.lower() for sensitive in ["password", "token", "key", "secret"]):
                detected.append({
                    "type": "sensitive_key",
                    "key": key,
                    "value": str(value)[:10] + "..." if len(str(value)) > 10 else str(value)
                })
            
            # 检查值
            detected.extend(self.detect_sensitive_data(value))
        
        return detected

# 使用数据保护
class SecureAgent:
    def __init__(self, data_protector: DataProtectionManager):
        self.data_protector = data_protector
        self.llm = ChatOpenAI(model="gpt-4o")
    
    async def run_secure(self, task: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """安全运行Agent"""
        # 检测敏感数据
        sensitive_data = self.data_protector.detect_sensitive_data(data)
        
        if sensitive_data:
            print(f"检测到 {len(sensitive_data)} 个敏感数据项")
            for item in sensitive_data:
                print(f"- {item['type']}: {item.get('value', item.get('key', ''))}")
        
        # 清理数据
        sanitized_data = self.data_protector.sanitize_data(data)
        
        # 运行Agent
        agent = Agent(
            task=task,
            llm=self.llm
        )
        
        result = await agent.run()
        
        # 清理结果
        sanitized_result = self.data_protector.sanitize_data(result)
        
        return {
            "result": sanitized_result,
            "sensitive_data_detected": len(sensitive_data),
            "security_warnings": [item["type"] for item in sensitive_data]
        }
```

### 2. 访问控制

#### 基于角色的访问控制
```python
from enum import Enum
from typing import List, Set
import jwt
from datetime import datetime, timedelta

class Permission(Enum):
    READ = "read"
    WRITE = "write"
    EXECUTE = "execute"
    ADMIN = "admin"

class Role(Enum):
    USER = "user"
    DEVELOPER = "developer"
    ADMIN = "admin"

class AccessControlManager:
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
        self.role_permissions = {
            Role.USER: {Permission.READ, Permission.EXECUTE},
            Role.DEVELOPER: {Permission.READ, Permission.WRITE, Permission.EXECUTE},
            Role.ADMIN: {Permission.READ, Permission.WRITE, Permission.EXECUTE, Permission.ADMIN}
        }
        self.user_roles = {}
    
    def create_token(self, user_id: str, role: Role, expires_in: int = 3600) -> str:
        """创建JWT令牌"""
        payload = {
            "user_id": user_id,
            "role": role.value,
            "exp": datetime.utcnow() + timedelta(seconds=expires_in)
        }
        
        return jwt.encode(payload, self.secret_key, algorithm="HS256")
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """验证JWT令牌"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            return payload
        except jwt.ExpiredSignatureError:
            raise ValueError("令牌已过期")
        except jwt.InvalidTokenError:
            raise ValueError("无效令牌")
    
    def has_permission(self, user_id: str, permission: Permission) -> bool:
        """检查用户权限"""
        if user_id not in self.user_roles:
            return False
        
        role = self.user_roles[user_id]
        return permission in self.role_permissions.get(role, set())
    
    def require_permission(self, permission: Permission):
        """权限装饰器"""
        def decorator(func):
            def wrapper(*args, **kwargs):
                # 从参数中获取token
                token = kwargs.get("token") or args[0] if args else None
                
                if not token:
                    raise ValueError("缺少认证令牌")
                
                # 验证令牌
                payload = self.verify_token(token)
                user_id = payload["user_id"]
                role = Role(payload["role"])
                
                # 设置用户角色
                self.user_roles[user_id] = role
                
                # 检查权限
                if not self.has_permission(user_id, permission):
                    raise PermissionError(f"缺少权限: {permission.value}")
                
                return func(*args, **kwargs)
            return wrapper
        return decorator

# 使用访问控制
class SecureAgentService:
    def __init__(self, access_control: AccessControlManager):
        self.access_control = access_control
    
    @AccessControlManager.require_permission(Permission.EXECUTE)
    async def execute_task(self, task: str, token: str) -> Dict[str, Any]:
        """执行任务（需要执行权限）"""
        agent = Agent(
            task=task,
            llm=ChatOpenAI(model="gpt-4o")
        )
        
        result = await agent.run()
        return {"result": result}
    
    @AccessControlManager.require_permission(Permission.READ)
    async def get_task_history(self, token: str) -> List[Dict[str, Any]]:
        """获取任务历史（需要读取权限）"""
        # 实现获取历史记录的逻辑
        return []
    
    @AccessControlManager.require_permission(Permission.ADMIN)
    async def manage_users(self, action: str, user_data: Dict[str, Any], token: str) -> Dict[str, Any]:
        """管理用户（需要管理员权限）"""
        # 实现用户管理逻辑
        return {"status": "success"}

# 使用示例
async def secure_agent_example():
    access_control = AccessControlManager("your-secret-key")
    secure_service = SecureAgentService(access_control)
    
    # 创建用户令牌
    user_token = access_control.create_token("user123", Role.USER)
    admin_token = access_control.create_token("