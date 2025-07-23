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



