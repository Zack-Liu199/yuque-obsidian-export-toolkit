# Yuque Obsidian Export Toolkit

一套面向 **语雀 → Obsidian** 的导出工具包。

这个目录专门为后续单独提交到 GitHub 做了整理，目标是：

- 把当前项目里已经验证可用的方法单独收敛出来
- 把“自研脚本”和“引用的第三方工具”分开摆放
- 让后续维护、开源说明、License 标注更清晰

## 1. 目录结构

```text
yuque-obsidian-export-toolkit/
├── README.md
├── requirements.txt
├── .gitignore
├── scripts/
│   ├── export_yuque_vault.py
│   ├── fix_yuque_obsidian_links.py
│   ├── normalize_exported_markdown.py
│   └── export_lakesheet_xlsx.py
└── third_party/
    ├── README.md
    ├── atian25-yuque-exporter/
    │   ├── LICENSE
    │   ├── UPSTREAM_README.md
    │   └── patches/
    │       └── local-adaptations.patch
    └── yuque-yuque-mcp-server/
        └── REFERENCE.md
```

## 2. 依赖

- Python 3.10+
- Node.js 18+
- `npx`
- Python 包：`openpyxl`

安装：

```bash
pip install -r requirements.txt
```

## 3. 脚本说明

### `scripts/export_yuque_vault.py`

主入口脚本，负责：

1. 使用本机 `npx` 缓存拉起 `yuque-exporter`
2. 自动给缓存中的导出器打补丁
3. 支持一次导出一个或多个语雀知识库
4. 展平导出目录
5. 修复 Obsidian 内部链接

### `scripts/fix_yuque_obsidian_links.py`

把 Markdown 中能映射到本地文档的语雀链接改为相对 `.md` 路径。

已支持：

- 单知识库导出
- 多知识库合并到同一个 vault 后的链接修复

### `scripts/normalize_exported_markdown.py`

清洗导出的 Markdown，重点处理：

- 表格单元格中的换行
- 删除线等误转义
- 一些 Obsidian 中渲染不自然的 Markdown 细节

### `scripts/export_lakesheet_xlsx.py`

把语雀 `lakesheet` 类型文档导出为 `.xlsx`，并把原 `.md` 重写为说明页。

适用于：

- 电子表格类文档
- 不适合直接保留为 Markdown 的内容

## 4. 标准流程

### 4.1 导出 Markdown

```bash
export YUQUE_TOKEN='你的语雀 Token'

python3 ./scripts/export_yuque_vault.py \
  shiwozack/root \
  ./exported-vaults/个人语雀花园
```

如果多个知识库要合并到一个 Obsidian 仓库：

```bash
python3 ./scripts/export_yuque_vault.py \
  shiwozack/secret \
  shiwozack/findjob \
  ./exported-vaults/个人问答与求职
```

### 4.2 清洗 Markdown

```bash
python3 ./scripts/normalize_exported_markdown.py \
  ./exported-vaults/个人问答与求职
```

### 4.3 导出 lakesheet

先定位包含 `lakesheet` 的 `.meta` 目录：

```bash
rg -l '"format"\s*:\s*"lakesheet"' ./exported-vaults/个人问答与求职/.meta \
  | sed 's#/docs/.*##' \
  | sort -u
```

再逐个导出：

```bash
python3 ./scripts/export_lakesheet_xlsx.py \
  ./exported-vaults/个人问答与求职/.meta/<user>/<repo>/docs \
  --output-dir ./exported-vaults/个人问答与求职/_lakesheet_xlsx_dedup
```

## 5. 当前这套方法相对上游的本地增强

相对 `atian25/yuque-exporter`，当前工具包额外处理了这些问题：

- `outputDir` 实际生效问题
- `/docs` 列表分页问题
- 多 namespace 合并导出到同一个 vault
- Obsidian 内部链接修复
- Markdown 表格清洗
- `lakesheet` 单独转 `.xlsx`
- 外链图片/资源下载失败时不中断整个导出
- `body` / `body_draft` 双通道解析 lakesheet 数据

对应第三方补丁可见：

- `third_party/atian25-yuque-exporter/patches/local-adaptations.patch`

## 6. 第三方工具说明

本目录已把第三方引用单独放到 `third_party/`：

- `atian25/yuque-exporter`
  - 这是 Markdown 批量导出的底层依赖
  - 本仓库不直接内嵌其完整源码作为运行时依赖
  - 仅保留上游 `README`、`LICENSE` 和本地补丁 diff 作为说明材料

- `yuque/yuque-mcp-server`
  - 作为参考工具记录
  - 本项目当前不依赖它执行批量导出

## 7. 开源建议

如果你后续把这个目录单独提交到 GitHub，建议：

- 仓库只提交这个目录内容
- 不提交你的 `exported-vaults/`
- 不提交真实 `YUQUE_TOKEN`
- 如果 Token 曾经暴露过，先去语雀后台轮换

## 8. License 与归属

- `scripts/` 下是当前项目整理出的本地脚本
- `third_party/` 下保留的是第三方来源说明、License 和补丁记录
- 提交到 GitHub 前，建议再补一版你自己的仓库 License
