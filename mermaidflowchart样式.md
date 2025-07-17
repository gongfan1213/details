```
flowchart TD
    %% 样式节点示例
    A((开始节点)) --> B[处理步骤节点]
    B --> C{决策节点}
    C -->|是| D[(数据存储节点)]
    C -->|否| E[输出节点]
    D --> F[错误处理节点]
    E --> G((结束节点))
    
%% 通用样式定义
classDef startEndStyle fill:#e8f5e8,stroke:#4caf50,stroke-width:3px,color:#000
classDef processStyle fill:#e3f2fd,stroke:#2196f3,stroke-width:2px,color:#000
classDef decisionStyle fill:#fff3e0,stroke:#ff9800,stroke-width:2px,color:#000
classDef dataStyle fill:#f3e5f5,stroke:#9c27b0,stroke-width:2px,color:#000
classDef outputStyle fill:#fce4ec,stroke:#e91e63,stroke-width:2px,color:#000
classDef errorStyle fill:#ffebee,stroke:#f44336,stroke-width:2px,color:#000
    
%% 应用样式到示例节点
class A,G startEndStyle
class B processStyle
class C decisionStyle
class D dataStyle
class E outputStyle
class F errorStyle
```
<img width="319" height="498" alt="image" src="https://github.com/user-attachments/assets/97f7b5f1-ae5b-409a-9bd2-beba9a13dab9" />




<img width="840" height="397" alt="image" src="https://github.com/user-attachments/assets/7dbfefb8-9ddf-41c4-bee2-75449e020f12" />




# 纯白简约风格

```
%%{
  init: {
    'theme': 'base',
    'themeVariables': {
      'primaryColor': '#ffffff',
      'primaryTextColor': '#333333',
      'primaryBorderColor': '#cccccc',
      'lineColor': '#888888',
      'tertiaryColor': '#D0E4FF',
      'tertiaryBorderColor': '#D0E4FF',
      'tertiaryTextColor': '#00A4FF'
    }
  }
}%%
```

主题一配置解析
如上所示，我基于 base 主题魔改了一些自定义样式。通过 themeVariables，调整了颜色方案：



```
primaryColor: #ffffff (节点背景色 - 白色)
primaryTextColor: #333333 (节点文字颜色 - 深灰色)
primaryBorderColor: #cccccc (节点边框色 - 浅灰色)
lineColor: #888888 (连接线颜色 - 中灰色)
tertiaryColor: #D0E4FF (特定节点/分组背景色 - 淡蓝色)
tertiaryBorderColor: #D0E4FF (特定节点/分组边框色 - 淡蓝色)
tertiaryTextColor: #00A4FF (特定节点/分组文字颜色 - 亮蓝色)
```


# 主题二：淡雅商务风格
第二个主题采用了更加商务化的配色方案，使用淡雅的背景色和黑色边框，更适合正式文档和商务报告。

<img width="815" height="443" alt="image" src="https://github.com/user-attachments/assets/765cf38a-3dae-4be3-8043-7557eaae6f3f" />

```
%%{
  init: {
    'theme': 'base',
    'themeVariables': {
      'primaryColor': '#F0F4FC',
      'primaryTextColor': '#1F2329',
      'primaryBorderColor': '#000000',
      'lineColor': '#888888',
      'tertiaryColor': '#F5F6F7',
      'tertiaryBorderColor': '#F5F6F7',
      'tertiaryTextColor': '#00A4FF'
    }
  }
}%%
```
主题二配置解析

这个主题使用了更加专业和商务化的色彩搭配：

```
primaryColor: #F0F4FC (节点背景色 - 淡蓝灰色)
primaryTextColor: #1F2329 (节点文字颜色 - 深色文本)
primaryBorderColor: #000000 (节点边框色 - 黑色边框)
lineColor: #888888 (连接线颜色 - 中灰色)
tertiaryColor: #F5F6F7 (特定节点/分组背景色 - 浅灰色)
tertiaryBorderColor: #F5F6F7 (特定节点/分组边框色 - 浅灰色)
tertiaryTextColor: #00A4FF (特定节点/分组文字颜色 - 亮蓝色)
```

使用示例


<img width="832" height="397" alt="image" src="https://github.com/user-attachments/assets/499dcacb-16d3-44aa-ba98-03f6e6555ae9" />


```
%%{
  init: {
    'theme': 'base',
    'themeVariables': {
      'primaryColor': '#ffffff',
      'primaryTextColor': '#333333',
      'primaryBorderColor': '#cccccc',
      'lineColor': '#888888',
      'tertiaryColor': '#D0E4FF',
      'tertiaryBorderColor': '#D0E4FF',
      'tertiaryTextColor': '#00A4FF'
    }
  }
}%%
graph TD
    subgraph client_subgraph [客户端]
        C1[客户端1]
        C2[客户端2]
        C3[客户端3]
    end

    subgraph server_subgraph [服务器集群]
        S1[服务器1 （健康）]
        S2[服务器2 （健康）]
        S3[服务器3 （不健康）]
        S4[服务器4 （健康）]
    end

    LB{负载均衡器}

    C1 --> LB
    C2 --> LB
    C3 --> LB

    LB -- 健康检查 --> S1
    LB -- 健康检查 --> S2
    LB -- 健康检查 --> S3
    LB -- 健康检查 --> S4

    LB -- 流量分配 --> S1
    LB -- 流量分配 --> S2
    LB -- 流量分配 --> S4

    %% 箭头样式：深灰色，1.5px宽度
    style S3 fill:#f99
```


<img width="832" height="397" alt="image" src="https://github.com/user-attachments/assets/defc9015-7952-4cae-a308-0bc7ed3d041d" />


![Uploading image.png…]()


https://mermaid.js.org/config/theming.html



