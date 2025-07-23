​
Implementation Guidelines 实施指南

Clients SHOULD: 客户端**应该**：

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



