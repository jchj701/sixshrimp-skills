# 禁止文件清单

> 以下文件不应出现在Skill目录中

---

## 禁止文件列表

| 文件名 | 原因 | 扣分 |
|:---|:---|:---:|
| README.md | Skill说明在SKILL.md中 | -2分 |
| CHANGELOG.md | 开发记录，不应出现 | -2分 |
| TODO.md | 临时文件，应清理 | -1分 |
| CONTRIBUTING.md | 开发指南，不应出现 | -1分 |
| LICENSE | 许可证，不应出现 | -1分 |
| HISTORY.md | 历史记录，不应出现 | -1分 |
| SUPPORT.md | 支持信息，不应出现 | -1分 |

---

## 正确做法

- 所有说明放在 SKILL.md 中
- 如需详细文档，放 references/
- 删除所有开发记录文件

---

## 检查命令

```bash
# 检查是否存在禁止文件
ls -la | grep -E "README|CHANGELOG|TODO|CONTRIBUTING|LICENSE"
```
