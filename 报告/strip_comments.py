# -*- coding: utf-8 -*-
"""去掉 C 源文件中的注释，保留 CubeMX 的 USER CODE 标记行。"""
import re
import sys

BEGIN = "/* USER CODE BEGIN"
END = "/* USER CODE END"


def strip_comments(src: str) -> str:
    # 先把 USER CODE 标记替换成占位符，避免被当成注释删掉
    holders = {}

    def hold(m):
        key = "@@UC%d@@" % len(holders)
        holders[key] = m.group(0)
        return key

    src = re.sub(r"/\* USER CODE (?:BEGIN|END)[^*]*\*/", hold, src)

    out = []
    i, n = 0, len(src)
    in_str = None
    in_line = False
    in_block = False
    while i < n:
        c = src[i]
        if in_line:
            if c == "\n":
                in_line = False
                out.append("\n")
            i += 1
            continue
        if in_block:
            if c == "*" and i + 1 < n and src[i + 1] == "/":
                in_block = False
                i += 2
                continue
            if c == "\n":
                out.append("\n")
            i += 1
            continue
        if in_str:
            out.append(c)
            if c == "\\" and i + 1 < n:
                out.append(src[i + 1])
                i += 2
                continue
            if c == in_str:
                in_str = None
            i += 1
            continue
        if c in "\"'":
            in_str = c
            out.append(c)
            i += 1
            continue
        if c == "/" and i + 1 < n and src[i + 1] == "/":
            in_line = True
            i += 2
            continue
        if c == "/" and i + 1 < n and src[i + 1] == "*":
            in_block = True
            i += 2
            continue
        out.append(c)
        i += 1

    text = "".join(out)

    # 恢复标记
    for key, val in holders.items():
        text = text.replace(key, val)

    # 去行尾空格、压缩连续空行
    lines = [ln.rstrip() for ln in text.split("\n")]
    cleaned = []
    blank = 0
    for ln in lines:
        if ln.strip() == "":
            blank += 1
            if blank > 1:
                continue
            cleaned.append("")
        else:
            blank = 0
            cleaned.append(ln)
    while cleaned and cleaned[0] == "":
        cleaned.pop(0)
    while cleaned and cleaned[-1] == "":
        cleaned.pop()
    return "\n".join(cleaned) + "\n"


if __name__ == "__main__":
    path = sys.argv[1]
    with open(path, "r", encoding="utf-8-sig") as f:
        src = f.read()
    result = strip_comments(src)
    with open(path, "w", encoding="utf-8-sig", newline="\n") as f:
        f.write(result)
    print("stripped:", path, "lines:", result.count("\n"))
