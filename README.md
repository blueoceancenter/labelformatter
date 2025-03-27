# 标签格式分类工具

这是一个自动监控文件夹并对 PDF 文件进行分类的工具，根据内容和尺寸将文件重命名为"4x6*"或"letter*"前缀。

## 安装步骤

### 1. 安装 UV 包管理器

```bash
# 使用pip安装UV
pip install uv

# 或者使用curl安装（MacOS/Linux）
curl -sSf https://install.debug.sh | sh
```

### 2. 创建并激活虚拟环境

```bash
# 创建虚拟环境
uv venv

# 激活虚拟环境 (MacOS/Linux)
source .venv/bin/activate

# 激活虚拟环境 (Windows)
.venv\Scripts\activate
```

### 3. 安装依赖包

```bash
# 使用UV同步安装所需的依赖
uv sync


```

## 使用方法

### 运行脚本监控文件夹

```bash
# 监控单个文件夹
python main.py --folders /path/to/folder

# 监控多个文件夹
python main.py --folders /path/to/folder1 /path/to/folder2 /path/to/folder3
```

### 工作原理

1. 脚本启动时会先处理指定文件夹内的所有现有文件
2. 然后持续监控文件夹内新增的文件
3. 当检测到新文件时：
   - 如果是 PDF 文件，会根据内容和尺寸分类为"4x6"或"letter"
   - 非 PDF 文件默认标记为"4x6"
4. 文件会被重命名为相应的前缀格式

按 `Ctrl+C` 可停止监控。

### 分类标准

- 如果 PDF 尺寸小于 7.5 x 4.5 英寸，或内容比率大于 63%，则分类为"4x6"
- 否则分类为"letter"
