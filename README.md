# ShinoGraph — 截图笔记知识图谱插件

截图 → AI 解析 → 知识图谱 → 智能问答

## 快速开始

### 1. 下载

```bash
git clone https://github.com/Iwannasignin-kong/Shinoimage.git
cd Shinoimage
```

### 2. 安装依赖

```bash
pip install -r backend/requirements.txt
```

### 3. 配置 API Key

```bash
cp .env.example .env
# 编辑 .env，填入你的 ANTHROPIC_API_KEY
```

### 4. 启动后端

```bash
python run.py
# → http://localhost:8000      (API)
# → http://localhost:8000/docs (Swagger 文档，可直接测试)
```

### 5. 安装 Chrome 插件

1. 打开 Chrome → 地址栏输入 `chrome://extensions/`
2. 右上角开启「开发者模式」
3. 点击「加载已解压的扩展程序」
4. 选择项目中的 `extension/` 目录
5. 完成！工具栏会出现 ShinoGraph 图标

## 使用方式

| 操作 | 方式 |
|------|------|
| 截图捕获 | `Ctrl+Shift+S` 或右键菜单 |
| 抓取选中文本 | `Ctrl+Shift+E` 或右键选中文本 |
| 打开知识面板 | 点击工具栏图标 → 「打开知识面板」 |
| AI 问答 | 侧边栏「问答」Tab |
| 查看图谱 | 侧边栏「图谱」Tab |

## API 接口

不装插件也能直接调 API 玩：

```bash
# 提交一段文本笔记
curl -X POST http://localhost:8000/api/notes/capture \
  -F "text=机器学习是人工智能的子集，深度学习是机器学习的子集。神经网络是深度学习的基础架构。"

# 查看笔记列表
curl http://localhost:8000/api/notes/

# 查看知识图谱
curl http://localhost:8000/api/graph/

# 问答
curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{"question": "深度学习和机器学习是什么关系？"}'

# 上传截图
curl -X POST http://localhost:8000/api/notes/capture \
  -F "image=@screenshot.png"
```

打开 http://localhost:8000/docs 有完整的 Swagger UI 可以直接在浏览器里测试所有接口。
