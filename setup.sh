#!/bin/bash

echo "开始设置标签格式分类工具..."

# 检查是否已安装UV
if ! command -v uv &> /dev/null; then
    echo "未找到UV，正在尝试安装..."
    if command -v pip &> /dev/null; then
        pip install uv
    else
        echo "错误：未找到pip。请先安装Python和pip，然后再运行此脚本。"
        exit 1
    fi
fi

echo "创建虚拟环境..."
uv venv

echo "激活虚拟环境..."
source .venv/bin/activate

echo "安装依赖包..."
uv sync

echo "设置脚本执行权限..."
chmod +x run.sh

echo "============================================"
echo "安装完成！可以使用以下命令启动程序："
echo "./run.sh [文件夹路径]"
echo "============================================" 