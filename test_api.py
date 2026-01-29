#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
FastAPI 后端测试脚本
用于测试博客内容 API 是否正常工作（跨平台支持）
"""
import sys
import json
import requests
from typing import Dict, Any
import os

# 设置标准输出编码为 UTF-8
if sys.platform == "win32":
    # Windows 系统设置 UTF-8 编码
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    # 设置环境变量
    os.environ['PYTHONIOENCODING'] = 'utf-8'
else:
    # Linux/macOS 设置 locale
    import locale
    try:
        locale.setlocale(locale.LC_ALL, "en_US.UTF-8")
    except:
        pass

BASE_URL = "http://localhost:8000"


def print_section(title: str):
    """打印章节标题"""
    print(f"\n{'='*50}")
    print(f" {title}")
    print(f"{'='*50}")


def print_result(success: bool, message: str, data: Any = None):
    """打印测试结果"""
    # 使用简单的符号避免编码问题
    status = "[OK]" if success else "[FAIL]"
    print(f"{status} {message}")
    if data:
        print(f"   数据: {data}")


def test_health_check() -> bool:
    """测试健康检查端点"""
    print_section("1. 健康检查")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_result(True, f"状态: {data.get('status')}")
            return True
        else:
            print_result(False, f"HTTP {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print_result(False, f"连接失败: {e}")
        return False


def test_get_all_posts() -> bool:
    """测试获取所有文章"""
    print_section("2. 获取所有文章")
    try:
        response = requests.get(f"{BASE_URL}/api/posts", timeout=10)
        response.encoding = 'utf-8'  # 确保 UTF-8 编码
        
        if response.status_code == 200:
            data = response.json()
            total = data.get('total', 0)
            posts = data.get('posts', [])
            
            print_result(True, f"成功获取 {total} 篇文章")
            print("\n   文章列表:")
            for i, post in enumerate(posts, 1):
                title = post.get('front_matter', {}).get('title', 'Unknown')
                slug = post.get('slug', 'unknown')
                print(f"   {i}. {title} (slug: {slug})")
            
            return True
        else:
            print_result(False, f"HTTP {response.status_code}: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print_result(False, f"请求失败: {e}")
        return False
    except json.JSONDecodeError as e:
        print_result(False, f"JSON 解析失败: {e}")
        print(f"   响应内容: {response.text[:200]}")
        return False


def test_get_single_post() -> bool:
    """测试获取单篇文章"""
    print_section("3. 获取单篇文章")
    slug = "aiops-state-and-tools"
    try:
        response = requests.get(f"{BASE_URL}/api/posts/{slug}", timeout=10)
        response.encoding = 'utf-8'
        
        if response.status_code == 200:
            data = response.json()
            front_matter = data.get('front_matter', {})
            
            print_result(True, f"成功获取文章: {slug}")
            print(f"   标题: {front_matter.get('title')}")
            print(f"   日期: {front_matter.get('date')}")
            print(f"   分类: {', '.join(front_matter.get('categories', []))}")
            print(f"   标签: {', '.join(front_matter.get('tags', []))}")
            print(f"   内容长度: {len(data.get('content', ''))} 字符")
            
            return True
        else:
            print_result(False, f"HTTP {response.status_code}: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print_result(False, f"请求失败: {e}")
        return False


def test_search_posts() -> bool:
    """测试搜索功能"""
    print_section("4. 搜索文章")
    query = "docker"
    try:
        response = requests.get(
            f"{BASE_URL}/api/posts/search",
            params={"q": query},
            timeout=10
        )
        response.encoding = 'utf-8'
        
        if response.status_code == 200:
            data = response.json()
            total = data.get('total', 0)
            posts = data.get('posts', [])
            
            print_result(True, f"搜索 '{query}' 找到 {total} 篇文章")
            if posts:
                print("\n   匹配的文章:")
                for i, post in enumerate(posts, 1):
                    title = post.get('front_matter', {}).get('title', 'Unknown')
                    print(f"   {i}. {title}")
            
            return True
        else:
            print_result(False, f"HTTP {response.status_code}: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print_result(False, f"请求失败: {e}")
        return False


def test_env_config() -> bool:
    """检查环境变量配置"""
    print_section("5. 检查环境变量配置")
    import os
    from pathlib import Path
    
    env_file = Path(".env")
    if env_file.exists():
        print_result(True, ".env 文件存在")
        try:
            with open(env_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            configured = []
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    if 'your_' not in line.lower() and 'here' not in line.lower():
                        key = line.split('=')[0].strip()
                        configured.append(key)
            
            if configured:
                print(f"   已配置项: {len(configured)} 个")
                print(f"   配置项: {', '.join(configured)}")
            else:
                print("   [WARN] 警告: 请配置实际的 API keys")
            
            return True
        except Exception as e:
            print_result(False, f"读取 .env 文件失败: {e}")
            return False
    else:
        print_result(False, ".env 文件不存在，请从 .env.example 复制并配置")
        return False


def main():
    """主函数"""
    print("\n" + "="*50)
    print(" FastAPI 后端 API 测试")
    print("="*50)
    
    results = []
    
    # 运行所有测试
    results.append(("健康检查", test_health_check()))
    results.append(("获取所有文章", test_get_all_posts()))
    results.append(("获取单篇文章", test_get_single_post()))
    results.append(("搜索文章", test_search_posts()))
    results.append(("环境配置", test_env_config()))
    
    # 打印总结
    print_section("测试总结")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"   {name}: {status}")
    
    print(f"\n总计: {passed}/{total} 项测试通过")
    
    if passed == total:
        print("\n[SUCCESS] 所有测试通过！")
        return 0
    else:
        print(f"\n[WARN] 有 {total - passed} 项测试失败")
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] 发生未预期的错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
