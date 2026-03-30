# MeowParser 重构快速参考

## 📋 一句话总结
将 2823 行的单文件拆分为 14+ 个模块，提高可维护性。

---

## 🎯 核心目标
- 模块化架构
- 职责分离
- 易于维护
- 易于测试

---

## 📁 新结构速览

```
meow_parser/
├── core/          # 核心功能（配置、文本处理）
├── ui/            # UI组件（窗口、编辑器）
├── platform/      # 平台代码（Windows/Linux/macOS）
├── app.py         # 主应用
└── __main__.py    # 入口
```

---

## 🔢 数字对比

| 指标 | 重构前 | 重构后 |
|------|--------|--------|
| 文件数 | 1 | 14+ |
| 最大文件行数 | 2823 | ~700 |
| 模块化程度 | 0% | 100% |
| 可测试性 | 低 | 高 |

---

## 📦 模块清单

### Core（核心）
- `config_manager.py` - 配置管理（~200行）
- `text_processor.py` - 文本处理（~30行）
- `instance_lock.py` - 单实例（~40行）

### UI（界面）
- `floating_window.py` - 悬浮窗（~350行）
- `window_selector.py` - 窗口管理（~310行）
- `config_editor.py` - 配置编辑（~280行）
- `rule_editor.py` - 规则编辑（~570行）
- `debug_window.py` - 调试窗口（~65行）
- `tray_icon.py` - 托盘图标（~80行）

### Platform（平台）
- `windows.py` - Windows（~150行）
- `linux.py` - Linux（~150行）
- `macos.py` - macOS（预留）

### Main（主程序）
- `app.py` - 主应用（~700行）
- `constants.py` - 常量（~50行）
- `__main__.py` - 入口（~30行）

---

## ⏱️ 时间估算

| 阶段 | 时间 |
|------|------|
| 准备工作 | 30分钟 |
| 核心模块 | 1小时 |
| UI模块 | 2小时 |
| 平台模块 | 1小时 |
| 主应用 | 1小时 |
| 测试验证 | 1小时 |
| **总计** | **6-7小时** |

---

## ✅ 快速开始

### 1. 查看预览
```bash
python scripts/refactor_preview.py
```

### 2. 备份代码
```bash
cp meow_parser.py meow_parser.py.backup
```

### 3. 选择方式
- **手动**：按 `REFACTORING_GUIDE.md` 执行
- **自动**：运行重构脚本（待开发）

---

## 🔍 关键文件

| 文件 | 用途 |
|------|------|
| `REFACTORING_PLAN.md` | 详细计划 |
| `REFACTORING_GUIDE.md` | 实施指南 |
| `REFACTORING_SUMMARY.md` | 总结文档 |
| `scripts/refactor_preview.py` | 预览脚本 |

---

## ✨ 主要优势

- ✅ **可维护性** - 每个模块职责单一
- ✅ **可测试性** - 模块可独立测试
- ✅ **可扩展性** - 新功能作为新模块
- ✅ **代码复用** - 模块可在其他项目复用
- ✅ **团队协作** - 多人可同时开发

---

## 🛡️ 兼容性

### 使用方式
```bash
# 旧方式（仍支持）
python meow_parser.py

# 新方式
python -m meow_parser
```

### 保证
- ✅ 配置文件不变
- ✅ 功能完全一致
- ✅ 用户体验不变

---

## 📝 测试清单

### 必测功能
- [ ] 程序启动
- [ ] 悬浮窗
- [ ] 文本替换
- [ ] 窗口管理
- [ ] 配置编辑
- [ ] 调试窗口

### 必测平台
- [ ] Windows
- [ ] Linux
- [ ] macOS（可选）

---

## ⚠️ 注意事项

1. **备份代码** - 重构前务必备份
2. **渐进式** - 逐步拆分和测试
3. **保持可运行** - 每步都要能运行
4. **充分测试** - 每个模块都要测试

---

## 🚀 下一步

1. 阅读 `REFACTORING_PLAN.md`
2. 运行 `scripts/refactor_preview.py`
3. 备份当前代码
4. 开始重构！

---

## 📞 获取帮助

- 查看详细文档
- 运行预览脚本
- 检查测试清单

---

**状态：** 📋 计划完成  
**下一步：** 🚀 开始实施
