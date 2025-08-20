### 面试话术｜部署与运维（Docker / K8s / 监控）

- 一句话简介：从本地一键到生产多副本部署，配套健康检查、日志与指标，保障稳定可观测。

#### 职责（20s）
- 设计一键脚本与容器化镜像；K8s 编排、健康探针与资源配额；Prometheus 指标接入

#### 实现要点（1min）
- 一键脚本：`check_dep_port.sh`、`Genie_start.sh`、`start_genie.sh`
- Docker：多阶段构建（后端/工具/前端），统一启动
- K8s：Deployment + Service + Ingress；`liveness/readiness` 探针
- 监控：后端 `actuator/prometheus`，工具/客户端暴露 `/metrics`
- 日志：生产 JSON + 轮转；按 `requestId` 关联

#### 问题与解决
- 问题1：端口/依赖检查不足
  - 方案：启动前 `check_dep_port.sh` 检查 JDK/Python/端口占用
- 问题2：OOM 与长 GC 暂停
  - 方案：JVM G1 参数与资源限额；工具服务并发上限
- 问题3：配置错配与联调困难
  - 方案：`.env` 与 `application.yml` 分环境；健康检查脚本与连通性自检

#### 指标
- 发布失败率 < 1%
- 回滚平均 < 2min

#### Q&A
- Q：如何快速定位线上问题？
  - A：按 `requestId` 检索后端日志与工具产物；SSE 错误事件回溯。

#### 演进
- GitOps 全流程；灰度与自动扩缩容
