# wired-ffi

wired-ffi 是一个基于序列化的跨语言接口（FFI, Foreign Function Interface）库。旨在简化不同编程语言之间的函数调用和数据交换。通过统一的序列化机制，实现跨语言的函数接口调用。

## 安装

使用 uv 进行开发：

```bash
# 克隆项目
git clone <repository-url>
cd wired-ffi

# 使用 uv 同步依赖
uv sync

# 运行程序
uv run wired-ffi --help
```

## 使用方法

### 查看帮助信息

```bash
uv run wired-ffi --help
uv run wired-ffi info
```

### 序列化数据

```bash
# 将 JSON 数据序列化为 Pickle 格式
uv run wired-ffi serialize --format pickle input.json output.pkl

# 使用 MessagePack 格式
uv run wired-ffi serialize --format msgpack input.json output.msgpack
```

### 反序列化数据

```bash
# 将 Pickle 数据反序列化为 JSON
uv run wired-ffi deserialize --format pickle input.pkl output.json
```

### FFI 函数调用

```bash
# 处理 FFI 请求
uv run wired-ffi call request.json response.json
```

请求文件格式示例：
```json
{
  "function_name": "calculate_sum",
  "args": [10, 20, 30],
  "kwargs": {
    "multiply_by": 2,
    "add_bonus": 5
  }
}
```

## 开发

### 项目结构

```
wired-ffi/
├── wired_ffi/
│   ├── __init__.py     # 包初始化
│   ├── main.py         # CLI 入口点
│   └── core.py         # 核心 FFI 功能
├── pyproject.toml      # 项目配置
├── README.md           # 项目文档
└── uv.lock            # 依赖锁定文件
```

### 运行测试

```bash
# 运行测试（如果有）
uv run pytest

# 代码格式化
uv run black .

# 类型检查
uv run mypy wired_ffi
uv run pyright wired_ffi

# 运行所有质量检查
uv run ruff check .
uv run isort --check-only .
```

### 开发工具

项目使用以下开发工具确保代码质量：

- **mypy**: 静态类型检查器
- **Pyright**: Microsoft 的高性能 Python 类型检查器，提供更快的检查速度和更好的 VS Code 集成
- **black**: 代码格式化工具
- **ruff**: 现代 Python 代码检查器
- **isort**: 导入排序工具
- **pytest**: 测试框架

#### VS Code 开发体验

项目已配置了 VS Code 工作区设置，包括：
- 自动类型检查（mypy + Pyright）
- 保存时自动格式化
- 导入自动排序
- 推荐的扩展插件

开发者可以直接打开项目获得最佳的开发体验。

## 技术栈

- **Python 3.13+**: 主要编程语言
- **uv**: 现代 Python 包管理器
- **Click**: 命令行界面框架
- **支持的序列化格式**: JSON、Pickle、MessagePack

## 贡献

欢迎提交 Issues 和 Pull Requests！

## 许可证

MIT License
