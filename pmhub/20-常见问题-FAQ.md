# 常见问题 FAQ

## 启动相关
- 服务启动失败：检查 Nacos 中对应 `*-dev.yml` 的数据库连接与Redis地址是否正确；确认数据库表已导入
- 端口占用：修改 `application.yml` 端口或释放占用进程
- Nacos 无法访问：确认已 standalone 启动并开放 8848 端口

## 登录与权限
- 登录401：Token 过期或网关未透传 Authorization；确认时间同步
- 权限不生效：菜单 perms 与后端 `@RequiresPermissions` 对齐

## 数据与SQL
- 慢查询：补充索引或裁剪字段
- 分页异常：确认 pageNum/pageSize 参数与拦截器是否生效

## 工作流
- 无流程可发起：未部署模型或权限不足
- 任务丢失：查询自己的“待签”列表（claimList）与“待办”（todoList）

## 文件上传
- 预览乱码：`Content-Type` 与文件编码不匹配
- 403：未授权的下载，按项目/任务校验权限

## 前端
- 白屏：查看控制台与网络请求；确认 `.env` 接口地址
- 跨域：本地代理或网关 CORS 设置

## 部署
- Docker 容器间无法通信：检查网络与服务名；使用相同 docker network
- 配置变更不生效：确认 Nacos 配置ID、group、dataId

## 其他
- 缓存不一致：手动清理相关 cache key 或重启
- MQ 堆积：扩容消费者/监控 DLQ/排查消费失败原因
