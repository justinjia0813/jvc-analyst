# 输出风险画像

- **Overflow**：宽表、长链接、图片和不可断行文本可能横向溢出，密集段落可能跨页失去上下文。构建报告必须提示宽表和分页风险；逐页视觉检查负责最终判定。
- **Missing/local assets**：图片、logo 和字体必须存在、可读且位于允许的本地边界内；远程资源或路径越界是 hard error。缺少必需资源时停止构建。
- **Citation drift**：正文 `[S<n>]` 与来源索引可能失配。未定义或重复 ID 是 hard error；未被引用的索引条目是 warning，不自动增删引用。
- **Font substitution**：指定字体不可用、替代字体字宽变化或缺字可能改变分页。无效字体是 hard error；可渲染的字体替代必须记录 warning，并检查中文、英文、数字和符号。
- **Rollback**：`report.pdf`、`report.html`、`build-report.txt` 作为一个成功产物集发布；任一校验或渲染失败都保留上一版完整产物，不发布部分结果。
- **Mandatory visual inspection**：构建成功后必须渲染并检查全部 PDF（Portable Document Format，可移植文档格式，用于固定版式）页面，确认无裁切、横向溢出、缺字、caption 脱离、意外空白页或页眉页脚不一致；未完成检查不得交付。
