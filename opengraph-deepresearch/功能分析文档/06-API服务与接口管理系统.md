# API服务与接口管理系统

## 功能概述

BluePlan Research的API服务与接口管理系统基于FastAPI框架构建，提供RESTful API接口、流式响应、中间件管理、路由控制等功能。系统支持多种认证方式、请求限流、错误处理、监控告警等企业级特性。

## 技术方案支撑

### 1. FastAPI应用架构

#### 应用初始化
```python
# apis/app.py
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
import uvicorn
import asyncio
import json

class BluePlanAPI:
    def __init__(self):
        self.app = FastAPI(
            title="BluePlan Research API",
            description="面向社交媒体内容创作的Gen-AI Agent系统",
            version="2.0.0",
            docs_url="/docs",
            redoc_url="/redoc"
        )
        
        self.setup_middleware()
        self.setup_routes()
        self.setup_exception_handlers()
    
    def setup_middleware(self):
        """设置中间件"""
        # CORS中间件
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # 可信主机中间件
        self.app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["*"]
        )
        
        # 自定义中间件
        self.app.add_middleware(RequestLoggingMiddleware)
        self.app.add_middleware(RateLimitMiddleware)
        self.app.add_middleware(AuthenticationMiddleware)
    
    def setup_routes(self):
        """设置路由"""
        # 健康检查
        self.app.get("/health")(self.health_check)
        self.app.get("/health/ready")(self.ready_check)
        self.app.get("/health/metrics")(self.metrics)
        
        # 核心API接口
        self.app.post("/novachat")(self.novachat_stream)
        self.app.post("/loomichat")(self.loomichat_stream)
        self.app.post("/chat")(self.chat_stream)
        
        # 管理接口
        self.app.get("/api/config")(self.get_config)
        self.app.put("/api/config")(self.update_config)
        self.app.get("/api/stats")(self.get_stats)
        
        # Token统计接口
        self.app.get("/api/token-stats/daily")(self.get_daily_token_stats)
        self.app.get("/api/token-stats/monthly")(self.get_monthly_token_stats)
        self.app.get("/api/token-stats/user-ranking")(self.get_user_token_ranking)
        self.app.get("/api/token-stats/dashboard")(self.get_token_dashboard)
    
    async def health_check(self):
        """健康检查"""
        return {"status": "healthy", "timestamp": datetime.now().isoformat()}
    
    async def ready_check(self):
        """就绪检查"""
        # 检查关键服务是否就绪
        checks = {
            "redis": await self.check_redis_connection(),
            "llm": await self.check_llm_connection(),
            "database": await self.check_database_connection()
        }
        
        is_ready = all(checks.values())
        return {
            "status": "ready" if is_ready else "not_ready",
            "checks": checks
        }
    
    async def metrics(self):
        """系统指标"""
        return {
            "requests_total": self.get_request_count(),
            "active_connections": self.get_active_connections(),
            "memory_usage": self.get_memory_usage(),
            "cpu_usage": self.get_cpu_usage()
        }
```

#### 流式响应处理
```python
    async def novachat_stream(self, request: Request):
        """Nova3模式的流式聊天接口"""
        try:
            # 解析请求数据
            request_data = await request.json()
            
            # 验证请求数据
            validated_data = self.validate_request(request_data)
            
            # 创建流式响应
            return StreamingResponse(
                self.generate_nova3_stream(validated_data),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "*"
                }
            )
        except Exception as e:
            return JSONResponse(
                status_code=400,
                content={"error": str(e), "type": "validation_error"}
            )
    
    async def generate_nova3_stream(self, request_data):
        """生成Nova3流式响应"""
        try:
            # 初始化Nova3 Supervisor
            supervisor = Nova3Supervisor()
            
            # 流式处理请求
            async for event in supervisor.process_request_stream(request_data):
                # 格式化SSE事件
                sse_event = self.format_sse_event(event)
                yield sse_event
                
        except Exception as e:
            # 发送错误事件
            error_event = {
                "event_type": "error",
                "agent_source": "api_server",
                "timestamp": datetime.now().isoformat(),
                "payload": {
                    "error": str(e),
                    "error_type": type(e).__name__
                }
            }
            yield self.format_sse_event(error_event)
    
    def format_sse_event(self, event):
        """格式化SSE事件"""
        event_data = {
            "event_type": event.get("event_type", "llm_chunk"),
            "agent_source": event.get("agent_source", "unknown"),
            "timestamp": event.get("timestamp"),
            "payload": event.get("payload", {})
        }
        
        return f"data: {json.dumps(event_data, ensure_ascii=False)}\n\n"
```

### 2. 中间件系统

#### 请求日志中间件
```python
class RequestLoggingMiddleware:
    def __init__(self, app):
        self.app = app
        self.logger = logging.getLogger(__name__)
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            # 记录请求开始
            start_time = time.time()
            request_id = str(uuid.uuid4())
            
            # 添加请求ID到scope
            scope["request_id"] = request_id
            
            # 记录请求信息
            self.log_request_start(scope, request_id)
            
            # 处理请求
            await self.app(scope, receive, send)
            
            # 记录请求结束
            end_time = time.time()
            duration = end_time - start_time
            self.log_request_end(request_id, duration)
    
    def log_request_start(self, scope, request_id):
        """记录请求开始"""
        self.logger.info(
            f"Request started - ID: {request_id}, "
            f"Method: {scope['method']}, "
            f"Path: {scope['path']}, "
            f"Client: {scope.get('client', ['unknown', 0])}"
        )
    
    def log_request_end(self, request_id, duration):
        """记录请求结束"""
        self.logger.info(
            f"Request completed - ID: {request_id}, "
            f"Duration: {duration:.3f}s"
        )
```

#### 限流中间件
```python
class RateLimitMiddleware:
    def __init__(self, app):
        self.app = app
        self.redis_client = redis.Redis()
        self.rate_limits = {
            "default": {"requests": 100, "window": 60},  # 每分钟100次
            "chat": {"requests": 10, "window": 60},      # 每分钟10次
            "admin": {"requests": 1000, "window": 60}    # 每分钟1000次
        }
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            # 获取客户端标识
            client_id = self.get_client_id(scope)
            
            # 确定限流规则
            rate_limit = self.get_rate_limit(scope["path"])
            
            # 检查限流
            if not await self.check_rate_limit(client_id, rate_limit):
                # 返回429状态码
                await self.send_rate_limit_response(send)
                return
            
            # 继续处理请求
            await self.app(scope, receive, send)
    
    def get_client_id(self, scope):
        """获取客户端标识"""
        # 优先使用用户ID
        headers = dict(scope["headers"])
        user_id = headers.get(b"x-user-id", b"anonymous").decode()
        
        if user_id != "anonymous":
            return f"user:{user_id}"
        
        # 使用IP地址
        client = scope.get("client", ["unknown", 0])
        return f"ip:{client[0]}"
    
    def get_rate_limit(self, path):
        """获取限流规则"""
        if path.startswith("/chat") or path.startswith("/novachat") or path.startswith("/loomichat"):
            return self.rate_limits["chat"]
        elif path.startswith("/admin"):
            return self.rate_limits["admin"]
        else:
            return self.rate_limits["default"]
    
    async def check_rate_limit(self, client_id, rate_limit):
        """检查限流"""
        key = f"rate_limit:{client_id}"
        current = await self.redis_client.incr(key)
        
        if current == 1:
            await self.redis_client.expire(key, rate_limit["window"])
        
        return current <= rate_limit["requests"]
    
    async def send_rate_limit_response(self, send):
        """发送限流响应"""
        response = {
            "status": "error",
            "message": "Rate limit exceeded",
            "retry_after": 60
        }
        
        await send({
            "type": "http.response.start",
            "status": 429,
            "headers": [
                (b"content-type", b"application/json"),
                (b"retry-after", b"60")
            ]
        })
        
        await send({
            "type": "http.response.body",
            "body": json.dumps(response).encode()
        })
```

#### 认证中间件
```python
class AuthenticationMiddleware:
    def __init__(self, app):
        self.app = app
        self.auth_service = AuthService()
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            # 检查是否需要认证
            if self.requires_authentication(scope["path"]):
                # 验证认证信息
                auth_result = await self.authenticate_request(scope)
                
                if not auth_result["authenticated"]:
                    # 返回401状态码
                    await self.send_unauthorized_response(send, auth_result["message"])
                    return
                
                # 添加用户信息到scope
                scope["user"] = auth_result["user"]
            
            # 继续处理请求
            await self.app(scope, receive, send)
    
    def requires_authentication(self, path):
        """检查路径是否需要认证"""
        public_paths = [
            "/health",
            "/health/ready",
            "/health/metrics",
            "/docs",
            "/redoc",
            "/openapi.json"
        ]
        
        return not any(path.startswith(public_path) for public_path in public_paths)
    
    async def authenticate_request(self, scope):
        """认证请求"""
        headers = dict(scope["headers"])
        
        # 检查Authorization头
        auth_header = headers.get(b"authorization", b"").decode()
        
        if not auth_header.startswith("Bearer "):
            return {
                "authenticated": False,
                "message": "Missing or invalid authorization header"
            }
        
        token = auth_header[7:]  # 移除"Bearer "前缀
        
        try:
            # 验证token
            user = await self.auth_service.verify_token(token)
            return {
                "authenticated": True,
                "user": user
            }
        except Exception as e:
            return {
                "authenticated": False,
                "message": str(e)
            }
    
    async def send_unauthorized_response(self, send, message):
        """发送未授权响应"""
        response = {
            "status": "error",
            "message": message,
            "code": "UNAUTHORIZED"
        }
        
        await send({
            "type": "http.response.start",
            "status": 401,
            "headers": [(b"content-type", b"application/json")]
        })
        
        await send({
            "type": "http.response.body",
            "body": json.dumps(response).encode()
        })
```

### 3. 路由管理系统

#### 路由注册器
```python
class RouteRegistry:
    def __init__(self):
        self.routes = {}
        self.middlewares = {}
    
    def register_route(self, path: str, handler, methods: List[str] = None, 
                      middleware: List[str] = None, auth_required: bool = True):
        """注册路由"""
        if methods is None:
            methods = ["GET"]
        
        self.routes[path] = {
            "handler": handler,
            "methods": methods,
            "middleware": middleware or [],
            "auth_required": auth_required
        }
    
    def register_middleware(self, name: str, middleware_class):
        """注册中间件"""
        self.middlewares[name] = middleware_class
    
    def get_route(self, path: str):
        """获取路由信息"""
        return self.routes.get(path)
    
    def get_all_routes(self):
        """获取所有路由"""
        return self.routes
    
    def apply_routes_to_app(self, app):
        """将路由应用到FastAPI应用"""
        for path, route_info in self.routes.items():
            handler = route_info["handler"]
            methods = route_info["methods"]
            
            # 根据方法注册路由
            for method in methods:
                if method == "GET":
                    app.get(path)(handler)
                elif method == "POST":
                    app.post(path)(handler)
                elif method == "PUT":
                    app.put(path)(handler)
                elif method == "DELETE":
                    app.delete(path)(handler)
```

## 业务功能实现

### 1. 核心API接口

#### Nova3聊天接口
```python
async def novachat_stream(self, request: Request):
    """Nova3模式的流式聊天接口"""
    try:
        # 解析和验证请求
        request_data = await request.json()
        validated_data = self.validate_novachat_request(request_data)
        
        # 获取用户信息
        user = request.scope.get("user", {})
        validated_data["user"] = user
        
        # 创建流式响应
        return StreamingResponse(
            self.process_novachat_request(validated_data),
            media_type="text/event-stream",
            headers=self.get_stream_headers()
        )
    except ValidationError as e:
        return JSONResponse(
            status_code=400,
            content={"error": "请求数据验证失败", "details": e.errors()}
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": "服务器内部错误", "message": str(e)}
        )

def validate_novachat_request(self, data):
    """验证Nova3请求数据"""
    required_fields = ["user_id", "session_id", "request_data"]
    
    for field in required_fields:
        if field not in data:
            raise ValidationError(f"缺少必需字段: {field}")
    
    # 验证request_data
    request_data = data["request_data"]
    if "query" not in request_data:
        raise ValidationError("缺少查询内容")
    
    return data

async def process_novachat_request(self, request_data):
    """处理Nova3请求"""
    try:
        # 初始化Nova3 Supervisor
        supervisor = Nova3Supervisor()
        
        # 发送开始事件
        yield self.format_sse_event({
            "event_type": "session_start",
            "agent_source": "nova3_supervisor",
            "timestamp": datetime.now().isoformat(),
            "payload": {
                "session_id": request_data["session_id"],
                "status": "started"
            }
        })
        
        # 流式处理请求
        async for event in supervisor.process_request_stream(request_data):
            yield self.format_sse_event(event)
        
        # 发送结束事件
        yield self.format_sse_event({
            "event_type": "session_end",
            "agent_source": "nova3_supervisor",
            "timestamp": datetime.now().isoformat(),
            "payload": {
                "session_id": request_data["session_id"],
                "status": "completed"
            }
        })
        
    except Exception as e:
        # 发送错误事件
        yield self.format_sse_event({
            "event_type": "error",
            "agent_source": "nova3_supervisor",
            "timestamp": datetime.now().isoformat(),
            "payload": {
                "error": str(e),
                "error_type": type(e).__name__
            }
        })
```

#### Loomi聊天接口
```python
async def loomichat_stream(self, request: Request):
    """Loomi模式的流式聊天接口"""
    try:
        # 解析和验证请求
        request_data = await request.json()
        validated_data = self.validate_loomichat_request(request_data)
        
        # 获取用户信息
        user = request.scope.get("user", {})
        validated_data["user"] = user
        
        # 创建流式响应
        return StreamingResponse(
            self.process_loomichat_request(validated_data),
            media_type="text/event-stream",
            headers=self.get_stream_headers()
        )
    except ValidationError as e:
        return JSONResponse(
            status_code=400,
            content={"error": "请求数据验证失败", "details": e.errors()}
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": "服务器内部错误", "message": str(e)}
        )

async def process_loomichat_request(self, request_data):
    """处理Loomi请求"""
    try:
        # 初始化Loomi Concierge
        concierge = LoomiConcierge()
        
        # 发送开始事件
        yield self.format_sse_event({
            "event_type": "session_start",
            "agent_source": "loomi_concierge",
            "timestamp": datetime.now().isoformat(),
            "payload": {
                "session_id": request_data["session_id"],
                "status": "started"
            }
        })
        
        # 流式处理请求
        async for event in concierge.process_request_stream(request_data):
            yield self.format_sse_event(event)
        
        # 发送结束事件
        yield self.format_sse_event({
            "event_type": "session_end",
            "agent_source": "loomi_concierge",
            "timestamp": datetime.now().isoformat(),
            "payload": {
                "session_id": request_data["session_id"],
                "status": "completed"
            }
        })
        
    except Exception as e:
        # 发送错误事件
        yield self.format_sse_event({
            "event_type": "error",
            "agent_source": "loomi_concierge",
            "timestamp": datetime.now().isoformat(),
            "payload": {
                "error": str(e),
                "error_type": type(e).__name__
            }
        })
```

### 2. Token统计接口

#### 每日Token统计
```python
async def get_daily_token_stats(self, days: int = 7):
    """获取每日Token统计"""
    try:
        from utils.token_accumulator import token_accumulator
        
        stats = await token_accumulator.get_daily_token_stats(days)
        
        return {
            "status": "success",
            "data": stats,
            "period": f"最近{days}天"
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": "获取Token统计失败", "message": str(e)}
        )

async def get_monthly_token_stats(self, months: int = 3):
    """获取月度Token统计"""
    try:
        from utils.token_accumulator import token_accumulator
        
        stats = await token_accumulator.get_monthly_token_stats(months)
        
        return {
            "status": "success",
            "data": stats,
            "period": f"最近{months}个月"
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": "获取Token统计失败", "message": str(e)}
        )

async def get_user_token_ranking(self, target_date: str = None, top_n: int = 10):
    """获取用户Token排行榜"""
    try:
        from utils.token_accumulator import token_accumulator
        
        if target_date is None:
            target_date = datetime.now().strftime("%Y-%m-%d")
        
        ranking = await token_accumulator.get_daily_user_token_ranking(
            target_date=target_date, 
            top_n=top_n
        )
        
        return {
            "status": "success",
            "data": ranking,
            "date": target_date,
            "top_n": top_n
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": "获取用户排行榜失败", "message": str(e)}
        )

async def get_token_dashboard(self):
    """获取Token统计仪表盘数据"""
    try:
        from utils.token_accumulator import token_accumulator
        
        dashboard_data = await token_accumulator.get_token_dashboard_data()
        
        return {
            "status": "success",
            "data": dashboard_data
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": "获取仪表盘数据失败", "message": str(e)}
        )
```

### 3. 配置管理接口

#### 配置查询和更新
```python
async def get_config(self, request: Request):
    """获取系统配置"""
    try:
        # 检查权限
        user = request.scope.get("user", {})
        if not self.has_config_permission(user):
            return JSONResponse(
                status_code=403,
                content={"error": "权限不足"}
            )
        
        # 获取配置
        config_manager = ConfigManager()
        config = config_manager.get_all_configs()
        
        return {
            "status": "success",
            "data": config
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": "获取配置失败", "message": str(e)}
        )

async def update_config(self, request: Request):
    """更新系统配置"""
    try:
        # 检查权限
        user = request.scope.get("user", {})
        if not self.has_admin_permission(user):
            return JSONResponse(
                status_code=403,
                content={"error": "权限不足"}
            )
        
        # 解析请求数据
        config_data = await request.json()
        
        # 验证配置
        validated_config = self.validate_config(config_data)
        
        # 更新配置
        config_manager = ConfigManager()
        config_manager.update_config(validated_config)
        
        return {
            "status": "success",
            "message": "配置更新成功"
        }
    except ValidationError as e:
        return JSONResponse(
            status_code=400,
            content={"error": "配置验证失败", "details": e.errors()}
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": "更新配置失败", "message": str(e)}
        )
```

## 常见问题与解决方案

### 1. 并发处理问题

#### 问题描述
高并发场景下可能出现连接数限制、内存溢出等问题。

#### 解决方案
- **连接池管理**: 使用连接池管理数据库和Redis连接
- **异步处理**: 全面使用异步处理提高并发能力
- **资源限制**: 设置合理的资源限制和超时时间
- **负载均衡**: 使用负载均衡分散请求压力

### 2. 流式响应中断

#### 问题描述
网络不稳定可能导致流式响应中断。

#### 解决方案
- **心跳机制**: 定期发送心跳包保持连接
- **自动重连**: 客户端自动重连机制
- **断点续传**: 支持断点续传功能
- **错误恢复**: 完善的错误恢复机制

### 3. 认证安全问题

#### 问题描述
API接口可能面临未授权访问、token泄露等安全问题。

#### 解决方案
- **JWT认证**: 使用JWT进行身份认证
- **Token轮换**: 定期轮换认证token
- **权限控制**: 细粒度的权限控制
- **审计日志**: 完整的访问审计日志

## 系统设计优势

### 1. 高性能
- **异步架构**: 基于异步架构提高并发性能
- **流式处理**: 支持流式处理减少延迟
- **缓存优化**: 智能缓存减少重复计算
- **资源优化**: 优化资源使用效率

### 2. 高可用性
- **健康检查**: 完善的健康检查机制
- **故障恢复**: 自动故障恢复能力
- **监控告警**: 实时监控和告警
- **负载均衡**: 支持负载均衡

### 3. 易扩展性
- **模块化设计**: 模块化设计便于扩展
- **插件机制**: 支持插件扩展功能
- **标准化接口**: 标准化的API接口
- **版本管理**: 支持API版本管理

## 可扩展性设计

### 1. 接口扩展
```python
# 新增API接口
class NewAPIRouter:
    def __init__(self):
        self.routes = []
    
    def add_route(self, path: str, handler, methods: List[str] = None):
        """添加新路由"""
        self.routes.append({
            "path": path,
            "handler": handler,
            "methods": methods or ["GET"]
        })
    
    def register_to_app(self, app):
        """注册到FastAPI应用"""
        for route in self.routes:
            for method in route["methods"]:
                if method == "GET":
                    app.get(route["path"])(route["handler"])
                elif method == "POST":
                    app.post(route["path"])(route["handler"])
```

### 2. 中间件扩展
- **自定义中间件**: 支持自定义中间件
- **中间件链**: 支持中间件链式处理
- **条件中间件**: 支持条件中间件
- **动态中间件**: 支持动态加载中间件

### 3. 认证方式扩展
- **OAuth2**: 支持OAuth2认证
- **API Key**: 支持API Key认证
- **LDAP**: 支持LDAP认证
- **自定义认证**: 支持自定义认证方式

## 高可用性保障

### 1. 服务监控
- **健康检查**: 定期健康检查
- **性能监控**: 实时性能监控
- **错误监控**: 错误监控和告警
- **资源监控**: 资源使用监控

### 2. 故障恢复
- **自动重启**: 服务自动重启
- **故障转移**: 自动故障转移
- **数据备份**: 定期数据备份
- **恢复测试**: 定期恢复测试

### 3. 安全防护
- **DDoS防护**: DDoS攻击防护
- **SQL注入防护**: SQL注入防护
- **XSS防护**: XSS攻击防护
- **CSRF防护**: CSRF攻击防护

## 通用性设计

### 1. 标准化接口
- **RESTful设计**: 遵循RESTful设计原则
- **统一响应格式**: 统一的响应数据格式
- **错误处理**: 统一的错误处理机制
- **版本控制**: API版本控制

### 2. 跨平台支持
- **多语言客户端**: 支持多种编程语言
- **移动端支持**: 支持移动端应用
- **Web端支持**: 支持Web端应用
- **桌面端支持**: 支持桌面端应用

### 3. 集成能力
- **第三方集成**: 支持第三方系统集成
- **Webhook**: 支持Webhook回调
- **消息队列**: 支持消息队列集成
- **事件总线**: 支持事件总线集成

## 总结

API服务与接口管理系统是BluePlan Research的核心服务层，通过FastAPI框架提供高性能、高可用的API服务。系统具备完善的中间件管理、认证授权、监控告警等功能，能够满足企业级应用的各种需求。同时，系统设计注重可扩展性和通用性，为未来的功能扩展和集成提供了良好的基础。
