#!/bin/bash
# ShinoGraph 一键安装脚本

set -e

echo "=== ShinoGraph 安装 ==="

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "ERROR: 需要 Python 3.10+"
    exit 1
fi

echo "[1/3] 安装 Python 依赖..."
pip install -r backend/requirements.txt -q

echo "[2/3] 配置环境变量..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "  已创建 .env 文件"
    echo "  请编辑 .env 填入你的 ANTHROPIC_API_KEY"
    echo ""
    read -p "  输入你的 Anthropic API Key (回车跳过): " api_key
    if [ -n "$api_key" ]; then
        sed -i "s|ANTHROPIC_API_KEY=sk-ant-xxx|ANTHROPIC_API_KEY=$api_key|" .env
        echo "  API Key 已保存"
    fi
else
    echo "  .env 已存在，跳过"
fi

echo "[3/3] 启动服务..."
echo ""
echo "=== 安装完成 ==="
echo ""
echo "启动命令:  python run.py"
echo "API 文档:  http://localhost:8000/docs"
echo "Chrome 插件: 加载 extension/ 目录"
