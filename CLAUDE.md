# molcrafts-zensical-theme — Project Context

MolCrafts 文档站共享 Zensical theme 扩展（Jinja + 静态 CSS/JS）。发布物是 **Python wheel**（`pip install molcrafts-zensical-theme`），**无 React、无 npm 运行时依赖**。

产品 docs 建站走 **Cloudflare Pages**；本包装进 wheel 后由各产品 `pip install` 消费。

## Stack

- Python ≥3.12 / setuptools
- Zensical（extends `zensical` modern variant）
- 静态 CSS（`tokens.css` + `molcrafts.css`）+ 少量 JS（mathjax 配置等）
- 可选：`mkdocstrings` C++ handler（同包）
- 测试：pytest / tox（stdlib，不引入前端构建）

## 目录约定

```
src/molcrafts_zensical_theme/
  templates/                 mkdocs theme 根（Zensical 会拷非代码资源进 site）
    assets/stylesheets/
      tokens.css             共享品牌锚点（与 index brand-tokens.css 必须完全一致）
      molcrafts.css          表面样式；@import tokens.css
    assets/javascripts/
    main.html
    mkdocs_theme.yml
    partials/
  formatters.py
src/mkdocstrings_handlers/cpp/
tests/
  test_tokens_contract.py    锚点完整性 + 与 index 字节对齐（若 monorepo 同级存在）
```

## 品牌 tokens（与 molcrafts-index 手动对齐）

**禁止** 给 theme 加 npm/build 依赖来同步 tokens。

| 本仓 | 对齐仓 |
|------|--------|
| `src/molcrafts_zensical_theme/templates/assets/stylesheets/tokens.css` | `molcrafts-index/src/styles/brand-tokens.css` |

改色流程：编辑其中一个 → **整文件复制**到另一个。

`tokens.css` 含：

- Hex：`--molcrafts-forest` / cream / sand / slate / radius / shadows …
- HSL channels：`--molcrafts-*-hsl`（给 index shadcn 用）

产品色 **不进** tokens；各站 `zensical.toml`：

```toml
[project.extra.molcrafts]
product = "molpy"
accent = "#0284c7"
accent_soft = "rgba(2, 132, 199, 0.14)"
```

锚点速查：

| Token | Hex |
|-------|-----|
| forest | `#18432b` |
| forest-light | `#2a6744` |
| forest-dark | `#0e2b1b` |
| cream | `#fbf6e4` |
| sand | `#f2da9d` |
| sand-strong | `#c8841d` |
| slate | `#101811` |
| radius | `0.4rem` |

Cyan（`--molcrafts-cyan-spark`）仅 display，非 interactive primary。

消费：

| 侧 | 方式 |
|----|------|
| Theme | `molcrafts.css` → `@import url("tokens.css")` → 打进 wheel |
| Index | `@import "./brand-tokens.css"` → `tailwind.css` 映射 UI 变量 |

漂移检查：

```bash
uv run --extra dev tox -e py
# test_tokens_contract：必有锚点；若存在 ../molcrafts-index/.../brand-tokens.css 则字节相等
```

## 强约定

1. **Theme 保持 Jinja + 静态资源**；不要引入 React / shadcn 运行时。
2. **tokens 只维护 `tokens.css`**，不要在 `molcrafts.css` 里再复制一份 hex 锚点。
3. **版本**：`pyproject.toml` version；发版打 `v*` tag 触发 PyPI workflow。
4. **消费方**只需 `[project.theme] name = "molcrafts"`；features/palette 由 theme 默认提供。
5. Web Component fence（MolVis/MolPlot）模型见 README；运行时仍走 CDN elements，不进 Python 依赖。

## 测试 / 发布

```bash
uv run --extra dev tox -e py          # 本地 CI 等价
python -m build && twine check dist/* # 发版前
# 合入主仓后：git tag v0.x.y && git push upstream v0.x.y
```
