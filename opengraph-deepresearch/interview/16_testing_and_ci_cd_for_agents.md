### 16 Agents 测试与 CI/CD 面试题（Testing & CI/CD for Agents）

- 关注点：单元/集成/端到端测试、数据构造、回归评测、CI 门禁、可重放
- 关键参考：`pytest.ini`, `press_test/**`, `run_and_analyze.sh`, `visualize_test_results.py`

#### 基础题
- 单元测试：如何 mock LLM 与工具（成功/超时/4xx/5xx）？如何断言 Agent 的路由与副作用不发生？
- 集成测试：如何对 `graph_routes_v2.py` 的 SSE 接口做端到端校验（阶段变更、最终结果、恢复流程）？
- 数据与隔离：如何构造稳定的测试数据并清理检查点与缓存？

#### 进阶题
- 评测集：为关键 Prompt/Agent 维护小而精的评测集，如何在 CI 中跑并判定退化？
- 压测：参考 `press_test/*`，如何在阶段性发布前进行流量压测与成本评估？
- 可重放：如何记录输入/决策/工具调用，便于事后重放与问题定位？

#### 实操题
- 写一个 Pytest 用例：模拟 `human_confirmation` 的 `interrupt/resume`，断言恢复后仅重放无副作用节点。
- 写一个脚本：批量回放近 24h 失败任务，生成“失败原因 Top-N + 建议修复”报告。

#### 场景题
- CI 门禁：哪些指标达标才能放行（单测覆盖、评测分、压测结果、基础监控绿灯）？
- 变更追责：如何用 trace ID 将线上问题回溯到具体 PR/Prompt 变更？

#### 追问
- 隔离性：如何避免测试对生产数据/配额造成影响？
- 稳定性：对易抖动用例如何做特判与降噪统计？

#### 作业
- 给出一个“最小可运行”的 CI 配置草案：安装、环境准备、运行评测/单测/集成/压测、产出报告、失败门禁。

### 参考答案（示例）
- 单测：mock LLM/工具（成功/超时/4xx/429/5xx），断言路由与副作用不发生；
- 集成：对 `/graph_v2/chat/stream` 做 E2E 校验（阶段事件/最终结果/人审恢复）；
- 评测集：维护 Prompt/Agent 小样本集，CI 中跑评分阈值门禁，出现退化自动阻断；
- 压测：按场景对关键接口做 QPS/时延/错误率测试，产出对比报告；
- 可重放：记录输入/决策/工具调用序列与 trace_id，提供回放脚本用于故障定位；
- 门禁：覆盖率≥阈值、评测分≥阈值、金指标绿灯、压测通过方可放行。

#### CI 配置片段（示意）
```yaml
name: agents-ci
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: {python-version: '3.11'}
      - run: pip install -r requirements.txt
      - run: pytest -q --maxfail=1 --disable-warnings
      - run: python press_test/run_and_analyze.sh
      - run: python tools/run_prompt_eval.py --gate 0.9
```

#### E2E 校验要点
- SSE 事件序列：start → stage_change/node_execution → final_result/end；
- 中断恢复：human_review_required → resume → 继续到 completed；
- 断言：最终输出结构、阶段顺序、错误码与耗时阈值。

### 常见错误与改进建议
- 错误：mock 粗糙，导致测试不稳定或与生产脱节。
  - 改进：覆盖成功/超时/4xx/429/5xx 等典型分支；对 LLM/工具使用可控桩；
- 错误：无评测集门禁，Prompt 变更常引入退化。
  - 改进：小样本评测 + 阈值门禁，失败即阻断并回滚；
- 错误：压测与成本评估缺失。
  - 改进：阶段性压测，记录 QPS/时延/成本曲线，超阈值阻断发布。

#### 图稿
- 参见：`interview/diagrams/testing_ci_cd.md`。
