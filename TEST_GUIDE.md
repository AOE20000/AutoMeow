# 测试指南

## 快速开始

### 1. 运行完整测试套件

测试所有 30+ 个场景：

```bash
python test_meow_rules.py
```

预期输出：
```
============================================================
喵语规则测试
============================================================

已加载 7 条规则

✓ 通过 - 基础句号
✓ 通过 - 基础问号
...
============================================================
测试完成: 30 通过, 0 失败
============================================================
```

### 2. 测试单个文本

#### 命令行模式

```bash
python test_single_text.py "你好，世界"
```

输出：
```
输入: 你好，世界
输出: 你好喵，世界喵
```

#### 交互模式

```bash
python test_single_text.py
```

然后输入文本进行测试：
```
>>> 你好，世界
转换结果: 你好喵，世界喵

>>> quit
再见喵~
```

### 3. 测试复杂场景

```bash
python test_single_text.py "在地址栏输入about:config 并按回车。"
```

输出：
```
输入: 在地址栏输入about:config 并按回车。
输出: 在地址栏输入about:config 并按回车喵。
```

注意：`about:config` 被正确保护，没有被破坏。

---

## 测试场景覆盖

### 基础功能
- ✓ 句号、问号、感叹号前添加"喵"
- ✓ 逗号、顿号、分号前添加"喵"
- ✓ 右括号前添加"喵"
- ✓ 换行前添加"喵"（包括无标点换行）
- ✓ 句尾添加"喵"

### 智能保护
- ✓ URL 保护（`about:config`, `https://example.com`）
- ✓ 配置项保护（`privacy.exposeContentTitleInWindow`）
- ✓ 文件路径保护（`C:\Users\test.txt`）
- ✓ 邮箱地址保护（`test@example.com`）
- ✓ 版本号保护（`3.14.159`）
- ✓ 英文句子保护（`Hello world.`）

### 边界情况
- ✓ 空字符串
- ✓ 只有标点
- ✓ 连续标点
- ✓ 已有"喵"不重复添加
- ✓ 括号嵌套

---

## 自定义测试

### 添加新测试用例

编辑 `test_meow_rules.py`，在 `test_cases` 列表中添加：

```python
("测试名称", "输入文本", "期望输出"),
```

示例：
```python
("自定义测试", "这是测试。", "这是测试喵。"),
```

### 修改规则

编辑 `.meowparser/rules/default.json`，然后运行测试验证：

```bash
python test_meow_rules.py
```

---

## 常见问题

### Q: 为什么冒号后的配置项没有添加"喵"？

A: 这是智能保护功能。当冒号后紧跟字母、数字、点等字符时（如 `privacy.test`），规则会自动保护，避免破坏技术内容。

示例：
- `输入：privacy.test` → `输入：privacy.test喵` ✓
- `注意：这很重要` → `注意喵：这很重要喵` ✓

### Q: 为什么 URL 没有被破坏？

A: 规则使用正则表达式的负向前瞻（`(?![a-zA-Z0-9_\-\.:/])`）来检测 URL 和配置项，自动跳过这些内容。

### Q: 如何测试换行？

A: 在命令行中使用 `\n` 或在交互模式中直接按回车：

```bash
python test_single_text.py "第一行\n第二行"
```

输出：
```
输入: 第一行\n第二行
输出: 第一行喵\n第二行喵
```

### Q: 测试失败怎么办？

1. 检查规则文件是否正确：`.meowparser/rules/default.json`
2. 查看失败的测试用例详情
3. 使用 `test_single_text.py` 单独测试该场景
4. 参考 `docs/RULES_OPTIMIZATION.md` 了解规则逻辑

---

## Python 版本要求

- Python 3.8+
- 推荐使用 Python 3.11

测试命令：
```bash
python --version
python test_meow_rules.py
```

或指定版本：
```bash
python311 test_meow_rules.py
```

---

## 持续集成

可以将测试集成到 CI/CD 流程中：

```bash
# 运行测试并检查退出码
python test_meow_rules.py
if [ $? -eq 0 ]; then
    echo "所有测试通过"
else
    echo "测试失败"
    exit 1
fi
```

---

## 性能测试

测试大量文本的转换性能：

```python
import time
from test_meow_rules import load_rules, apply_rules

rules = load_rules()
text = "你好，世界。" * 1000

start = time.time()
result = apply_rules(text, rules)
end = time.time()

print(f"处理 {len(text)} 字符耗时: {end - start:.4f} 秒")
```

---

## 更多信息

- 规则详细说明：`docs/RULES_OPTIMIZATION.md`
- 更新日志：`docs/CHANGELOG.md`
- 项目文档：`README.md`
