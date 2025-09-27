import os
import re

# 要扫描的目录，比如 _posts
SCAN_DIR = "_posts"

# 需要标记的问题字符
BAD_CHARS = ["：", " ", "　"]  # 中文冒号、半角空格、全角空格

def check_markdown(file_path):
    issues = []
    with open(file_path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            # 检查 markdown 链接/图片
            for match in re.findall(r'!?\[.*?\]\((.*?)\)', line):
                path = match.strip()
                if not path:
                    issues.append((i, "空链接/图片", line.strip()))
                else:
                    # 绝对路径才检查文件是否存在
                    if path.startswith("/"):
                        abs_path = os.path.join(os.getcwd(), path.lstrip("/"))
                        if not os.path.exists(abs_path):
                            issues.append((i, f"路径不存在: {path}", line.strip()))
                    # 检查文件名里是否有坏字符
                    for bad in BAD_CHARS:
                        if bad in path:
                            issues.append((i, f"文件名包含不安全字符 '{bad}': {path}", line.strip()))

            # 检查 Liquid 错误标签
            if re.search(r"{%\s*\d{4}", line):
                issues.append((i, "疑似错误 Liquid 标签，改为 {% post_url ... %}", line.strip()))

            # 检查 HTML 空链接
            if re.search(r'<a\s+href=[\'"]\s*[\'"]', line):
                issues.append((i, "HTML 空链接", line.strip()))

    return issues


def main():
    all_issues = {}
    for root, _, files in os.walk(SCAN_DIR):
        for file in files:
            if file.endswith(".md"):
                path = os.path.join(root, file)
                issues = check_markdown(path)
                if issues:
                    all_issues[path] = issues

    if not all_issues:
        print("✅ 没有发现明显问题")
    else:
        print("⚠️ 发现以下问题：\n")
        for file, issues in all_issues.items():
            print(f"📄 文件: {file}")
            for line_num, issue, content in issues:
                print(f"  - 第 {line_num} 行: {issue}")
                print(f"    内容: {content}")
            print()

if __name__ == "__main__":
    main()
