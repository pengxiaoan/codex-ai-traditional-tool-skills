from __future__ import annotations

import argparse
import asyncio
import math
import re
import subprocess
import wave
from pathlib import Path

import imageio.v2 as imageio
import imageio_ffmpeg
import win32com.client


DEFAULT_HIGHLIGHTS = [
    "一句需求生成绘图脚本",
    "AutoCAD 自动完成复杂图纸",
    "适合重复制图工作流",
]

FONT_CANDIDATES = [
    Path("C:/Windows/Fonts/simhei.ttf"),
    Path("C:/Windows/Fonts/msyh.ttc"),
    Path("C:/Windows/Fonts/simsun.ttc"),
]


def slug(value: str) -> str:
    text = re.sub(r"[^A-Za-z0-9]+", "_", value).strip("_").lower()
    return text or "tutorial_video"


def video_metadata(path: Path) -> dict:
    reader = imageio.get_reader(path)
    try:
        meta = reader.get_meta_data()
    finally:
        reader.close()
    size = meta.get("source_size") or meta.get("size") or (1920, 1080)
    return {
        "duration": float(meta.get("duration") or 0),
        "fps": float(meta.get("fps") or 30),
        "width": int(size[0]),
        "height": int(size[1]),
    }


def build_default_script(title: str, topic: str, highlights: list[str], duration: float) -> str:
    return (
        f"大家好，这期想分享一个我最近觉得很实用的组合：{title}。"
        f"我们不从概念讲起，直接看它能不能帮我们完成一件具体的事：让 AutoCAD 自动画出一张复杂机械图。"
        f"整个过程里，Codex 更像是一个会写脚本、会调试流程的工程助手。"
        f"我给它目标和限制条件，它负责把需求拆成图层、线条、圆、标注、文字样式这些可执行步骤。"
        f"接着脚本通过 AutoCAD 的自动化接口新建图纸，一步一步把图框、齿轮、轴承、剖面线和尺寸标注画出来。"
        f"这个地方最有意思的是，传统工具并没有被替代。AutoCAD 还是负责专业绘图，Codex 负责把重复操作整理成稳定流程。"
        f"中间也遇到过很真实的问题，比如中文标注显示成问号、图层切换不稳定。"
        f"这些问题不是靠手动绕过去，而是继续让 Codex 修改脚本，把字体样式和图层设置固定下来。"
        f"所以这套方法的价值，不只是生成一张图，而是把一次操作沉淀成以后可以反复调用的工作流。"
        f"如果你平时也要处理制图、报表、批量整理这类重复任务，可以先选一个边界清楚的小流程，让 AI 帮你自动化。"
        f"从这个例子看，Codex 加 AutoCAD 的组合，最适合做的不是炫技，而是把传统软件里耗时间的步骤变成可复用的流程。"
    )


def read_script(script_file: Path | None, title: str, topic: str, highlights: list[str], duration: float) -> str:
    if script_file:
        return script_file.read_text(encoding="utf-8").strip()
    return build_default_script(title, topic, highlights, duration)


def find_chinese_voice(voice) -> object | None:
    tokens = list(voice.GetVoices())
    preferred = ("Huihui", "Chinese", "Simplified", "China")
    for keyword in preferred:
        for token in tokens:
            desc = token.GetDescription()
            if keyword.lower() in desc.lower():
                return token
    return tokens[0] if tokens else None


def synthesize_sapi_voice(text: str, output_wav: Path, rate: int, volume: int) -> Path:
    output_wav.parent.mkdir(parents=True, exist_ok=True)
    voice = win32com.client.Dispatch("SAPI.SpVoice")
    token = find_chinese_voice(voice)
    if token is not None:
        voice.Voice = token
    voice.Rate = int(rate)
    voice.Volume = int(volume)

    stream = win32com.client.Dispatch("SAPI.SpFileStream")
    stream.Open(str(output_wav), 3, False)
    try:
        voice.AudioOutputStream = stream
        voice.Speak(text)
    finally:
        stream.Close()
    return output_wav


def ps_quote(value: Path | str) -> str:
    return "'" + str(value).replace("'", "''") + "'"


def synthesize_winrt_voice(text: str, output_wav: Path, voice_hint: str) -> Path:
    output_wav.parent.mkdir(parents=True, exist_ok=True)
    text_file = output_wav.with_suffix(".txt")
    text_file.write_text(text, encoding="utf-8")
    script = f"""
Add-Type -AssemblyName System.Runtime.WindowsRuntime
[Windows.Media.SpeechSynthesis.SpeechSynthesizer, Windows.Media.SpeechSynthesis, ContentType=WindowsRuntime] | Out-Null
[Windows.Media.SpeechSynthesis.SpeechSynthesisStream, Windows.Media.SpeechSynthesis, ContentType=WindowsRuntime] | Out-Null
[Windows.Storage.Streams.RandomAccessStream, Windows.Storage.Streams, ContentType=WindowsRuntime] | Out-Null
$text = Get-Content -Raw -Encoding UTF8 -LiteralPath {ps_quote(text_file)}
$outFile = {ps_quote(output_wav)}
$synth = [Windows.Media.SpeechSynthesis.SpeechSynthesizer]::new()
$voice = [Windows.Media.SpeechSynthesis.SpeechSynthesizer]::AllVoices | Where-Object {{ $_.DisplayName -like '*{voice_hint}*' -or $_.Description -like '*{voice_hint}*' }} | Select-Object -First 1
if ($null -eq $voice) {{
  $voice = [Windows.Media.SpeechSynthesis.SpeechSynthesizer]::AllVoices | Where-Object {{ $_.Gender -eq 'Male' -and $_.Language -eq 'zh-CN' }} | Select-Object -First 1
}}
if ($null -ne $voice) {{ $synth.Voice = $voice }}
$op = $synth.SynthesizeTextToStreamAsync($text)
$method = [System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object {{ $_.Name -eq 'AsTask' -and $_.IsGenericMethodDefinition -and $_.GetParameters().Count -eq 1 }} | Select-Object -First 1
$generic = $method.MakeGenericMethod([Windows.Media.SpeechSynthesis.SpeechSynthesisStream])
$task = $generic.Invoke($null, @($op))
$task.Wait()
$stream = $task.Result
$readStream = [System.IO.WindowsRuntimeStreamExtensions]::AsStreamForRead($stream)
$fileStream = [System.IO.File]::Open($outFile, [System.IO.FileMode]::Create)
try {{ $readStream.CopyTo($fileStream) }} finally {{ $fileStream.Close(); $readStream.Close(); $stream.Dispose(); $synth.Dispose() }}
"""
    subprocess.run(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script],
        check=True,
    )
    if output_wav.stat().st_size <= 46:
        raise ValueError("WinRT speech synthesis produced an empty audio file")
    return output_wav


async def synthesize_edge_voice(text: str, output_mp3: Path, voice_name: str, rate: str, volume: str) -> None:
    import edge_tts

    output_mp3.parent.mkdir(parents=True, exist_ok=True)
    communicate = edge_tts.Communicate(text, voice_name, rate=rate, volume=volume)
    await communicate.save(str(output_mp3))


def synthesize_voice(
    text: str,
    output_dir: Path,
    engine: str,
    winrt_voice: str,
    sapi_rate: int,
    sapi_volume: int,
    edge_voice: str,
    edge_rate: str,
    edge_volume: str,
) -> Path:
    if engine == "winrt":
        try:
            return synthesize_winrt_voice(text, output_dir / "voiceover_male.wav", winrt_voice)
        except Exception as exc:
            print(f"WinRT TTS failed, falling back to Edge/SAPI: {exc}")
            engine = "edge"

    if engine == "edge":
        output_mp3 = output_dir / "voiceover_male.mp3"
        try:
            asyncio.run(synthesize_edge_voice(text, output_mp3, edge_voice, edge_rate, edge_volume))
            return output_mp3
        except Exception as exc:
            print(f"Edge TTS failed, falling back to Windows SAPI: {exc}")

    return synthesize_sapi_voice(text, output_dir / "voiceover.wav", rate=sapi_rate, volume=sapi_volume)


def wav_duration(path: Path) -> float:
    with wave.open(str(path), "rb") as wav:
        return wav.getnframes() / float(wav.getframerate())


def media_duration(path: Path) -> float:
    if path.suffix.lower() == ".wav":
        return wav_duration(path)

    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    result = subprocess.run(
        [ffmpeg, "-hide_banner", "-i", str(path)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    match = re.search(r"Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)", result.stderr)
    if not match:
        raise ValueError(f"Could not determine audio duration for {path}")
    hours, minutes, seconds = match.groups()
    return int(hours) * 3600 + int(minutes) * 60 + float(seconds)


def split_sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[。！？!?])\s*", text)
    cleaned = [part.strip() for part in parts if part.strip()]
    return cleaned or [text.strip()]


def ass_time(seconds: float) -> str:
    seconds = max(0.0, seconds)
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    cs = int(round((seconds - math.floor(seconds)) * 100))
    if cs >= 100:
        s += 1
        cs = 0
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def wrap_ass_text(text: str, max_chars: int = 24) -> str:
    text = text.replace(",", "，").replace("{", "").replace("}", "")
    chunks = [text[i : i + max_chars] for i in range(0, len(text), max_chars)]
    return r"\N".join(chunks[:2])


def find_font() -> str:
    for path in FONT_CANDIDATES:
        if path.exists():
            return path.stem
    return "SimHei"


def write_ass_subtitles(sentences: list[str], output_ass: Path, audio_duration: float, width: int, height: int) -> None:
    output_ass.parent.mkdir(parents=True, exist_ok=True)
    weights = [max(8, len(sentence)) for sentence in sentences]
    total_weight = sum(weights)
    cursor = 0.0
    font_size = max(34, int(height * 0.042))
    margin_v = max(46, int(height * 0.07))
    font_name = find_font()

    lines = [
        "[Script Info]",
        "ScriptType: v4.00+",
        f"PlayResX: {width}",
        f"PlayResY: {height}",
        "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        f"Style: Default,{font_name},{font_size},&H00F1F7F7,&H000000FF,&H00101518,&HAA000000,0,0,0,0,100,100,0,0,1,3,1,2,80,80,{margin_v},1",
        "",
        "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    ]

    for sentence, weight in zip(sentences, weights):
        duration = max(2.2, audio_duration * weight / total_weight)
        start = cursor
        end = min(audio_duration, start + duration)
        if end - start < 1.0:
            end = min(audio_duration, start + 1.0)
        cursor = end
        lines.append(f"Dialogue: 0,{ass_time(start)},{ass_time(end)},Default,,0,0,0,,{wrap_ass_text(sentence)}")
        if cursor >= audio_duration - 0.2:
            break

    output_ass.write_text("\n".join(lines), encoding="utf-8")


def ffmpeg_filter_path(path: Path) -> str:
    text = path.resolve().as_posix()
    return text.replace(":", r"\:")


def run_intro(
    source: Path,
    output_dir: Path,
    title: str,
    highlights: list[str],
    subtitle: str,
) -> Path:
    intro_script = Path.home() / ".codex" / "skills" / "ai-tool-video-intro" / "scripts" / "make_intro.py"
    if not intro_script.exists():
        return source

    intro = output_dir / "intro.mp4"
    combined = output_dir / "video_with_intro.mp4"
    command = [
        "python",
        str(intro_script),
        "--input",
        str(source),
        "--output-intro",
        str(intro),
        "--output-combined",
        str(combined),
        "--title",
        title,
        "--subtitle",
        subtitle,
        "--caption",
        "AI TOOL WORKFLOW",
        "--duration",
        "3.2",
        "--fps",
        "30",
    ]
    for item in highlights[:3]:
        command.extend(["--highlight", item])
    subprocess.run(command, check=True)
    return combined


def mux_video(video: Path, audio: Path, subtitles: Path, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    sub_filter = f"ass='{ffmpeg_filter_path(subtitles)}'"
    duration = max(0.1, video_metadata(video)["duration"])
    command = [
        ffmpeg,
        "-y",
        "-i",
        str(video),
        "-i",
        str(audio),
        "-filter_complex",
        f"[0:v]{sub_filter}[v];[1:a]apad=whole_dur={duration:.3f},atrim=0:{duration:.3f}[a]",
        "-map",
        "[v]",
        "-map",
        "[a]",
        "-t",
        f"{duration:.3f}",
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-crf",
        "20",
        "-preset",
        "veryfast",
        "-c:a",
        "aac",
        "-b:a",
        "160k",
        "-movflags",
        "+faststart",
        str(output),
    ]
    subprocess.run(command, check=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Package a tutorial recording with narration, voiceover, subtitles, and optional intro.")
    parser.add_argument("--input", required=True, help="Source recording.")
    parser.add_argument("--title", default="Codex + AutoCAD", help="Video title and opener title.")
    parser.add_argument("--topic", default=None, help="Detailed topic; defaults to title.")
    parser.add_argument("--highlight", action="append", default=None, help="Opener/narration highlight. Pass up to three times.")
    parser.add_argument("--script-file", default=None, help="Optional custom narration text file.")
    parser.add_argument("--output-dir", default=None, help="Folder for generated assets.")
    parser.add_argument("--tts-engine", choices=("winrt", "edge", "sapi"), default="winrt", help="TTS engine. WinRT uses the local Microsoft Kangkang Chinese male voice.")
    parser.add_argument("--winrt-voice", default="Kangkang", help="Local Windows WinRT voice hint. Default is the Chinese male voice Kangkang.")
    parser.add_argument("--edge-voice", default="zh-CN-YunxiNeural", help="Edge neural TTS voice. Default is a Chinese male voice.")
    parser.add_argument("--edge-rate", default="+0%", help="Edge neural TTS rate, such as +0%%, -5%%, or +8%%.")
    parser.add_argument("--edge-volume", default="+0%", help="Edge neural TTS volume, such as +0%%.")
    parser.add_argument("--voice-rate", type=int, default=0, help="Windows SAPI fallback voice rate.")
    parser.add_argument("--voice-volume", type=int, default=100, help="Windows SAPI voice volume.")
    parser.add_argument("--no-intro", action="store_true", help="Skip fixed opener generation.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source = Path(args.input).resolve()
    if not source.exists():
        raise FileNotFoundError(source)

    title = args.title
    topic = args.topic or args.title
    highlights = args.highlight or DEFAULT_HIGHLIGHTS
    out_dir = Path(args.output_dir).resolve() if args.output_dir else (source.parent / f"{slug(title)}_publish")
    out_dir.mkdir(parents=True, exist_ok=True)

    meta = video_metadata(source)
    script_text = read_script(Path(args.script_file).resolve() if args.script_file else None, title, topic, highlights, meta["duration"])
    narration_file = out_dir / "narration.txt"
    narration_file.write_text(script_text, encoding="utf-8")

    voice_file = synthesize_voice(
        script_text,
        out_dir,
        engine=args.tts_engine,
        winrt_voice=args.winrt_voice,
        sapi_rate=args.voice_rate,
        sapi_volume=args.voice_volume,
        edge_voice=args.edge_voice,
        edge_rate=args.edge_rate,
        edge_volume=args.edge_volume,
    )
    audio_duration = media_duration(voice_file)

    base_video = source if args.no_intro else run_intro(
        source=source,
        output_dir=out_dir,
        title=title,
        highlights=highlights,
        subtitle="全自动绘图 / 工作流分享 / 实战复盘",
    )
    final_meta = video_metadata(base_video)

    sentences = split_sentences(script_text)
    subtitles = out_dir / "subtitles.ass"
    write_ass_subtitles(sentences, subtitles, audio_duration, final_meta["width"], final_meta["height"])

    final_video = out_dir / "final_upload_ready.mp4"
    mux_video(base_video, voice_file, subtitles, final_video)

    print(f"Narration: {narration_file}")
    print(f"Voiceover: {voice_file} ({audio_duration:.1f}s)")
    print(f"Subtitles: {subtitles}")
    print(f"Base video: {base_video}")
    print(f"Final video: {final_video}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
