# content_engines/aigc_engine/script_gen.py

def generate_script(hook, sell_point):
    """
    模拟 AI 生成广告文案脚本
    """
    script = f"{hook} — 让用户体验 {sell_point}！"
    print(f"[AIGC Engine] Generated script: {script}")
    return script

if __name__ == "__main__":
    hook = "快来直播吧"
    sell_point = "娱乐与社交的乐趣"
    script = generate_script(hook, sell_point)