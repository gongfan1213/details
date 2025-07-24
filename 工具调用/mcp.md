Best practices 最佳实践
​

Transport selection 运输方式选择

Local communication 本地通信

Use stdio transport for local processes

对本地进程使用标准输入输出传输


Efficient for same-machine communication

对于同一机器内的通信效率高

Simple process management 简单的进程管理

Remote communication 远程通信

Use Streamable HTTP for scenarios requiring HTTP compatibility

对于需要HTTP兼容性的场景，请使用可流化HTTP

Consider security implications including authentication and authorization

考虑安全影响，包括身份验证和授权

​

Message handling 消息处理

Request processing 请求处理

Validate inputs thoroughly 全面验证输入内容

Use type-safe schemas 使用类型安全的模式

Handle errors gracefully 优雅地处理错误

Implement timeouts 实现超时设置

Progress reporting 进度报告

Use progress tokens for long operations

对长时间运行的操作使用进度令牌

Report progress incrementally 逐步报告进度

Include total progress when known 已知总进度时，将其包含在内

Error management 错误管理

Use appropriate error codes 使用适当的错误代码

Include helpful error messages 包含有用的错误信息

Clean up resources on errors 发生错误时清理资源

​

Security considerations 安全注意事项

Transport security 运输安全

Use TLS for remote connections 对远程连接使用传输层安全协议（TLS）

Validate connection origins 验证连接来源

Implement authentication when needed 在需要时实施身份验证

Message validation 消息验证

Validate all incoming messages 验证所有传入消息

Sanitize inputs 清理输入

Check message size limits 检查消息大小限制

Verify JSON-RPC format 验证JSON-RPC格式

Resource protection 资源保护

Implement access controls 实施访问控制

Validate resource paths 验证资源路径

Monitor resource usage 监控资源使用情况

Rate limit requests 限制请求速率

Error handling 错误处理

Don’t leak sensitive information 不要泄露敏感信息

Log security-relevant errors 记录与安全相关的错误

Implement proper cleanup 执行适当的清理操作

Handle DoS scenarios 处理拒绝服务（DoS）场景

​Best practices 最佳实践

When implementing resource support: 在实现资源支持时：

Use clear, descriptive resource names and URIs

使用清晰、描述性的资源名称和统一资源标识符

Include helpful descriptions to guide LLM understanding

添加有助于引导大语言模型理解的描述信息

Set appropriate MIME types when known

已知时设置合适的MIME类型

Implement resource templates for dynamic content

实现动态内容的资源模板

Use subscriptions for frequently changing resources

对频繁变化的资源使用订阅功能

Handle errors gracefully with clear error messages

优雅地处理错误，并给出清晰的错误信息

Consider pagination for large resource lists

对于大型资源列表，考虑使用分页功能

Cache resource contents when appropriate

在适当的时候缓存资源内容

Validate URIs before processing 在处理之前验证统一资源标识符（URI）

Document your custom URI schemes 记录您的自定义 URI 方案

​

Security considerations 安全注意事项

When exposing resources: 在公开资源时：

Validate all resource URIs 验证所有资源统一资源标识符

Implement appropriate access controls

实施适当的访问控制

Sanitize file paths to prevent directory traversal

清理文件路径以防止目录遍历

Be cautious with binary data handling

处理二进制数据时要谨慎

Consider rate limiting for resource reads

考虑对资源读取进行速率限制

Audit resource access 审计资源访问

Encrypt sensitive data in transit 传输中加密敏感数据

Validate MIME types 验证MIME类型

Implement timeouts for long-running reads

为长时间运行的读取操作设置超时时间

Handle resource cleanup appropriately

妥善处理资源清理







Server not showing up in Claude 服务器未在Claude中显示



Check your claude_desktop_config.json file syntax

检查你的claude_desktop_config.json文件语法

Make sure the path to your project is absolute and not relative

确保项目路径是绝对路径，而非相对路径。

Restart Claude for Desktop completely

完全重启桌面版Claude

​
Implementation Guidelines 实施指南

Clients SHOULD: 客户端****应该**：

Prompt users for consent before exposing roots to servers

在向服务器暴露根目录之前，提示用户进行确认

Provide clear user interfaces for root management

为根管理提供清晰的用户界面

Validate root accessibility before exposing

在公开之前验证根可访问性

Monitor for root changes 监控根目录的更改

Servers SHOULD: 服务器 应该：

Check for roots capability before usage

使用前检查根权限

Handle root list changes gracefully 妥善处理根列表变更

Respect root boundaries in operations

操作中尊重根权限边界

Cache root information appropriately 适当地缓存根目录信息

When implementing MCP servers, be careful about how you handle logging:

在实现MCP服务器时，要注意处理日志记录的方式：

For STDIO-based servers: Never write to standard output (stdout). This includes:

**对于基于标准输入输出（STDIO）的服务器**：切勿写入标准输出（stdout）。这包括：

print() statements in Python Python中的print()语句

console.log() in JavaScript JavaScript中的console.log()

fmt.Println() in Go Go语言中的fmt.Println()

Similar stdout functions in other languages

其他语言中类似的标准输出函数

Writing to stdout will corrupt the JSON-RPC messages and break your server.

写入标准输出会破坏JSON-RPC消息并导致服务器故障。

For HTTP-based servers: Standard output logging is fine since it doesn’t interfere with HTTP responses.

对于基于HTTP的服务器：标准输出日志记录就可以，因为它不会干扰HTTP响应。


Best practices 最佳实践
Error Handling 错误处理
Always wrap tool calls in try-catch blocks
始终将工具调用包装在try-catch块中
Provide meaningful error messages 提供有意义的错误信息
Gracefully handle connection issues 优雅地处理连接问题
Resource Management 资源管理
Use AsyncExitStack for proper cleanup
使用 AsyncExitStack 进行妥善清理
Close connections when done 完成后关闭连接
Handle server disconnections 处理服务器断开连接
Security 安全
Store API keys securely in .env 将API密钥安全存储在.env中
Validate server responses 验证服务器响应
Be cautious with tool permissions 谨慎授予工具权限
​
Troubleshooting 故障排除
​
Server Path Issues 服务器路径问题

Double-check the path to your server script is correct

仔细检查服务器脚本的路径是否正确

Use the absolute path if the relative path isn’t working

如果相对路径不起作用，请使用绝对路径。

For Windows users, make sure to use forward slashes (/) or escaped backslashes (\) in the path

对于Windows用户，请确保在路径中使用正斜杠（/）或转义后的反斜杠（\）

Verify the server file has the correct extension (.py for Python or .js for Node.js)

验证服务器文件具有正确的扩展名（Python为.py，Node.js为.js）
