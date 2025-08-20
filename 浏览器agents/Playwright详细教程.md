# Playwright详细教程 - 基于Browser-Use项目实战

## 目录
1. [环境准备](#环境准备)
2. [基础概念](#基础概念)
3. [核心架构](#核心架构)
4. [实战示例](#实战示例)
5. [高级功能](#高级功能)
6. [最佳实践](#最佳实践)
7. [故障排除](#故障排除)

## 环境准备

### 1. 创建Conda虚拟环境

```bash
# 创建conda虚拟环境
conda create -n browser-agent python=3.11
conda activate browser-agent

# 安装核心依赖
pip install browser-use
pip install playwright
playwright install chromium

# 安装开发工具
pip install pytest
pip install black
pip install mypy
```

### 2. 环境配置

```bash
# 创建.env文件配置API密钥
cat > .env << EOF
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
GEMINI_API_KEY=your_gemini_api_key
EOF
```

### 3. 验证安装

```python
import asyncio
from playwright.async_api import async_playwright

async def test_playwright_installation():
    """测试Playwright安装是否成功"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto('https://example.com')
        title = await page.title()
        print(f"页面标题: {title}")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_playwright_installation())
```

## 基础概念

### 1. Playwright核心组件

#### Browser（浏览器）
- **Chromium**: 默认浏览器，功能最完整
- **Firefox**: 支持，但功能有限
- **WebKit**: Safari引擎，支持有限

#### BrowserContext（浏览器上下文）
- 独立的浏览器会话
- 支持多标签页
- 可配置用户代理、视口等

#### Page（页面）
- 单个标签页
- 主要的交互对象
- 包含DOM操作、网络请求等功能

### 2. Browser-Use架构概览

```
Agent (代理)
├── LLM (语言模型)
├── Controller (控制器)
├── BrowserSession (浏览器会话)
│   ├── BrowserProfile (浏览器配置)
│   ├── Page (页面)
│   └── EventBus (事件总线)
└── DOM Service (DOM服务)
```

## 核心架构

### 1. BrowserSession类详解

```python
from browser_use.browser import BrowserSession, BrowserProfile
from browser_use.browser.types import ViewportSize

# 创建浏览器配置
browser_profile = BrowserProfile(
    headless=False,  # 显示浏览器窗口
    viewport=ViewportSize(width=1200, height=800),
    user_data_dir='~/.config/browseruse/profiles/default',
    stealth=True,  # 启用反检测
    disable_security=False,
    wait_for_network_idle_page_load_time=1,
)

# 创建浏览器会话
browser_session = BrowserSession(
    browser_profile=browser_profile,
    # 可选：连接到远程浏览器
    # cdp_url='ws://localhost:9222'
)
```

### 2. Agent服务架构

```python
from browser_use import Agent
from browser_use.llm import ChatOpenAI
from browser_use.controller import Controller

# 创建LLM实例
llm = ChatOpenAI(model="gpt-4o", temperature=0.1)

# 创建控制器（可选）
controller = Controller()

# 创建Agent
agent = Agent(
    task="访问百度首页并搜索'Python教程'",
    llm=llm,
    browser_session=browser_session,
    controller=controller,
    max_actions_per_step=3,
    max_steps=20
)
```

## 实战示例

### 1. 基础搜索示例

```python
"""
基于 browser-use/examples/getting_started/01_basic_search.py
"""

import asyncio
from browser_use import Agent
from browser_use.llm import ChatOpenAI

async def basic_search_example():
    """基础搜索示例"""
    # 初始化模型
    llm = ChatOpenAI(model='gpt-4o')
    
    # 定义搜索任务
    task = "访问百度首页，搜索'Python教程'，获取前3个搜索结果"
    
    # 创建并运行Agent
    agent = Agent(task=task, llm=llm)
    history = await agent.run()
    
    # 输出结果
    print(f"任务完成，共执行{len(history.steps)}步")
    print(f"最终URL: {history.final_url}")
    print(f"最终内容: {history.final_content[:200]}...")

if __name__ == "__main__":
    asyncio.run(basic_search_example())
```

### 2. 表单填写示例

```python
"""
基于 browser-use/examples/getting_started/02_form_filling.py
"""

import asyncio
from browser_use import Agent
from browser_use.llm import ChatOpenAI

async def form_filling_example():
    """表单填写示例"""
    llm = ChatOpenAI(model='gpt-4o')
    
    task = """
    访问 https://httpbin.org/forms/post 并填写联系表单：
    - 客户姓名: 张三
    - 电话: 138-1234-5678
    - 邮箱: zhangsan@example.com
    - 尺寸: 中号
    - 配料: 奶酪
    - 配送时间: 现在
    - 备注: 这是一个测试表单提交
    
    然后提交表单并告诉我响应结果。
    """
    
    agent = Agent(task=task, llm=llm)
    history = await agent.run()
    
    print(f"表单提交结果: {history.final_content}")

if __name__ == "__main__":
    asyncio.run(form_filling_example())
```

### 3. 数据提取示例

```python
"""
基于 browser-use/examples/getting_started/03_data_extraction.py
"""

import asyncio
from browser_use import Agent
from browser_use.llm import ChatOpenAI

async def data_extraction_example():
    """数据提取示例"""
    llm = ChatOpenAI(model='gpt-4o')
    
    task = """
    访问 https://quotes.toscrape.com/ 并提取以下信息：
    - 页面上的前5个名言
    - 每个名言的作者
    - 每个名言关联的标签
    
    以清晰的格式呈现信息：
    名言1: "[名言内容]" - 作者: [作者名] - 标签: [标签1, 标签2, ...]
    名言2: "[名言内容]" - 作者: [作者名] - 标签: [标签1, 标签2, ...]
    等等。
    """
    
    agent = Agent(task=task, llm=llm)
    history = await agent.run()
    
    print("提取的数据:")
    print(history.final_content)

if __name__ == "__main__":
    asyncio.run(data_extraction_example())
```

### 4. 结构化输出示例

```python
"""
基于 browser-use/examples/features/custom_output.py
"""

import asyncio
from pydantic import BaseModel
from browser_use import Agent, Controller
from browser_use.llm import ChatOpenAI

# 定义数据结构
class Post(BaseModel):
    post_title: str
    post_url: str
    num_comments: int
    hours_since_post: int

class Posts(BaseModel):
    posts: list[Post]

async def structured_output_example():
    """结构化输出示例"""
    # 创建控制器并指定输出模型
    controller = Controller(output_model=Posts)
    
    task = '访问Hacker News的Show HN页面，获取前5个帖子信息'
    llm = ChatOpenAI(model='gpt-4o')
    
    agent = Agent(task=task, llm=llm, controller=controller)
    history = await agent.run()
    
    # 解析结构化结果
    result = history.final_result()
    if result:
        parsed: Posts = Posts.model_validate_json(result)
        
        for post in parsed.posts:
            print('\n--------------------------------')
            print(f'标题:            {post.post_title}')
            print(f'URL:              {post.post_url}')
            print(f'评论数:         {post.num_comments}')
            print(f'发布时间: {post.hours_since_post}小时前')
    else:
        print('没有获取到结果')

if __name__ == "__main__":
    asyncio.run(structured_output_example())
```

## 高级功能

### 1. 自定义动作开发

```python
"""
基于 browser-use/examples/custom-functions/ 目录
"""

from browser_use.controller import Controller
from browser_use.core.views import ActionResult
from playwright.async_api import Page
import asyncio

# 创建控制器
controller = Controller()

@controller.registry.action("自定义搜索动作")
async def custom_search(query: str, page: Page):
    """在指定网站执行搜索"""
    try:
        # 导航到搜索页面
        await page.goto("https://www.example.com/search")
        
        # 等待搜索框加载
        await page.wait_for_selector("#search-input", timeout=10000)
        
        # 填写搜索框
        await page.fill("#search-input", query)
        
        # 点击搜索按钮
        await page.click("#search-button")
        
        # 等待结果加载
        await page.wait_for_selector(".search-results", timeout=10000)
        
        # 提取搜索结果
        results = await page.query_selector_all(".result-item")
        extracted_data = []
        
        for result in results[:5]:  # 取前5个结果
            title_elem = await result.query_selector(".title")
            title_text = await title_elem.text_content() if title_elem else ""
            
            link_elem = await result.query_selector("a")
            link_href = await link_elem.get_attribute("href") if link_elem else ""
            
            desc_elem = await result.query_selector(".description")
            desc_text = await desc_elem.text_content() if desc_elem else ""
            
            extracted_data.append({
                "title": title_text.strip(),
                "url": link_href,
                "description": desc_text.strip()
            })
        
        return ActionResult(
            extracted_content=extracted_data,
            include_in_memory=True,
            success=True
        )
        
    except Exception as e:
        return ActionResult(
            success=False,
            error=str(e),
            include_in_memory=True
        )

# 使用自定义动作
async def use_custom_action():
    from browser_use import Agent
    from browser_use.llm import ChatOpenAI
    
    agent = Agent(
        task="使用自定义搜索功能搜索'机器学习教程'",
        llm=ChatOpenAI(model="gpt-4o"),
        controller=controller
    )
    
    history = await agent.run()
    return history
```

### 2. 多任务处理

```python
"""
基于 browser-use/examples/features/multiple_tasks.py
"""

import asyncio
from browser_use import Agent
from browser_use.browser import BrowserSession, BrowserProfile
from browser_use.llm import ChatOpenAI

async def multiple_tasks_example():
    """多任务处理示例"""
    # 创建浏览器配置
    browser_profile = BrowserProfile(
        headless=False,
        viewport={'width': 1502, 'height': 853},
        ignore_https_errors=True,
    )
    
    # 创建浏览器会话
    browser_session = BrowserSession(browser_profile=browser_profile)
    await browser_session.start()
    
    llm = ChatOpenAI(model='gpt-4o')
    
    agent = Agent(
        browser_session=browser_session,
        task='访问 https://browser-use.com/',
        llm=llm,
    )
    
    try:
        # 执行第一个任务
        result = await agent.run()
        print(f'第一个任务{"成功" if result.is_successful else "失败"}')
        
        if result.is_successful:
            # 添加新任务
            agent.add_new_task('导航到文档页面')
            
            # 执行第二个任务
            result = await agent.run()
            print(f'第二个任务{"成功" if result.is_successful else "失败"}')
            
            # 交互式添加任务
            while True:
                next_task = input('输入下一个任务或留空退出\n> ')
                
                if not next_task.strip():
                    print('退出...')
                    break
                
                agent.add_new_task(next_task)
                result = await agent.run()
                
                print(f"任务 '{next_task}' {'成功' if result.is_successful else '失败'}")
                
                if not result.is_successful:
                    print('任务失败，请重试。')
                    continue
                    
    finally:
        await browser_session.stop()

if __name__ == "__main__":
    asyncio.run(multiple_tasks_example())
```

### 3. 反检测浏览器

```python
"""
基于 browser-use/examples/browser/stealth.py
"""

import asyncio
from browser_use.browser import BrowserSession, BrowserProfile
from browser_use.browser.events import NavigateToUrlEvent

async def stealth_browser_example():
    """反检测浏览器示例"""
    print('\n\n普通浏览器:')
    # 默认Playwright Chromium浏览器
    normal_browser = BrowserSession(
        browser_profile=BrowserProfile(
            user_data_dir=None,
            headless=False,
            stealth=False,
        )
    )
    await normal_browser.start()
    
    # 导航到反检测测试网站
    nav_event = normal_browser.event_bus.dispatch(
        NavigateToUrlEvent(url='https://abrahamjuliot.github.io/creepjs/', new_tab=True)
    )
    await nav_event
    await asyncio.sleep(5)
    
    await normal_browser.kill()
    
    print('\n\n反检测浏览器:')
    stealth_browser = BrowserSession(
        browser_profile=BrowserProfile(
            user_data_dir='~/.config/browseruse/profiles/stealth',
            stealth=True,  # 启用反检测
            headless=False,
            disable_security=False,
            deterministic_rendering=False,
        )
    )
    await stealth_browser.start()
    
    # 导航到反检测测试网站
    nav_event = stealth_browser.event_bus.dispatch(
        NavigateToUrlEvent(url='https://abrahamjuliot.github.io/creepjs/', new_tab=True)
    )
    await nav_event
    await asyncio.sleep(5)
    
    await stealth_browser.kill()

if __name__ == "__main__":
    asyncio.run(stealth_browser_example())
```

### 4. 使用Brave浏览器

```python
"""
基于 browser-use/examples/browser/stealth.py
"""

import asyncio
from pathlib import Path
from browser_use.browser import BrowserSession, BrowserProfile

async def brave_browser_example():
    """使用Brave浏览器示例"""
    brave_path = '/Applications/Brave Browser.app/Contents/MacOS/Brave Browser'
    
    if Path(brave_path).exists():
        brave_browser = BrowserSession(
            executable_path=brave_path,
            browser_profile=BrowserProfile(
                user_data_dir='~/.config/browseruse/profiles/brave',
                headless=False,
                stealth=True,
            )
        )
        await brave_browser.start()
        
        # 执行任务
        from browser_use import Agent
        from browser_use.llm import ChatOpenAI
        
        agent = Agent(
            browser_session=brave_browser,
            task="访问百度首页并搜索'Brave浏览器'",
            llm=ChatOpenAI(model="gpt-4o")
        )
        
        history = await agent.run()
        print(f"使用Brave浏览器完成任务: {history.final_url}")
        
        await brave_browser.kill()
    else:
        print("Brave浏览器未找到")

if __name__ == "__main__":
    asyncio.run(brave_browser_example())
```

## 最佳实践

### 1. 错误处理和重试机制

```python
import asyncio
from typing import Callable, Any
from functools import wraps

class RetryManager:
    def __init__(self, max_retries: int = 3, base_delay: float = 1.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
    
    async def retry_with_backoff(
        self, 
        func: Callable, 
        *args, 
        **kwargs
    ) -> Any:
        """指数退避重试机制"""
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)
                return result
                
            except Exception as e:
                last_exception = e
                print(f"尝试 {attempt + 1}/{self.max_retries} 失败: {e}")
                
                if attempt < self.max_retries - 1:
                    delay = self.base_delay * (2 ** attempt)
                    print(f"等待 {delay} 秒后重试...")
                    await asyncio.sleep(delay)
        
        raise last_exception

# 装饰器版本
def retry_on_failure(max_retries: int = 3, base_delay: float = 1.0):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            retry_manager = RetryManager(max_retries, base_delay)
            return await retry_manager.retry_with_backoff(func, *args, **kwargs)
        return wrapper
    return decorator

# 使用示例
@retry_on_failure(max_retries=3, base_delay=1.0)
async def reliable_web_scraping():
    """可靠的网页抓取"""
    from browser_use import Agent
    from browser_use.llm import ChatOpenAI
    
    agent = Agent(
        task="访问不稳定的网站并提取数据",
        llm=ChatOpenAI(model="gpt-4o")
    )
    
    return await agent.run()
```

### 2. 资源管理

```python
import asyncio
from contextlib import asynccontextmanager
from browser_use.browser import BrowserSession, BrowserProfile

@asynccontextmanager
async def managed_browser_session():
    """管理浏览器会话的上下文管理器"""
    browser_session = None
    try:
        browser_session = BrowserSession(
            browser_profile=BrowserProfile(
                headless=False,
                stealth=True
            )
        )
        await browser_session.start()
        yield browser_session
    finally:
        if browser_session:
            await browser_session.stop()

async def safe_browser_operation():
    """安全的浏览器操作"""
    async with managed_browser_session() as browser_session:
        from browser_use import Agent
        from browser_use.llm import ChatOpenAI
        
        agent = Agent(
            browser_session=browser_session,
            task="执行安全的浏览器操作",
            llm=ChatOpenAI(model="gpt-4o")
        )
        
        return await agent.run()
```

### 3. 性能优化

```python
import asyncio
from browser_use.browser import BrowserProfile

async def optimized_browser_config():
    """优化的浏览器配置"""
    # 性能优化配置
    browser_profile = BrowserProfile(
        headless=True,  # 无头模式提高性能
        viewport={'width': 1200, 'height': 800},
        wait_for_network_idle_page_load_time=0.5,  # 减少等待时间
        disable_security=True,  # 禁用安全限制提高速度
        args=[
            '--no-sandbox',
            '--disable-dev-shm-usage',
            '--disable-gpu',
            '--disable-web-security',
            '--disable-features=VizDisplayCompositor',
        ]
    )
    
    from browser_use import Agent
    from browser_use.llm import ChatOpenAI
    
    agent = Agent(
        task="高性能网页抓取任务",
        llm=ChatOpenAI(model="gpt-4o"),
        browser_session=BrowserSession(browser_profile=browser_profile),
        max_actions_per_step=5,  # 增加每步动作数
        max_steps=10  # 限制最大步数
    )
    
    return await agent.run()
```

## 故障排除

### 1. 常见错误及解决方案

#### 浏览器启动失败
```python
# 问题：浏览器启动失败
# 解决方案：
browser_profile = BrowserProfile(
    headless=True,  # 尝试无头模式
    args=['--no-sandbox', '--disable-dev-shm-usage'],  # 添加启动参数
)
```

#### 页面加载超时
```python
# 问题：页面加载超时
# 解决方案：
browser_profile = BrowserProfile(
    wait_for_network_idle_page_load_time=5,  # 增加等待时间
    timeout=30000,  # 设置超时时间
)
```

#### 元素定位失败
```python
# 问题：元素定位失败
# 解决方案：使用更灵活的选择器
@controller.registry.action("灵活元素点击")
async def flexible_click(selector: str, page: Page):
    try:
        # 尝试多种选择器策略
        selectors = [
            selector,
            f"[data-testid='{selector}']",
            f"[aria-label='{selector}']",
            f"text={selector}",
        ]
        
        for sel in selectors:
            try:
                await page.click(sel, timeout=5000)
                return ActionResult(success=True)
            except:
                continue
        
        return ActionResult(success=False, error="元素未找到")
    except Exception as e:
        return ActionResult(success=False, error=str(e))
```

### 2. 调试技巧

```python
import logging
from browser_use.browser import BrowserSession, BrowserProfile

# 启用详细日志
logging.basicConfig(level=logging.DEBUG)

async def debug_browser_session():
    """调试浏览器会话"""
    browser_profile = BrowserProfile(
        headless=False,  # 显示浏览器窗口便于调试
        slow_mo=1000,  # 放慢操作速度便于观察
    )
    
    browser_session = BrowserSession(browser_profile=browser_profile)
    await browser_session.start()
    
    # 获取当前页面进行调试
    page = await browser_session.get_current_page()
    
    # 启用详细日志
    page.on("console", lambda msg: print(f"Console: {msg.text}"))
    page.on("pageerror", lambda err: print(f"Page Error: {err}"))
    
    # 执行任务
    from browser_use import Agent
    from browser_use.llm import ChatOpenAI
    
    agent = Agent(
        browser_session=browser_session,
        task="调试任务",
        llm=ChatOpenAI(model="gpt-4o")
    )
    
    try:
        history = await agent.run()
        print(f"调试完成: {history.final_url}")
    except Exception as e:
        print(f"调试错误: {e}")
    finally:
        await browser_session.stop()
```

### 3. 性能监控

```python
import time
import asyncio
from browser_use import Agent
from browser_use.llm import ChatOpenAI

async def performance_monitoring():
    """性能监控示例"""
    start_time = time.time()
    
    agent = Agent(
        task="性能测试任务",
        llm=ChatOpenAI(model="gpt-4o")
    )
    
    try:
        history = await agent.run()
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        print(f"任务执行时间: {execution_time:.2f}秒")
        print(f"执行步数: {len(history.steps)}")
        print(f"平均每步时间: {execution_time/len(history.steps):.2f}秒")
        
        return history
    except Exception as e:
        print(f"性能测试失败: {e}")
        raise
```

## 总结

本教程详细介绍了基于Browser-Use项目的Playwright使用方法和最佳实践。通过实际代码示例，展示了从基础操作到高级功能的完整开发流程。

### 关键要点：

1. **环境配置**: 正确设置Conda虚拟环境和依赖
2. **架构理解**: 掌握Browser-Use的核心组件和架构
3. **实战应用**: 通过实际示例学习各种使用场景
4. **高级功能**: 自定义动作、反检测、多任务处理等
5. **最佳实践**: 错误处理、资源管理、性能优化
6. **故障排除**: 常见问题的解决方案和调试技巧

通过本教程的学习，您应该能够熟练使用Playwright进行网页自动化开发，并能够构建复杂的浏览器Agent应用。
