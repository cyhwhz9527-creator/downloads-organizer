# Downloads Organizer 📁

一个简单又实用的小工具：一条命令，自动把杂乱的「下载」文件夹整理得井井有条。

下载文件夹用着用着就堆满了图片、PDF、压缩包、安装包……这个工具会按文件类型，把它们分门别类地放进对应子文件夹里。支持先预览再执行，还能一键撤销，安全又省心。

## ✨ 功能特点

- **按类型自动分类**：图片、文档、视频、音频、压缩包、程序代码、安装包，其余归入「其他」
- **预览模式（`--dry-run`）**：先看会怎么整理，确认无误再真正动文件
- **一键撤销（`--undo`）**：整理后不满意？一条命令全部还原
- **不会覆盖文件**：遇到重名自动改成 `文件 (1).jpg`，绝不丢东西
- **跨平台**：Windows、macOS、Linux 都能用
- **可自定义规则**：用一个 JSON 文件就能改分类方式
- **零依赖**：只用 Python 自带库，装好 Python 即可运行

## 🚀 快速开始

### 1. 准备环境

确认电脑装了 Python 3.7 或更高版本：

```bash
python --version
```

如果没有，去 [python.org](https://www.python.org/downloads/) 下载安装即可。

### 2. 下载本工具

```bash
git clone https://github.com/你的用户名/downloads-organizer.git
cd downloads-organizer
```

### 3. 使用

**第一步，先预览（强烈建议）—— 不会真正移动任何文件：**

```bash
python organizer.py ~/Downloads --dry-run
```

**确认效果满意后，真正整理：**

```bash
python organizer.py ~/Downloads
```

**如果想还原，撤销上一次整理：**

```bash
python organizer.py ~/Downloads --undo
```

> Windows 用户把 `~/Downloads` 换成你的下载文件夹路径，例如
> `C:\Users\你的用户名\Downloads`

### 4. （可选）安装成命令，随处可用

如果你想直接用 `organize-downloads` 命令、不用每次都写 `python organizer.py`，可以一键安装：

```bash
pip install git+https://github.com/cyhwhz9527-creator/downloads-organizer.git
```

之后在任意目录都能直接运行：

```bash
organize-downloads ~/Downloads --dry-run
organize-downloads ~/Downloads
organize-downloads ~/Downloads --undo
```

## ⚙️ 自定义分类规则

新建一个 `my_rules.json`，按 `"分类名": ["扩展名", ...]` 的格式写：

```json
{
  "图片": [".jpg", ".png", ".gif"],
  "工作文档": [".pdf", ".docx", ".xlsx"],
  "我的安装包": [".dmg", ".exe", ".apk"]
}
```

然后运行时加上 `--config`：

```bash
python organizer.py ~/Downloads --config my_rules.json
```

## 📂 整理效果示例

整理前：

```
Downloads/
├── 报告.pdf
├── 猫咪.jpg
├── 风景.png
├── 安装包.dmg
└── 电影.mp4
```

整理后：

```
Downloads/
├── 图片/
│   ├── 猫咪.jpg
│   └── 风景.png
├── 文档/
│   └── 报告.pdf
├── 视频/
│   └── 电影.mp4
└── 安装包/
    └── 安装包.dmg
```

## 🤝 参与贡献

欢迎提 Issue 和 Pull Request！想加新的文件类型、新功能，或发现 bug，都可以在
[Issues](https://github.com/你的用户名/downloads-organizer/issues) 里告诉我。
详见 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 📄 开源协议

本项目基于 [MIT License](LICENSE) 开源，可自由使用、修改和分发。
