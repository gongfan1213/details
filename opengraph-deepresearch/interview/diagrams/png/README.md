### Mermaid 转 PNG 指南

- 推荐使用 vscode + Mermaid 或 `mmdc`（mermaid-cli）导出：
```bash
npm i -g @mermaid-js/mermaid-cli
mmdc -i ../architecture_flow.md -o architecture_flow.png
```
- 输出路径：`interview/diagrams/png/`
- 文档中的双格式引用：
  - Markdown 内嵌 mermaid 作为主格式
  - PNG 作为备用（如渲染失败时手动打开）
