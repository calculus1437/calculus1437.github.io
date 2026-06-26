import os
import re
import shutil
from pathlib import Path

POSTS_DIR = Path("posts")
BACKUP_DIR = Path("posts_backup")

# ================= 配置 =================
# 检测 HEAD 中是否已包含以下内容，如果缺失则添加（注意保持缩进风格）
NEW_HEAD_CONTENT_LINES = [
    '<link href="../assets/fonts/NotoSerifSC-VF/result.css" rel="stylesheet">',
    '<link rel="stylesheet" href="../assets/css/style.css">',
    # 删掉 KaTeX CSS，因为 MPE 自己会加
    '<link href="../assets/css/toc.css"  rel=stylesheet>',
    '<script src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>',
    '<script src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js"></script>',
    '<script src="../assets/js/lazy.js" defer></script>',
    '<script src="../assets/js/toc.js" defer></script>',
    '<link rel="icon" type="image/jpg" href="../assets/images/avatar.jpg">'
]


# 脚注 HTML（注意缩进）
FOOTER_HTML = '''    <footer>
        Copyright 2026 HuangTianye 版权所有
    </footer>'''
# =======================================


def has_target_content(content, target):
    """检查内容中是否已存在目标字符串（去除多余空白差异）"""
    return target in content


def replace_font_family(content):
    # 检查时允许可选双引号
    if re.search(
        r'\.markdown-preview\.markdown-preview\s*\{[^}]*font-family:\s*"?Noto Serif SC"?\s*;[^}]*font-weight:\s*500',
        content
    ):
        return content, False

    pattern = r'(\.markdown-preview\.markdown-preview\s*\{[^}]*?font-family:\s*)(?:"[^"]*"|[^;]+)(;)'
    def replacer(match):
        return match.group(1) + '"Noto Serif SC";\n  font-weight: 500' + match.group(2)

    new_content = re.sub(pattern, replacer, content, flags=re.DOTALL)
    return new_content, (new_content != content)


def replace_head_links(content):
    """
    检查 <head> 部分，确保 NEW_HEAD_CONTENT_LINES 中的每一行都存在。
    如果缺失，则在 </head> 之前插入缺失的行（保持原有缩进风格）。
    返回修改后的内容和是否有修改。
    """
    # 找到 <head> 和 </head> 的位置
    head_start = re.search(r'<head>', content, re.IGNORECASE)
    head_end = re.search(r'</head>', content, re.IGNORECASE)
    if not head_start or not head_end:
        return content, False

    head_content = content[head_start.end():head_end.start()]
    # 提取 head 中已有的所有行（去除空白行）
    existing_lines = [line.strip() for line in head_content.splitlines() if line.strip()]

    lines_to_add = []
    for required_line in NEW_HEAD_CONTENT_LINES:
        # 检查该行是否已存在（简单字符串匹配，忽略前导空格差异）
        found = False
        for existing in existing_lines:
            if required_line.strip() == existing.strip():
                found = True
                break
        if not found:
            lines_to_add.append(required_line)

    if not lines_to_add:
        return content, False

    # 将缺失的行插入到 </head> 之前，保持适当的缩进（原 head 内容的前导空格风格）
    # 简单方法：取原 head 内第一行的前导空格作为缩进参考，或者统一用 4 个空格
    # 这里使用 4 个空格作为缩进前缀
    indent = '    '
    insertion = '\n' + '\n'.join([indent + line for line in lines_to_add]) + '\n'
    new_content = content[:head_end.start()] + insertion + content[head_end.start():]
    return new_content, True



def add_footer(content):
    # 要替换成的完整结尾（注意保留换行和缩进）
    new_ending = '''    <footer>
        Copyright 2026 HuangTianye 版权所有
    </footer>

</body>
</html>'''
    # 如果已经包含脚注内容，则跳过
    if 'Copyright 2026 HuangTianye' in content:
        return content, False
    # 匹配从最后一个 </body> 到文件末尾之间的所有内容（包括空白）
    # 使用 (?s) 让 . 匹配换行符
    pattern = r'(?s)(.*?)</body>\s*</html>\s*$'
    match = re.match(pattern, content)
    if match:
        # 保留 </body> 之前的所有内容
        before_body = match.group(1)
        new_content = before_body + new_ending
        return new_content, True
    return content, False


def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    modified = False

    # 字体替换
    content, changed = replace_font_family(content)
    if changed:
        modified = True

    # 头部链接替换
    content, changed = replace_head_links(content)
    if changed:
        modified = True

    # 脚注添加
    content, changed = add_footer(content)
    if changed:
        modified = True

    if modified:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ 已更新: {filepath}")
    else:
        print(f"⏭️ 无需修改: {filepath}")


def main():
    # 创建备份
    if BACKUP_DIR.exists():
        print(f"⚠️ 备份目录 {BACKUP_DIR} 已存在，跳过备份。")
    else:
        shutil.copytree(POSTS_DIR, BACKUP_DIR)
        print(f"📁 已备份原文件到 {BACKUP_DIR}")

    html_files = list(POSTS_DIR.glob("*.html"))
    if not html_files:
        print("❌ 没有找到任何 .html 文件，请检查 posts 目录路径。")
        return

    for html_file in html_files:
        process_file(html_file)

    print("🎉 批量处理完成！")


if __name__ == "__main__":
    main()