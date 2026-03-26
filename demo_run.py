# demo_run.py
"""
一键演示脚本：广告素材生成 & 广告创建 & 数据监控
"""

from content_engines.content_remix.auto_edit import auto_edit_clip
from content_engines.aigc_engine.script_gen import generate_script
from ads_ops.ad_builder import create_ad, monitor_ad

def run_demo():
    print("=== AdOps-Automation Demo Run ===\n")

    # Step 1: 内容重组
    sample_clip = "sample_live_clip.mp4"
    edited_clip = auto_edit_clip(sample_clip)
    print(f"[Demo] Edited clip: {edited_clip}\n")

    # Step 2: AI文案生成
    hook = "快来直播吧"
    sell_point = "娱乐与社交的乐趣"
    script = generate_script(hook, sell_point)
    print(f"[Demo] Generated script: {script}\n")

    # Step 3: 广告创建
    ad_id = create_ad(script, edited_clip)
    print(f"[Demo] Created ad ID: {ad_id}\n")

    # Step 4: 广告监控
    monitor_ad(ad_id)
    print("\n=== Demo Complete ===")

if __name__ == "__main__":
    run_demo()