# Third-party References

这个目录专门用于存放第三方工具的引用说明，避免和本地脚本混在一起。

## 目录说明

### `atian25-yuque-exporter/`

- 上游项目：`atian25/yuque-exporter`
- 用途：当前工具包的底层导出能力来源
- 当前保留内容：
  - `LICENSE`
  - `UPSTREAM_README.md`
  - `patches/local-adaptations.patch`

说明：

- 当前工具包运行时仍通过 `npx` 拉起上游包
- 这里保留的是“来源说明 + 本地补丁记录”
- 这样更适合单独整理后开源

### `yuque-yuque-mcp-server/`

- 上游项目：`yuque/yuque-mcp-server`
- 用途：参考性工具说明
- 当前不作为这套批量导出的主执行链路
