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
