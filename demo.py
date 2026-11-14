#!/usr/bin/env python3
"""示例脚本，演示 wired-ffi 的基本用法"""

import json
import os
import subprocess
from pathlib import Path


def run_command(cmd):
    """运行命令并返回结果"""
    print(f"执行: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.stdout:
        print(f"输出: {result.stdout.strip()}")
    if result.stderr:
        print(f"错误: {result.stderr.strip()}")
    print("-" * 50)
    return result


def main():
    print("wired-ffi 示例演示")
    print("=" * 50)

    # 1. 显示版本信息
    print("\n1. 显示程序信息:")
    run_command("uv run wired-ffi info")

    # 2. 创建示例数据
    print("\n2. 创建示例数据:")
    sample_data = {
        "user_id": 12345,
        "username": "张三",
        "email": "zhangsan@example.com",
        "preferences": {"language": "zh-CN", "theme": "dark", "notifications": True},
        "tags": ["developer", "python", "ffi"],
    }

    with open("demo_data.json", "w", encoding="utf-8") as f:
        json.dump(sample_data, f, indent=2, ensure_ascii=False)
    print("已创建 demo_data.json")

    # 3. 序列化为不同格式
    print("\n3. 序列化演示:")

    # JSON to Pickle
    run_command(
        "uv run wired-ffi serialize --format pickle demo_data.json demo_data.pkl"
    )

    # JSON to JSON (复制)
    run_command(
        "uv run wired-ffi serialize --format json demo_data.json demo_data_copy.json"
    )

    # 4. 反序列化演示
    print("\n4. 反序列化演示:")

    # Pickle to JSON
    run_command(
        "uv run wired-ffi deserialize --format pickle demo_data.pkl restored_data.json"
    )

    # 5. FFI 调用演示
    print("\n5. FFI 调用演示:")

    # 创建 FFI 请求
    ffi_request = {
        "function_name": "process_user_data",
        "args": [sample_data],
        "kwargs": {"validate": True, "transform": "uppercase_username"},
    }

    with open("ffi_request.json", "w", encoding="utf-8") as f:
        json.dump(ffi_request, f, indent=2, ensure_ascii=False)
    print("已创建 ffi_request.json")

    # 执行 FFI 调用
    run_command("uv run wired-ffi call ffi_request.json ffi_response.json")

    # 6. 显示结果
    print("\n6. 查看结果:")

    files_to_show = ["restored_data.json", "ffi_response.json"]

    for filename in files_to_show:
        if os.path.exists(filename):
            print(f"\n{filename} 内容:")
            with open(filename, encoding="utf-8") as f:
                content = json.load(f)
                print(json.dumps(content, indent=2, ensure_ascii=False))

    print("\n演示完成！")
    print("\n生成的文件:")
    for file in Path(".").glob("demo_*"):
        print(f"  - {file}")
    for file in Path(".").glob("ffi_*"):
        print(f"  - {file}")
    for file in Path(".").glob("restored_*"):
        print(f"  - {file}")


if __name__ == "__main__":
    main()
