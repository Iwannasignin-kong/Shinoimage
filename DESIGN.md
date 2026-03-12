# ShinoGraph — 轻量知识图谱笔记插件 设计方案

## 一、产品定位

**一句话**：截图 → AI 解析 → 知识图谱 → 智能回顾问答

区别于 Obsidian/Notion 等重型工具，ShinoGraph 定位为**浏览器侧边栏插件**，
核心差异点：**零手动整理，截图即入库，AI 自动编织知识网络**。

---

## 二、核心功能模块

```
┌─────────────────────────────────────────────────────┐
│                  Chrome Extension                    │
│  ┌──────────┐  ┌──────────┐  ┌───────────────────┐  │
│  │ 截图/选区 │  │ 侧边栏   │  │ 知识图谱可视化    │  │
│  │ Capture  │  │ Sidebar  │  │ Graph View        │  │
│  └────┬─────┘  └────┬─────┘  └────────┬──────────┘  │
│       │              │                 │             │
└───────┼──────────────┼─────────────────┼─────────────┘
        │              │                 │
        ▼              ▼                 ▼
┌─────────────────────────────────────────────────────┐
│                   Backend API                        │
│  ┌──────────┐  ┌──────────┐  ┌───────────────────┐  │
│  │ OCR +    │  │ 知识抽取  │  │ 问答/回顾引擎     │  │
│  │ 图片解析 │  │ & 图谱    │  │ Q&A Engine        │  │
│  └──────────┘  └──────────┘  └───────────────────┘  │
│                                                      │
│  Storage: SQLite + 向量数据库(本地)                   │
└─────────────────────────────────────────────────────┘
```

---

## 三、技术选型（轻量优先）

| 层级 | 选型 | 理由 |
|------|------|------|
| 前端插件 | Chrome Extension (Manifest V3) + Preact | 极小体积，侧边栏渲染快 |
| 截图 | html2canvas / Chrome `captureVisibleTab` API | 浏览器原生，免权限 |
| 后端 | Python FastAPI (单文件可跑) | 轻量，AI 生态好 |
| OCR/解析 | Claude Vision API (multimodal) | 直接图片→结构化，省去 OCR 中间步骤 |
| 知识图谱存储 | SQLite + JSON Graph | 零部署，单文件数据库 |
| 向量检索 | ChromaDB (本地嵌入) | 无需外部服务，pip install 即用 |
| 图谱可视化 | D3-force / Cytoscape.js | 轻量交互式图谱 |

---

## 四、Coding 步骤拆解

### Phase 1：基础骨架（MVP）
```
Step 1 — 项目初始化
  ├── /extension        # Chrome 插件
  │   ├── manifest.json
  │   ├── popup.html    # 弹窗入口
  │   ├── sidebar.html  # 侧边栏主界面
  │   ├── content.js    # 页面截图注入脚本
  │   └── background.js # Service Worker
  ├── /backend
  │   ├── main.py       # FastAPI 入口
  │   ├── models.py     # 数据模型
  │   ├── graph.py      # 知识图谱逻辑
  │   └── ai.py         # AI 调用封装
  └── /shared
      └── types.ts      # 前后端共享类型
```

```
Step 2 — 截图捕获
  • Chrome Extension 右键菜单 / 快捷键 (Ctrl+Shift+S)
  • 支持三种模式：
    a) 全页截图
    b) 区域选取截图（拖拽框选）
    c) 选中文本直接抓取
  • 截图暂存 IndexedDB，异步上传后端
```

```
Step 3 — AI 解析管线
  • 图片/文本 → Claude Vision API
  • Prompt 模板：
    "从这张笔记截图中提取：
     1. 核心概念(entities)
     2. 概念间关系(relations)
     3. 关键摘要(summary)
     4. 可能的问答对(qa_pairs)
     返回 JSON 格式"
  • 解析结果存入 SQLite
```

```
Step 4 — 知识图谱构建
  • 节点(Node)：每个概念/实体
  • 边(Edge)：概念间关系（包含、因果、对比、扩展等）
  • 新笔记入库时，自动与已有节点做相似度匹配
  • 合并重复概念，建立跨笔记关联
```

### Phase 2：智能回顾
```
Step 5 — 问答引擎
  • 基于知识图谱的上下文检索
  • 向量相似度 + 图谱路径 联合排序
  • 支持自然语言提问，返回关联笔记 + AI 总结

Step 6 — 侧边栏 UI
  • 笔记时间线视图
  • 知识图谱力导向图
  • 搜索 + 问答对话框
  • 「今日回顾」卡片流
```

### Phase 3：体验打磨
```
Step 7 — 间隔重复回顾（Spaced Repetition）
Step 8 — 导出功能（Markdown/PDF）
Step 9 — 多端同步（可选，用 GitHub 做存储后端）
```

---

## 五、创新差异化方案 ★

### 1. 「知识星系」可视化（而非传统图谱）
```
传统 Obsidian：节点 + 连线 = 看起来都差不多，信息密度低
我们的方案：
  • 每个主题 = 一颗「星球」，大小反映笔记数量
  • 笔记 = 星球上的「地标」
  • 主题间连线 = 星际航线，粗细反映关联强度
  • 用户浏览 = 在知识宇宙中「旅行」
  → 视觉记忆远强于平面图谱
```

### 2. 「截图对话」—— 和你的笔记聊天
```
传统：截图 → 存储 → 手动检索
我们的方案：
  • 截图后直接弹出 AI 对话气泡
  • "这段和你之前存的《XX》第三章有什么关联？"
  • "帮我用费曼技巧解释这个概念"
  • "生成 5 道测试题检验我是否理解了"
  → 截图不只是「存」，而是即时交互学习
```

### 3. 「知识涟漪」—— 自动联想推送
```
传统：用户主动搜索
我们的方案：
  • 浏览网页时，侧边栏自动匹配相关历史笔记
  • 像「弹幕」一样飘出关联提示："这和你3天前存的XX有关"
  • 点击展开完整关联链路
  → 被动学习，知识在不经意间被强化
```

### 4. 「知识 DNA」—— 学习画像
```
  • 分析用户的知识图谱结构
  • 发现知识盲区："你在 ML 方向缺少概率论基础"
  • 推荐学习路径
  • 生成可分享的「知识 DNA 图」
  → 社交属性 + 成长可视化 = 高留存
```

### 5. 「思维碰撞」—— 跨领域连接
```
  • AI 主动发现不同领域概念的相似模式
  • "你存的经济学'边际效用递减'和心理学'享乐适应'是同一个模式"
  • 帮助用户建立跨学科思维
  → 超越笔记工具，成为思维方式训练器
```

---

## 六、技术实现优先级

```
  高 ─┐
     │  P0: 截图 → AI 解析 → 存储（核心管线）
     │  P0: 侧边栏基础 UI
     │  P1: 知识图谱构建 + 可视化
     │  P1: 问答引擎
     │  P2: 知识涟漪（浏览时自动匹配）
     │  P2: 间隔重复回顾
     │  P3: 知识星系可视化
     │  P3: 知识 DNA 画像
  低 ─┘
```

---

## 七、数据模型设计

```sql
-- 笔记条目
CREATE TABLE notes (
    id          TEXT PRIMARY KEY,
    source_url  TEXT,
    source_title TEXT,
    image_path  TEXT,          -- 截图路径
    raw_text    TEXT,          -- OCR/提取的原文
    summary     TEXT,          -- AI 生成摘要
    embedding   BLOB,          -- 向量嵌入
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 知识实体
CREATE TABLE entities (
    id          TEXT PRIMARY KEY,
    name        TEXT UNIQUE,
    category    TEXT,          -- 学科/领域分类
    description TEXT,
    embedding   BLOB,
    note_count  INTEGER DEFAULT 1
);

-- 实体关系（图谱边）
CREATE TABLE relations (
    id          TEXT PRIMARY KEY,
    source_id   TEXT REFERENCES entities(id),
    target_id   TEXT REFERENCES entities(id),
    relation    TEXT,          -- 包含/因果/对比/扩展/相似
    strength    REAL DEFAULT 1.0,
    evidence    TEXT           -- 关系来源笔记
);

-- 笔记-实体 关联
CREATE TABLE note_entities (
    note_id     TEXT REFERENCES notes(id),
    entity_id   TEXT REFERENCES entities(id),
    PRIMARY KEY (note_id, entity_id)
);

-- 问答对
CREATE TABLE qa_pairs (
    id          TEXT PRIMARY KEY,
    note_id     TEXT REFERENCES notes(id),
    question    TEXT,
    answer      TEXT,
    next_review DATETIME,      -- 间隔重复下次复习时间
    ease_factor REAL DEFAULT 2.5
);
```

---

## 八、文件结构（最终）

```
Shinoimage/
├── extension/
│   ├── manifest.json
│   ├── src/
│   │   ├── popup/          # 插件弹窗
│   │   ├── sidebar/        # 侧边栏主界面
│   │   │   ├── App.tsx
│   │   │   ├── NoteTimeline.tsx
│   │   │   ├── GraphView.tsx
│   │   │   ├── ChatPanel.tsx
│   │   │   └── ReviewCards.tsx
│   │   ├── content/        # 注入页面的脚本
│   │   │   ├── capture.ts  # 截图逻辑
│   │   │   └── ripple.ts   # 知识涟漪匹配
│   │   ├── background/
│   │   │   └── service-worker.ts
│   │   └── shared/
│   │       └── api.ts      # 后端通信
│   ├── public/
│   └── vite.config.ts
├── backend/
│   ├── main.py             # FastAPI 入口
│   ├── routers/
│   │   ├── notes.py        # 笔记 CRUD
│   │   ├── graph.py        # 图谱查询
│   │   └── chat.py         # 问答接口
│   ├── services/
│   │   ├── ai_parser.py    # AI 解析服务
│   │   ├── graph_builder.py# 图谱构建
│   │   ├── vector_store.py # 向量检索
│   │   └── reviewer.py     # 间隔重复
│   ├── models.py           # SQLAlchemy 模型
│   ├── database.py         # DB 初始化
│   └── requirements.txt
├── img/                    # 原有图床目录
└── DESIGN.md               # 本文档
```
