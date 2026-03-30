#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
单文本测试工具
快速测试喵语转换效果
"""

import re
import json
import sys
import io

# 设置 Windows 控制台编码
if sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    except:
        pass


def load_rules(config_path='.meowparser/rules/default.json'):
    """加载规则配置"""
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    rules = []
    for group in config.get('groups', []):
        for rule in group.get('rules', []):
            if rule.get('enabled', True):
                rules.append(rule)
    return rules


def apply_rules(text, rules):
    """应用替换规则"""
    result = text
    for rule in rules:
        pattern = rule['pattern']
        replacement = rule['replacement']
        is_regex = rule.get('is_regex', False)
        
        if is_regex:
            result = re.sub(pattern, replacement, result)
        else:
            result = result.replace(pattern, replacement)
    
    return result


def main():
    """主函数"""
    print("=" * 60)
    print("喵语转换测试工具")
    print("=" * 60)
    print()
    
    # 加载规则
    try:
        rules = load_rules()
        print(f"[OK] 已加载 {len(rules)} 条规则\n")
    except Exception as e:
        print(f"[ERROR] 加载规则失败: {e}")
        return 1
    
    # 交互式测试
    if len(sys.argv) > 1:
        # 命令行参数模式
        text = ' '.join(sys.argv[1:])
        result = apply_rules(text, rules)
        print(f"输入: {text}")
        print(f"输出: {result}")
    else:
        # 交互模式
        print("请输入要转换的文本（输入 'quit' 或 'exit' 退出）：")
        print()
        
        while True:
            try:
                text = input(">>> ")
                
                if text.lower() in ['quit', 'exit', 'q']:
                    print("\n再见喵~")
                    break
                
                if not text.strip():
                    continue
                
                result = apply_rules(text, rules)
                print(f"转换结果: {result}")
                print()
                
            except KeyboardInterrupt:
                print("\n\n再见喵~")
                break
            except EOFError:
                break
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
