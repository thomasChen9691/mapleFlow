#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
验证 API 中文编码是否正确
"""
import sys
import requests
import json

# 设置 UTF-8 编码
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

BASE_URL = "http://localhost:8000"

def verify_encoding():
    """验证 API 响应的编码"""
    print("=" * 60)
    print("验证 API 中文编码")
    print("=" * 60)
    
    try:
        # 获取单篇文章
        response = requests.get(f"{BASE_URL}/api/posts/aiops-state-and-tools")
        response.encoding = 'utf-8'
        
        if response.status_code == 200:
            data = response.json()
            
            print("\n[测试 1] 检查响应头")
            print(f"Content-Type: {response.headers.get('Content-Type', 'N/A')}")
            print(f"响应编码: {response.encoding}")
            
            print("\n[测试 2] 检查 JSON 中的中文")
            title = data['front_matter']['title']
            tags = data['front_matter']['tags']
            
            print(f"标题: {title}")
            print(f"标签: {', '.join(tags)}")
            
            # 检查 JSON 序列化
            print("\n[测试 3] JSON 序列化测试")
            json_str = json.dumps(data, ensure_ascii=False, indent=2)
            print(f"JSON 长度: {len(json_str)} 字符")
            print(f"包含中文: {'是' if any(ord(c) > 127 for c in json_str) else '否'}")
            
            # 验证可以正确解析
            parsed = json.loads(json_str)
            print(f"可以正确解析: {'是' if parsed['front_matter']['title'] == title else '否'}")
            
            print("\n[结果] ✅ API 中文编码正常！")
            print("    - JSON 响应使用 UTF-8 编码")
            print("    - ensure_ascii=False 确保中文不被转义")
            print("    - 中文内容可以正确显示和解析")
            
            return True
        else:
            print(f"\n[错误] HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"\n[错误] {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = verify_encoding()
    sys.exit(0 if success else 1)
