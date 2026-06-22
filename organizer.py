#!/usr/bin/env python3
"""
Downloads Organizer —— 自动整理下载文件夹的小工具

按文件类型把杂乱的文件夹整理进分类子文件夹（图片 / 文档 / 视频 / 音频 / 压缩包 / 程序 / 安装包 / 其他）。
支持预览（不真正移动）、撤销上一次整理、自动处理重名文件、跨平台运行。

用法示例：
    python organizer.py ~/Downloads --dry-run    # 先预览，不动文件
    python organizer.py ~/Downloads              # 真正整理
    python organizer.py ~/Downloads --undo       # 撤销上一次整理

作者：陈宇航 · MIT License
"""

import argparse
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# 默认分类规则：扩展名 -> 分类文件夹名
# 你可以用 --config 指定自己的 JSON 规则来覆盖这里
# ---------------------------------------------------------------------------
DEFAULT_RULES = {
    "图片": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg", ".heic", ".tiff"],
    "文档": [".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
             ".txt", ".md", ".csv", ".rtf", ".odt", ".epub"],
    "视频": [".mp4", ".mov", ".avi", ".mkv", ".flv", ".wmv", ".webm", ".m4v"],
    "音频": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a", ".wma"],
    "压缩包": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz"],
    "程序与代码": [".py", ".js", ".ts", ".html", ".css", ".json", ".java",
                ".c", ".cpp", ".go", ".rs", ".sh"],
    "安装包": [".dmg", ".pkg", ".exe", ".msi", ".deb", ".apk", ".appimage"],
}

# 记录每次整理的操作日志，撤销时用。存放在被整理文件夹内。
LOG_NAME = ".organizer_log.json"


def build_extension_map(rules):
    """把 {分类: [扩展名...]} 反转成 {扩展名: 分类}，方便查找。"""
    ext_map = {}
    for category, exts in rules.items():
        for ext in exts:
            ext_map[ext.lower()] = category
    return ext_map


def category_for(file_path, ext_map):
    """根据扩展名返回分类，找不到归到“其他”。"""
    return ext_map.get(file_path.suffix.lower(), "其他")


def unique_destination(dest):
    """如果目标已存在同名文件，自动加 (1)、(2)… 避免覆盖。"""
    if not dest.exists():
        return dest
    stem, suffix, parent = dest.stem, dest.suffix, dest.parent
    counter = 1
    while True:
        candidate = parent / f"{stem} ({counter}){suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


def collect_files(folder, ext_map):
    """收集待整理的文件，跳过子文件夹、隐藏文件和日志/脚本自身。"""
    plans = []
    self_name = Path(__file__).name
    for item in folder.iterdir():
        if item.is_dir():
            continue
        if item.name.startswith("."):
            continue
        if item.name in (LOG_NAME, self_name):
            continue
        category = category_for(item, ext_map)
        dest = folder / category / item.name
        plans.append((item, dest, category))
    return plans


def organize(folder, ext_map, dry_run=False):
    """执行整理。返回本次移动的 (源, 目标) 列表。"""
    plans = collect_files(folder, ext_map)
    if not plans:
        print("文件夹里没有需要整理的文件。")
        return []

    moves = []
    for src, dest, category in plans:
        final_dest = unique_destination(dest)
        if dry_run:
            print(f"[预览] {src.name}  ->  {category}/{final_dest.name}")
        else:
            final_dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(final_dest))
            print(f"已移动 {src.name}  ->  {category}/{final_dest.name}")
            moves.append((str(final_dest), str(src)))

    if dry_run:
        print(f"\n预览完成：共 {len(plans)} 个文件可整理。去掉 --dry-run 即可真正执行。")
    else:
        _write_log(folder, moves)
        print(f"\n整理完成：共移动 {len(moves)} 个文件。如需还原，运行  --undo")
    return moves


def _write_log(folder, moves):
    log = {"time": datetime.now().isoformat(timespec="seconds"), "moves": moves}
    (folder / LOG_NAME).write_text(json.dumps(log, ensure_ascii=False, indent=2),
                                   encoding="utf-8")


def undo(folder):
    """根据日志把上一次整理的文件移回原位。"""
    log_path = folder / LOG_NAME
    if not log_path.exists():
        print("没有找到整理记录，无法撤销。")
        return
    log = json.loads(log_path.read_text(encoding="utf-8"))
    restored = 0
    for current, original in log.get("moves", []):
        current_path, original_path = Path(current), Path(original)
        if current_path.exists():
            original_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(current_path), str(unique_destination(original_path)))
            restored += 1
    log_path.unlink(missing_ok=True)
    # 清理整理时产生的空分类文件夹
    for sub in folder.iterdir():
        if sub.is_dir():
            try:
                sub.rmdir()
            except OSError:
                pass  # 非空就保留
    print(f"已撤销：还原了 {restored} 个文件。")


def load_rules(config_path):
    if not config_path:
        return DEFAULT_RULES
    path = Path(config_path).expanduser()
    if not path.exists():
        print(f"找不到配置文件：{path}，将使用默认规则。")
        return DEFAULT_RULES
    return json.loads(path.read_text(encoding="utf-8"))


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="自动整理下载文件夹：按类型把文件归类到子文件夹。")
    parser.add_argument("folder", help="要整理的文件夹路径，例如 ~/Downloads")
    parser.add_argument("--dry-run", action="store_true",
                        help="只预览，不真正移动文件（建议第一次先用）")
    parser.add_argument("--undo", action="store_true",
                        help="撤销上一次整理，把文件还原回原位")
    parser.add_argument("--config", help="自定义分类规则的 JSON 文件路径")
    args = parser.parse_args(argv)

    folder = Path(args.folder).expanduser().resolve()
    if not folder.is_dir():
        print(f"错误：{folder} 不是一个有效的文件夹。")
        sys.exit(1)

    if args.undo:
        undo(folder)
        return

    ext_map = build_extension_map(load_rules(args.config))
    organize(folder, ext_map, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
