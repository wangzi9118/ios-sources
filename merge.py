#!/usr/bin/env python3
"""把 DouDuo 官方源和 Erosion-CN 官方源合并成一个 AltStore / SideStore / Feather / ESign 通用软件源。

用法：
    python3 merge.py [输出路径，默认 apps.json]

默认从上游 raw 链接实时拉取；可用环境变量覆盖：
    DOUDUO_URL / EROSION_URL / SOURCE_URL（合并后源自身的 raw 链接）
"""
import json
import os
import sys
import urllib.request

DOUDUO_URL = os.environ.get(
    "DOUDUO_URL",
    "https://raw.githubusercontent.com/81199000/DouDuo/main/docs/source/douduo-github.json",
)
EROSION_URL = os.environ.get(
    "EROSION_URL",
    "https://raw.githubusercontent.com/Kianuni/Erosion-CN/main/apps.json",
)
# 合并后源自身的 raw 链接（传到你自己的 GitHub 后改成真实地址，
# 或由 GitHub Action 自动填，见 .github/workflows/merge-sources.yml）
SOURCE_URL = os.environ.get(
    "SOURCE_URL",
    "https://raw.githubusercontent.com/<你的GitHub用户名>/<仓库名>/main/apps.json",
)


def fetch(url):
    with urllib.request.urlopen(url, timeout=30) as r:
        return json.load(r)


def main():
    out_path = sys.argv[1] if len(sys.argv) > 1 else "apps.json"
    douduo = fetch(DOUDUO_URL)
    erosion = fetch(EROSION_URL)

    # 按 (bundleIdentifier, version) 去重；同包名保留两边各自的版本条目
    seen = set()
    apps = []
    for app in erosion.get("apps", []) + douduo.get("apps", []):
        key = (app.get("bundleIdentifier"), app.get("version"))
        if key in seen:
            continue
        seen.add(key)
        # AltStore / SideStore 要求 size 为数字，DouDuo 源里是字符串，统一转 int
        if isinstance(app.get("size"), str) and app["size"].isdigit():
            app["size"] = int(app["size"])
        apps.append(app)

    news = erosion.get("news", []) + douduo.get("news", [])

    merged = {
        "name": "DouDuo + Erosion-CN 合并源",
        "identifier": "com.merged.douduo-erosion.source",
        "subtitle": "DouDuo 与 Erosion-CN 合并软件源（AltStore / SideStore / Feather / ESign）",
        "description": "合并自 DouDuo 官方源与 Erosion-CN 官方源。DouDuo：开源第三方抖音客户端（未签名，需自签）；Erosion-CN：iOS 系统配置与 MobileGestalt 研究工具箱（安装时保留 App Group 权限）。安装包均来自上游官方仓库发行版。",
        "iconURL": "https://raw.githubusercontent.com/Kianuni/Erosion-CN/main/PreviewIcon.png",
        "website": "https://github.com/Kianuni/Erosion-CN",
        "tintColor": "#CF7D46",
        "sourceURL": SOURCE_URL,
        "featuredApps": erosion.get("featuredApps", []),
        "apps": apps,
        "news": news,
    }

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)
        f.write("\n")

    print(f"merged {len(apps)} app entries from 2 sources -> {out_path}")
    for app in apps:
        print(f"  - {app.get('name')} {app.get('version')} ({app.get('bundleIdentifier')})")


if __name__ == "__main__":
    main()
