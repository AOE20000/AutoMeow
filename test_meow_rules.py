#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
喵语规则测试脚本
测试各种场景下的文本转换效果
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


def load_rules(config_path):
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


def test_case(name, input_text, expected_output, rules):
    """测试单个用例"""
    actual_output = apply_rules(input_text, rules)
    passed = actual_output == expected_output
    
    # 使用 ASCII 兼容的符号
    status = "[PASS]" if passed else "[FAIL]"
    print(f"\n{status} - {name}")
    print(f"输入: {repr(input_text)}")
    print(f"期望: {repr(expected_output)}")
    print(f"实际: {repr(actual_output)}")
    
    if not passed:
        print(f"差异:")
        print(f"  期望长度: {len(expected_output)}")
        print(f"  实际长度: {len(actual_output)}")
        for i, (e, a) in enumerate(zip(expected_output, actual_output)):
            if e != a:
                print(f"  位置 {i}: 期望 {repr(e)}, 实际 {repr(a)}")
    
    return passed


def run_tests():
    """运行所有测试"""
    print("=" * 60)
    print("喵语规则测试")
    print("=" * 60)
    
    # 加载规则
    try:
        rules = load_rules('.meowparser/rules/default.json')
        print(f"\n已加载 {len(rules)} 条规则")
    except Exception as e:
        print(f"加载规则失败: {e}")
        return
    
    # 测试用例
    test_cases = [
        # 基础标点测试
        ("基础句号", "你好。", "你好喵。"),
        ("基础问号", "为什么？", "为什么喵？"),
        ("基础感叹号", "太棒了！", "太棒了喵！"),
        ("基础逗号", "你好，世界", "你好喵，世界喵"),
        
        # URL和配置项测试
        ("URL保护", "访问about:config并确认", "访问about:config并确认喵"),
        ("配置项保护", "设置privacy.exposeContentTitleInWindow为false", 
         "设置privacy.exposeContentTitleInWindow为false喵"),
        ("完整URL", "打开https://example.com查看", "打开https://example.com查看喵"),
        
        # 冒号测试
        ("中文冒号后跟中文", "注意：这很重要", "注意喵：这很重要喵"),
        ("中文冒号后跟英文配置", "输入：privacy.test", "输入：privacy.test喵"),  # 冒号后跟配置项，保护不添加喵
        ("英文冒号在URL中", "about:config", "about:config喵"),  # 纯URL也会在句尾添加喵
        ("单独URL", "访问about:config", "访问about:config喵"),
        
        # 括号测试
        ("括号内容", "（没有问题）继续", "（没有问题喵）继续喵"),
        ("多层括号", "这是（一个（嵌套）的）例子", "这是（一个（嵌套喵）的喵）例子喵"),
        
        # 换行测试
        ("单行换行", "第一行\n第二行", "第一行喵\n第二行喵"),
        ("多行换行", "第一行\n第二行\n第三行", "第一行喵\n第二行喵\n第三行喵"),
        ("无标点换行", "这是一行\n这是另一行", "这是一行喵\n这是另一行喵"),
        ("标点后换行", "你好。\n世界", "你好喵。\n世界喵"),
        
        # 句尾测试
        ("无标点句尾", "你好世界", "你好世界喵"),
        ("有标点句尾", "你好世界。", "你好世界喵。"),
        
        # 复杂场景测试
        ("完整示例", 
         '在地址栏输入about:config 并按回车。 （没有问题）点击"接受风险并继续"。 在搜索框中输入：privacy.exposeContentTitleInWindow。 将该项的值切换为false。 注意： 如果你使用的是隐私浏览模式，还需要找到privacy.exposeContentTitleInWindow.pbm 并同样设置为false。',
         '在地址栏输入about:config 并按回车喵。 （没有问题喵）点击"接受风险并继续"喵。 在搜索框中输入：privacy.exposeContentTitleInWindow喵。 将该项的值切换为false喵。 注意喵： 如果你使用的是隐私浏览模式喵，还需要找到privacy.exposeContentTitleInWindow.pbm 并同样设置为false喵。'),  # 冒号后跟配置项，保护不添加喵
        
        # 边界情况
        ("空字符串", "", ""),
        ("只有标点", "。", "。"),
        ("连续标点", "什么？！", "什么喵？！"),
        ("已有喵", "你好喵。", "你好喵。"),
        ("英文句子", "Hello world.", "Hello world."),  # 英文句号结尾不添加喵
        
        # 特殊字符
        ("文件路径", "打开C:\\Users\\test.txt文件", "打开C:\\Users\\test.txt文件喵"),
        ("邮箱地址", "发送到test@example.com", "发送到test@example.com喵"),
        ("数字和点", "版本3.14.159", "版本3.14.159喵"),
        
        # 分号测试
        ("分号", "第一项；第二项", "第一项喵；第二项喵"),
        
        # 顿号测试
        ("顿号", "苹果、香蕉、橙子", "苹果喵、香蕉喵、橙子喵"),
    ]
    
    # 运行测试
    passed = 0
    failed = 0
    
    for name, input_text, expected in test_cases:
        if test_case(name, input_text, expected, rules):
            passed += 1
        else:
            failed += 1
    
    # 输出统计
    print("\n" + "=" * 60)
    print(f"测试完成: {passed} 通过, {failed} 失败")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
