      
import os
import csv
import subprocess
from pathlib import Path

# =========================
# 配置区
# =========================

BASE_DIR = r"F:\FFmpeg"

DIR_A = os.path.join(BASE_DIR, "A")
DIR_A_STD = os.path.join(BASE_DIR, "A_std")

DIR_B = os.path.join(BASE_DIR, "B")
DIR_B_CUT = os.path.join(BASE_DIR, "B_cut")

DIR_C = os.path.join(BASE_DIR, "C")
DIR_C_CUT = os.path.join(BASE_DIR, "C_cut")

DIR_MUSIC = os.path.join(BASE_DIR, "music")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

MAPPING_CSV = os.path.join(BASE_DIR, "mapping_hook_test_bgm.csv")

# 命名规则
DATE_STR = "260306"
NAME_PREFIX = f"{DATE_STR}-inhouse-video"
NAME_SUFFIX = "-remix-9x16.mp4"

# B / C 裁剪秒数
TRIM_SECONDS = 5

# 输出规格
TARGET_W = 1080
TARGET_H = 1920
TARGET_FPS = 30
TARGET_AR = 44100
TARGET_AC = 2

# BGM 音量
BGM_VOLUME = 0.25

# 是否覆盖已存在文件
OVERWRITE = True

# 是否清空旧输出
CLEAR_OLD_OUTPUT = False

# 支持格式
VIDEO_EXTS = {".mp4", ".mov", ".mkv", ".avi", ".m4v"}
AUDIO_EXTS = {".mp3", ".wav", ".m4a", ".aac"}

# FFmpeg 路径
FFMPEG = r"E:\软件\ffmpeg\bin\ffmpeg.exe"
FFPROBE = r"E:\软件\ffmpeg\bin\ffprobe.exe"


# =========================
# 工具函数
# =========================

def ensure_dirs():
    for folder in [DIR_A, DIR_A_STD, DIR_B, DIR_B_CUT, DIR_C, DIR_C_CUT, DIR_MUSIC, OUTPUT_DIR]:
        os.makedirs(folder, exist_ok=True)


def is_video_file(filename: str) -> bool:
    return Path(filename).suffix.lower() in VIDEO_EXTS


def is_audio_file(filename: str) -> bool:
    return Path(filename).suffix.lower() in AUDIO_EXTS


def list_video_files(folder: str):
    files = [f for f in os.listdir(folder) if is_video_file(f)]
    files.sort()
    return files


def list_audio_files(folder: str):
    files = [f for f in os.listdir(folder) if is_audio_file(f)]
    files.sort()
    return files


def run_cmd(cmd):
    print("执行命令：", " ".join(f'"{c}"' if " " in str(c) else str(c) for c in cmd))
    subprocess.run(cmd, check=True)


def get_media_duration(input_path: str) -> float:
    cmd = [
        FFPROBE,
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        input_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    try:
        return float(result.stdout.strip())
    except ValueError:
        return 0.0


def build_video_filter():
    return (
        f"scale={TARGET_W}:{TARGET_H}:force_original_aspect_ratio=decrease,"
        f"pad={TARGET_W}:{TARGET_H}:(ow-iw)/2:(oh-ih)/2,"
        f"fps={TARGET_FPS},format=yuv420p,setsar=1"
    )


def clear_folder(folder: str, exts: set):
    if not os.path.exists(folder):
        return
    for f in os.listdir(folder):
        path = os.path.join(folder, f)
        if os.path.isfile(path) and Path(f).suffix.lower() in exts:
            try:
                os.remove(path)
            except OSError:
                pass


def auto_pick_first_audio(folder: str) -> str:
    files = [f for f in os.listdir(folder) if is_audio_file(f)]
    files.sort()
    if not files:
        raise FileNotFoundError(f"music 文件夹为空：{folder}")
    picked = files[0]
    print(f"自动选择 BGM：{picked}")
    return picked


def standardize_video(input_path: str, output_path: str) -> bool:
    """
    标准化整条视频（A 用）
    去掉原音轨，最终统一上 BGM
    """
    duration = get_media_duration(input_path)
    if duration <= 0:
        print(f"跳过无效视频：{input_path}")
        return False

    cmd = [
        FFMPEG,
        "-y" if OVERWRITE else "-n",
        "-i", input_path,
        "-vf", build_video_filter(),
        "-an",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "18",
        "-movflags", "+faststart",
        output_path
    ]
    run_cmd(cmd)
    return True


def trim_and_standardize_video(input_path: str, output_path: str, trim_seconds: int = 5) -> bool:
    """
    裁前 N 秒并标准化（B / C 用）
    去掉原音轨，最终统一上 BGM
    """
    duration = get_media_duration(input_path)
    if duration <= 0:
        print(f"跳过无效视频：{input_path}")
        return False

    actual_trim = min(trim_seconds, duration)

    cmd = [
        FFMPEG,
        "-y" if OVERWRITE else "-n",
        "-i", input_path,
        "-t", str(actual_trim),
        "-vf", build_video_filter(),
        "-an",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "18",
        "-movflags", "+faststart",
        output_path
    ]
    run_cmd(cmd)
    return True


def standardize_folder(input_dir: str, output_dir: str):
    os.makedirs(output_dir, exist_ok=True)
    input_files = list_video_files(input_dir)

    print(f"\n开始标准化 A 文件夹：{input_dir}")
    print(f"共发现 {len(input_files)} 个视频")

    for file_name in input_files:
        input_path = os.path.join(input_dir, file_name)
        stem = Path(file_name).stem
        output_name = f"{stem}_std.mp4"
        output_path = os.path.join(output_dir, output_name)

        try:
            standardize_video(input_path, output_path)
            print(f"标准化完成：{file_name} -> {output_name}")
        except subprocess.CalledProcessError as e:
            print(f"标准化失败：{file_name}，错误：{e}")


def trim_folder(input_dir: str, output_dir: str, trim_seconds: int = 5):
    os.makedirs(output_dir, exist_ok=True)
    input_files = list_video_files(input_dir)

    print(f"\n开始裁剪并标准化文件夹：{input_dir}")
    print(f"共发现 {len(input_files)} 个视频")

    for file_name in input_files:
        input_path = os.path.join(input_dir, file_name)
        stem = Path(file_name).stem
        output_name = f"{stem}_5s.mp4"
        output_path = os.path.join(output_dir, output_name)

        try:
            trim_and_standardize_video(input_path, output_path, trim_seconds)
            print(f"裁剪完成：{file_name} -> {output_name}")
        except subprocess.CalledProcessError as e:
            print(f"裁剪失败：{file_name}，错误：{e}")


def build_output_name(counter: int) -> str:
    return f"{NAME_PREFIX}{counter:02d}{NAME_SUFFIX}"


def concat_with_bgm(video_a: str, video_b: str, video_c: str, bgm_path: str, output_path: str):
    """
    拼接 A+B+C，并加入 BGM
    BGM 自动循环，并按最终视频时长截断
    """
    filter_complex = (
        "[0:v][1:v][2:v]concat=n=3:v=1:a=0[v];"
        f"[3:a]volume={BGM_VOLUME}[bgm]"
    )

    cmd = [
        FFMPEG,
        "-y" if OVERWRITE else "-n",
        "-i", video_a,
        "-i", video_b,
        "-i", video_c,
        "-stream_loop", "-1",
        "-i", bgm_path,
        "-filter_complex", filter_complex,
        "-map", "[v]",
        "-map", "[bgm]",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "18",
        "-c:a", "aac",
        "-ar", str(TARGET_AR),
        "-ac", str(TARGET_AC),
        "-shortest",
        "-movflags", "+faststart",
        output_path
    ]
    run_cmd(cmd)


# =========================
# 主流程
# =========================

def main():
    ensure_dirs()

    if CLEAR_OLD_OUTPUT:
        print("清空旧输出文件...")
        clear_folder(DIR_A_STD, VIDEO_EXTS)
        clear_folder(DIR_B_CUT, VIDEO_EXTS)
        clear_folder(DIR_C_CUT, VIDEO_EXTS)
        clear_folder(OUTPUT_DIR, VIDEO_EXTS)

    print("========== 第一步：标准化 A 库 ==========")
    standardize_folder(DIR_A, DIR_A_STD)

    print("\n========== 第二步：裁剪并标准化 B 库 ==========")
    trim_folder(DIR_B, DIR_B_CUT, TRIM_SECONDS)

    print("\n========== 第三步：裁剪并标准化 C 库 ==========")
    trim_folder(DIR_C, DIR_C_CUT, TRIM_SECONDS)

    print("\n========== 第四步：读取素材 ==========")

    files_a = list_video_files(DIR_A_STD)
    files_b = list_video_files(DIR_B_CUT)
    files_c = list_video_files(DIR_C_CUT)

    if not files_a:
        print("A_std 为空，停止执行。")
        return

    if not files_b:
        print("B_cut 为空，停止执行。")
        return

    if not files_c:
        print("C_cut 为空，停止执行。")
        return

    try:
        picked_bgm_file = auto_pick_first_audio(DIR_MUSIC)
    except FileNotFoundError as e:
        print(str(e))
        return

    bgm_path = os.path.join(DIR_MUSIC, picked_bgm_file)

    print(f"A hook 数量：{len(files_a)}")
    print(f"B 录屏数量：{len(files_b)}")
    print(f"C 录屏数量：{len(files_c)}")
    print(f"固定 BGM：{picked_bgm_file}")
    print(f"总输出数：{len(files_a)}")

    print("\n========== 第五步：拼接并输出 ==========")

    mapping_rows = []
    counter = 1

    for i, a in enumerate(files_a):
        path_a = os.path.join(DIR_A_STD, a)

        # B / C 顺序轮换
        b_file = files_b[i % len(files_b)]
        c_file = files_c[i % len(files_c)]

        path_b = os.path.join(DIR_B_CUT, b_file)
        path_c = os.path.join(DIR_C_CUT, c_file)

        output_name = build_output_name(counter)
        output_path = os.path.join(OUTPUT_DIR, output_name)

        a_stem = Path(a).stem.replace("_std", "")
        b_stem = Path(b_file).stem.replace("_5s", "")
        c_stem = Path(c_file).stem.replace("_5s", "")
        bgm_stem = Path(picked_bgm_file).stem

        print(f"\n正在生成第 {counter:02d} 条：{output_name}")
        print(f"A: {a} | B: {b_file} | C: {c_file}")

        try:
            concat_with_bgm(path_a, path_b, path_c, bgm_path, output_path)

            mapping_rows.append({
                "序号": f"{counter:02d}",
                "成品文件名": output_name,
                "A素材": a,
                "B素材": b_file,
                "C素材": c_file,
                "BGM": picked_bgm_file,
                "A素材名(无后缀)": a_stem,
                "B素材名(无后缀)": b_stem,
                "C素材名(无后缀)": c_stem,
                "BGM名(无后缀)": bgm_stem,
            })

            counter += 1

        except subprocess.CalledProcessError as e:
            print(f"拼接失败：{output_name}，错误：{e}")

    print("\n========== 第六步：输出 mapping_hook_test_bgm.csv ==========")
    with open(MAPPING_CSV, "w", newline="", encoding="utf-8-sig") as csvfile:
        fieldnames = [
            "序号", "成品文件名",
            "A素材", "B素材", "C素材", "BGM",
            "A素材名(无后缀)", "B素材名(无后缀)", "C素材名(无后缀)", "BGM名(无后缀)"
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(mapping_rows)

    print("\n全部完成。")
    print(f"成品输出目录：{OUTPUT_DIR}")
    print(f"映射表：{MAPPING_CSV}")


if __name__ == "__main__":
    main()

    
