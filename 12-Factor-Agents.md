# 12-Factor Agents 开发经验完整总结

## 概述

12-Factor Agents 是一套构建可靠LLM应用的原则，借鉴了经典的12-Factor Apps方法论。这些原则旨在帮助开发者构建高质量、可扩展、易维护的AI代理系统。

### 核心理念

- **AI代理本质上是软件**：它们应该遵循良好的软件工程实践
- **模块化设计**：将复杂的AI功能分解为小型、专注的组件
- **确定性优先**：在可能的情况下使用确定性代码，只在需要的地方引入AI
- **上下文工程**：优化与LLM的交互方式，最大化模型性能

## 12个核心因子详解

### Factor 1: 自然语言到工具调用 (Natural Language to Tool Calls)

**核心概念**：将自然语言转换为结构化的工具调用

**最佳实践**：
- 使用LLM将用户意图转换为JSON格式的工具调用
- 保持工具调用的原子性和可预测性
- 在确定性代码中处理工具执行

**代码示例**：
```typescript
// 用户输入
const userInput = "创建一个750美元的付款链接给Terri，用于赞助2月份的AI聚会"

// LLM转换为结构化输出
const toolCall = {
  function: {
    name: "create_payment_link",
    parameters: {
      amount: 750,
      customer: "cust_128934ddasf9",
      product: "prod_8675309",
      memo: "2月份AI聚会的赞助付款链接"
    }
  }
}

// 确定性代码执行
if (toolCall.function.name === 'create_payment_link') {
  const result = await stripe.paymentLinks.create(toolCall.function.parameters)
  return result
}
```

**实际应用**：
- 客服机器人处理用户请求
- 代码部署代理理解部署指令
- 数据分析代理处理查询请求

### Factor 2: 拥有你的提示词 (Own Your Prompts)

**核心概念**：不要将提示词工程外包给框架，保持对提示词的完全控制

**最佳实践**：
- 将提示词作为一等公民的代码
- 使用专门的提示词工程工具（如BAML）
- 为提示词编写测试和评估
- 快速迭代和优化提示词

**代码示例**：
```typescript
function DetermineNextStep(thread: string): DoneForNow | ListGitTags | DeployBackend | DeployFrontend | RequestMoreInformation {
  const prompt = `
    {{ _.role("system") }}
    
    你是一个帮助管理前端和后端系统部署的助手。
    你致力于确保安全成功的部署，遵循最佳实践和正确的部署程序。
    
    在部署任何系统之前，你应该检查：
    - 部署环境（测试 vs 生产）
    - 正确的标签/版本
    - 当前系统状态
    
    你可以使用deploy_backend、deploy_frontend和check_deployment_status等工具来管理部署。
    对于敏感部署，使用request_approval获取人工验证。
    
    {{ _.role("user") }}
    {{ thread }}
    
    下一步应该做什么？
  `
  
  return await llm.generate(prompt)
}
```

**实际应用**：
- 自定义部署代理的决策逻辑
- 客服机器人的回复风格
- 代码审查代理的评估标准

### Factor 3: 拥有你的上下文窗口 (Own Your Context Window)

**核心概念**：优化传递给LLM的上下文格式，最大化信息密度和模型理解

**最佳实践**：
- 设计自定义的上下文格式，而非标准消息格式
- 使用XML或YAML等结构化格式
- 控制传递给LLM的信息内容
- 优化token效率和注意力机制

**代码示例**：
```typescript
class Thread {
  events: Event[]
}

class Event {
  type: "list_git_tags" | "deploy_backend" | "deploy_frontend" | "error"
  data: any
}

function eventToPrompt(event: Event): string {
  const data = typeof event.data === 'string' 
    ? event.data 
    : stringifyToYaml(event.data)
  
  return `<${event.type}>\n${data}\n</${event.type}>`
}

function threadToPrompt(thread: Thread): string {
  return thread.events.map(eventToPrompt).join('\n\n')
}
```

**上下文窗口示例**：
```xml
<slack_message>
    From: @alex
    Channel: #deployments
    Text: 能否部署最新的后端到生产环境？
</slack_message>

<list_git_tags>
    intent: "list_git_tags"
</list_git_tags>

<list_git_tags_result>
    tags:
      - name: "v1.2.3"
        commit: "abc123"
        date: "2024-03-15T10:00:00Z"
      - name: "v1.2.2"
        commit: "def456"
        date: "2024-03-14T15:30:00Z"
</list_git_tags_result>
```

**实际应用**：
- 部署代理的上下文管理
- 客服对话历史的结构化存储
- 代码审查的上下文传递

### Factor 4: 工具只是结构化输出 (Tools are Structured Outputs)

**核心概念**：工具调用本质上是LLM的结构化输出，触发确定性代码执行

**最佳实践**：
- 将工具定义为简单的JSON结构
- 在确定性代码中处理工具执行逻辑
- 保持LLM决策与代码执行的分离

**代码示例**：
```typescript
interface CreateIssue {
  intent: "create_issue"
  issue: {
    title: string
    description: string
    team_id: string
    assignee_id: string
  }
}

interface SearchIssues {
  intent: "search_issues"
  query: string
  what_youre_looking_for: string
}

// 处理工具调用
switch (nextStep.intent) {
  case 'create_issue':
    await linearClient.issues.create(nextStep.issue)
    break
  case 'search_issues':
    const issues = await linearClient.issues.list({ query: nextStep.query })
    break
  default:
    // 处理未知工具调用
}
```

**实际应用**：
- API调用代理
- 数据库操作代理
- 文件系统操作代理

### Factor 5: 统一执行状态和业务状态 (Unify Execution State and Business State)

**核心概念**：简化状态管理，尽可能统一执行状态和业务状态

**最佳实践**：
- 避免复杂的状态分离抽象
- 从上下文窗口推断执行状态
- 最小化无法放入上下文的状态

**代码示例**：
```typescript
// 统一的状态结构
interface Thread {
  events: Event[]
  // 执行状态可以从events推断
}

// 序列化和反序列化
async function saveThread(thread: Thread): Promise<string> {
  const threadId = generateId()
  await db.save(threadId, JSON.stringify(thread))
  return threadId
}

async function loadThread(threadId: string): Promise<Thread> {
  const data = await db.load(threadId)
  return JSON.parse(data)
}

// 从上下文推断状态
function getCurrentStep(thread: Thread): string {
  const lastEvent = thread.events[thread.events.length - 1]
  return lastEvent?.type || 'initial'
}
```

**实际应用**：
- 部署流程的状态管理
- 客服对话的状态跟踪
- 工作流执行的状态持久化

### Factor 6: 启动/暂停/恢复的简单API (Launch/Pause/Resume with Simple APIs)

**核心概念**：提供简单的API来启动、查询、恢复和停止代理

**最佳实践**：
- 设计RESTful API接口
- 支持长时间运行的操作
- 通过webhook实现恢复功能

**代码示例**：
```typescript
// API端点
app.post('/agents/start', async (req, res) => {
  const { initialMessage } = req.body
  const threadId = await startAgent(initialMessage)
  res.json({ threadId, status: 'started' })
})

app.get('/agents/:threadId/status', async (req, res) => {
  const { threadId } = req.params
  const status = await getAgentStatus(threadId)
  res.json(status)
})

app.post('/agents/:threadId/resume', async (req, res) => {
  const { threadId } = req.params
  const { response } = req.body
  await resumeAgent(threadId, response)
  res.json({ status: 'resumed' })
})

// 暂停和恢复逻辑
async function pauseAgent(threadId: string, reason: string) {
  const thread = await loadThread(threadId)
  thread.events.push({
    type: 'paused',
    data: { reason, timestamp: new Date().toISOString() }
  })
  await saveThread(threadId, thread)
}
```

**实际应用**：
- 部署代理的暂停和恢复
- 客服对话的异步处理
- 长时间运行任务的监控

### Factor 7: 通过工具调用联系人类 (Contact Humans with Tools)

**核心概念**：将人类交互作为工具调用处理，支持结构化的交互

**最佳实践**：
- 定义人类交互的工具结构
- 支持多种交互格式（自由文本、是/否、多选）
- 实现异步的人类反馈处理

**代码示例**：
```typescript
interface RequestHumanInput {
  intent: "request_human_input"
  question: string
  context: string
  options: {
    urgency: "low" | "medium" | "high"
    format: "free_text" | "yes_no" | "multiple_choice"
    choices?: string[]
  }
}

// 处理人类交互请求
if (nextStep.intent === 'request_human_input') {
  thread.events.push({
    type: 'human_input_requested',
    data: nextStep
  })
  
  const threadId = await saveThread(thread)
  await notifyHuman(nextStep, threadId)
  return // 中断循环，等待响应
}

// 处理人类响应
app.post('/webhook/human-response', async (req, res) => {
  const { threadId, response } = req.body
  const thread = await loadThread(threadId)
  
  thread.events.push({
    type: 'human_response',
    data: response
  })
  
  await saveThread(threadId, thread)
  await continueAgent(threadId)
  
  res.json({ status: 'ok' })
})
```

**实际应用**：
- 部署审批流程
- 客服升级处理
- 敏感操作的人工确认

### Factor 8: 拥有你的控制流 (Own Your Control Flow)

**核心概念**：构建自定义的控制结构，支持复杂的交互模式

**最佳实践**：
- 实现自定义的循环和条件逻辑
- 支持工具选择和执行之间的暂停
- 集成日志、追踪和指标

**代码示例**：
```typescript
async function handleNextStep(thread: Thread) {
  while (true) {
    const nextStep = await determineNextStep(threadToPrompt(thread))
    
    switch (nextStep.intent) {
      case 'request_clarification':
        thread.events.push({
          type: 'request_clarification',
          data: nextStep
        })
        await sendMessageToHuman(nextStep)
        await saveThread(thread)
        return // 异步步骤，稍后通过webhook恢复
        
      case 'fetch_open_issues':
        thread.events.push({
          type: 'fetch_open_issues',
          data: nextStep
        })
        
        const issues = await linearClient.issues()
        thread.events.push({
          type: 'fetch_open_issues_result',
          data: issues
        })
        continue // 同步步骤，继续循环
        
      case 'create_issue':
        thread.events.push({
          type: 'create_issue',
          data: nextStep
        })
        
        await requestHumanApproval(nextStep)
        await saveThread(thread)
        return // 异步步骤，等待审批
    }
  }
}
```

**实际应用**：
- 复杂工作流的控制
- 条件分支的处理
- 错误恢复机制

### Factor 9: 将错误压缩到上下文窗口 (Compact Errors into Context Window)

**核心概念**：将错误信息结构化地包含在上下文中，支持自我修复

**最佳实践**：
- 格式化错误信息以便LLM理解
- 实现错误重试机制
- 设置错误阈值和升级策略

**代码示例**：
```typescript
let consecutiveErrors = 0

while (true) {
  try {
    const nextStep = await determineNextStep(threadToPrompt(thread))
    thread.events.push({
      type: nextStep.intent,
      data: nextStep
    })
    
    const result = await handleNextStep(thread, nextStep)
    thread.events.push({
      type: nextStep.intent + '_result',
      data: result
    })
    
    consecutiveErrors = 0 // 成功，重置错误计数
  } catch (error) {
    consecutiveErrors++
    
    if (consecutiveErrors < 3) {
      // 添加错误到上下文并重试
      thread.events.push({
        type: 'error',
        data: formatError(error)
      })
    } else {
      // 达到错误阈值，升级到人工处理
      await escalateToHuman(thread, error)
      break
    }
  }
}

function formatError(error: Error): string {
  return {
    message: error.message,
    type: error.constructor.name,
    timestamp: new Date().toISOString(),
    suggestion: getErrorSuggestion(error)
  }
}
```

**实际应用**：
- API调用失败的重试
- 网络错误的恢复
- 数据验证错误的处理

### Factor 10: 小型专注的代理 (Small, Focused Agents)

**核心概念**：构建小型、专注的代理，而非大型的通用代理

**最佳实践**：
- 限制代理的步骤数量（3-20步）
- 明确定义代理的职责范围
- 保持上下文窗口的可管理性

**代码示例**：
```typescript
// 部署代理 - 专注单一职责
class DeploymentAgent {
  async handleDeployment(request: DeploymentRequest): Promise<DeploymentResult> {
    const thread = { events: [request] }
    
    // 限制最大步骤数
    let stepCount = 0
    const MAX_STEPS = 10
    
    while (stepCount < MAX_STEPS) {
      const nextStep = await this.determineNextStep(thread)
      
      if (nextStep.intent === 'deployment_complete') {
        return nextStep.result
      }
      
      await this.executeStep(thread, nextStep)
      stepCount++
    }
    
    throw new Error('部署步骤过多，可能陷入循环')
  }
}

// 代码审查代理 - 专注代码质量
class CodeReviewAgent {
  async reviewCode(pullRequest: PullRequest): Promise<ReviewResult> {
    // 专注的代码审查逻辑
    const review = await this.analyzeCode(pullRequest)
    return this.generateReview(review)
  }
}
```

**实际应用**：
- 专门的部署代理
- 专注的客服代理
- 单一功能的代码生成代理

### Factor 11: 从任何地方触发，在用户所在的地方相遇 (Trigger from Anywhere, Meet Users Where They Are)

**核心概念**：支持多种触发方式和响应渠道

**最佳实践**：
- 支持Slack、邮件、SMS等多种渠道
- 实现外循环代理（由事件触发）
- 支持高风险的代理操作

**代码示例**：
```typescript
// 多渠道触发
app.post('/webhook/slack', async (req, res) => {
  const { text, user, channel } = req.body
  const threadId = await startAgent({
    type: 'slack_message',
    data: { text, user, channel }
  })
  res.json({ threadId })
})

app.post('/webhook/email', async (req, res) => {
  const { subject, body, from } = req.body
  const threadId = await startAgent({
    type: 'email',
    data: { subject, body, from }
  })
  res.json({ threadId })
})

// 定时任务触发
cron.schedule('0 9 * * *', async () => {
  await startAgent({
    type: 'daily_report',
    data: { date: new Date().toISOString() }
  })
})

// 多渠道响应
async function respondToUser(threadId: string, response: string) {
  const thread = await loadThread(threadId)
  const triggerEvent = thread.events[0]
  
  switch (triggerEvent.type) {
    case 'slack_message':
      await slackClient.postMessage(triggerEvent.data.channel, response)
      break
    case 'email':
      await emailClient.sendEmail(triggerEvent.data.from, response)
      break
  }
}
```

**实际应用**：
- 多渠道客服系统
- 自动化监控和报警
- 定时报告生成

### Factor 12: 让你的代理成为无状态归约器 (Make Your Agent a Stateless Reducer)

**核心概念**：将代理设计为无状态的函数，便于测试和扩展

**最佳实践**：
- 实现纯函数式的代理逻辑
- 支持状态的序列化和反序列化
- 便于并行处理和扩展

**代码示例**：
```typescript
// 无状态的代理函数
function agentReducer(state: Thread, action: AgentAction): Thread {
  switch (action.type) {
    case 'ADD_EVENT':
      return {
        ...state,
        events: [...state.events, action.payload]
      }
    
    case 'UPDATE_EVENT':
      return {
        ...state,
        events: state.events.map(event => 
          event.id === action.payload.id 
            ? { ...event, ...action.payload }
            : event
        )
      }
    
    case 'RESET':
      return {
        events: [action.payload]
      }
    
    default:
      return state
  }
}

// 使用归约器
async function runAgent(initialState: Thread): Promise<Thread> {
  let state = initialState
  
  while (!isComplete(state)) {
    const nextAction = await determineNextAction(state)
    state = agentReducer(state, nextAction)
    
    if (nextAction.type === 'EXECUTE_TOOL') {
      const result = await executeTool(nextAction.payload)
      state = agentReducer(state, {
        type: 'ADD_EVENT',
        payload: { type: 'tool_result', data: result }
      })
    }
  }
  
  return state
}
```

**实际应用**：
- 可测试的代理逻辑
- 分布式代理系统
- 状态回滚和恢复

## 附录：Factor 13 - 预取上下文 (Pre-fetch Context)

**核心概念**：如果知道代理可能需要某些信息，提前获取并包含在上下文中

**最佳实践**：
- 分析代理的常见执行路径
- 预取可能需要的API数据
- 减少token往返次数

**代码示例**：
```typescript
// 预取Git标签
async function startDeploymentAgent(deploymentRequest: DeploymentRequest) {
  // 预取可能需要的Git标签
  const gitTags = await fetchGitTags()
  
  const thread = {
    events: [
      deploymentRequest,
      {
        type: 'git_tags_available',
        data: gitTags
      }
    ]
  }
  
  return await runAgent(thread)
}

// 预取用户信息
async function startSupportAgent(supportRequest: SupportRequest) {
  // 预取用户历史记录
  const userHistory = await fetchUserHistory(supportRequest.userId)
  
  const thread = {
    events: [
      supportRequest,
      {
        type: 'user_history_available',
        data: userHistory
      }
    ]
  }
  
  return await runAgent(thread)
}
```

## 实际应用案例

### 案例1：部署代理 (DeployBot)

**功能**：自动化代码部署流程
**应用因子**：1, 2, 3, 5, 6, 7, 8, 10

```typescript
// 部署代理的核心逻辑
class DeployBot {
  async handleDeployment(request: DeploymentRequest): Promise<void> {
    const thread = { events: [request] }
    
    while (true) {
      const nextStep = await this.determineNextStep(thread)
      
      switch (nextStep.intent) {
        case 'deploy_backend':
          await this.requestApproval(nextStep, thread)
          return // 等待审批
          
        case 'deploy_frontend':
          await this.requestApproval(nextStep, thread)
          return // 等待审批
          
        case 'deployment_complete':
          await this.notifySuccess(thread)
          return
      }
    }
  }
}
```

### 案例2：客服代理 (Support Agent)

**功能**：处理客户支持请求
**应用因子**：1, 2, 3, 4, 7, 9, 10, 11

```typescript
// 客服代理的核心逻辑
class SupportAgent {
  async handleSupportRequest(request: SupportRequest): Promise<void> {
    const thread = { events: [request] }
    
    while (true) {
      const nextStep = await this.determineNextStep(thread)
      
      switch (nextStep.intent) {
        case 'search_knowledge_base':
          const articles = await this.searchKB(nextStep.query)
          thread.events.push({
            type: 'search_result',
            data: articles
          })
          continue
          
        case 'escalate_to_human':
          await this.escalateToHuman(thread, nextStep)
          return
          
        case 'provide_answer':
          await this.sendResponse(thread, nextStep.answer)
          return
      }
    }
  }
}
```

## 最佳实践总结

### 1. 架构设计原则
- **模块化**：将复杂系统分解为小型、专注的组件
- **确定性优先**：在可能的情况下使用确定性代码
- **状态简化**：统一执行状态和业务状态
- **控制流拥有**：自定义控制逻辑而非依赖框架

### 2. 开发流程
- **迭代开发**：从简单功能开始，逐步增加复杂性
- **测试驱动**：为每个代理编写测试用例
- **监控和日志**：实现全面的监控和日志系统
- **错误处理**：设计健壮的错误处理和恢复机制

### 3. 性能优化
- **上下文优化**：最大化信息密度和token效率
- **预取策略**：提前获取可能需要的数据
- **缓存机制**：缓存频繁使用的信息
- **并行处理**：支持并发执行和扩展

### 4. 用户体验
- **多渠道支持**：支持用户偏好的交互方式
- **透明性**：提供清晰的状态和进度信息
- **可控性**：允许用户干预和控制代理行为
- **可靠性**：确保高可用性和错误恢复

## 技术栈建议

### 核心框架
- **TypeScript/JavaScript**：类型安全和开发效率
- **Node.js**：异步处理和生态系统
- **BAML**：提示词工程和类型安全
- **OpenAI/Anthropic**：LLM API

### 基础设施
- **PostgreSQL/Redis**：状态存储和缓存
- **Docker/Kubernetes**：容器化和编排
- **Prometheus/Grafana**：监控和可视化
- **Slack/Email APIs**：多渠道集成

### 开发工具
- **Jest**：测试框架
- **ESLint/Prettier**：代码质量
- **GitHub Actions**：CI/CD
- **VSCode**：开发环境

## 结论

12-Factor Agents 提供了一套系统性的方法来构建高质量的AI代理系统。通过遵循这些原则，开发者可以：

1. **提高可靠性**：通过模块化设计和错误处理
2. **增强可维护性**：通过清晰的架构和测试
3. **改善用户体验**：通过多渠道支持和透明性
4. **支持扩展性**：通过无状态设计和并行处理

这些原则不仅适用于AI代理，也可以应用于任何需要LLM集成的软件系统。关键是理解每个原则的核心价值，并根据具体需求灵活应用。

记住，AI工程的核心是**上下文工程** - 如何最有效地与LLM交互，如何构建最合适的提示词和上下文格式，以及如何设计最有效的控制流程。通过掌握这些技能，你可以构建出真正有价值的AI应用。
