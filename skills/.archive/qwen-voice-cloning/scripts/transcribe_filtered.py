#!/usr/bin/env python3
"""
Transcription Pipeline for Voice Cloning
=========================================
Transcribes filtered speaker audio and generates training data JSONL
for Qwen3-TTS fine-tuning.

Usage:
  python3 transcribe_filtered.py --input filtered.wav --output train_raw.jsonl

Requirements:
  - openai-whisper
  - soundfile
"""

import argparse
import json
import os
import whisper


def main():
    parser = argparse.ArgumentParser(description="Transcribe filtered audio for fine-tuning")
    parser.add_argument("--input", type=str, required=True,
        help="Path to filtered/stitched audio file")
    parser.add_argument("--output", type=str, required=True,
        help="Output JSONL path for training data")
    parser.add_argument("--reference", type=str, default=None,
        help="Reference WAV used for speaker filtering (same as in extract_speaker.py)")
    parser.add_argument("--whisper-model", type=str, default="base",
        help="Whisper model size: tiny, base, small, medium, large")
    parser.add_argument("--language", type=str, default="en",
        help="Language code (default: en)")
    parser.add_argument("--min-segment-duration", type=float, default=1.0,
        help="Minimum segment duration in seconds (skip shorter)")
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"Error: Input file not found: {args.input}")
        return

    # Reference WAV defaults to same directory, common naming pattern
    if args.reference is None:
        # Try to find reference WAV in the same directory as input
        input_dir = os.path.dirname(args.input)
        candidates = [f for f in os.listdir(input_dir) if f.endswith(".wav") and "reference" in f.lower()]
        if candidates:
            args.reference = os.path.join(input_dir, candidates[0])
        else:
            print("Warning: No reference WAV found. Using input as reference.")
            args.reference = args.input

    print(f"Input: {args.input}")
    print(f"Whisper model: {args.whisper_model}")
    print(f"Language: {args.language}")
    print("=" * 60)

    # Load Whisper model
    print("Loading Whisper model...")
    model = whisper.load_model(args.whisper_model, device="cpu")

    # Transcribe
    print("Transcribing...")
    result = model.transcribe(
        args.input,
        language=args.language,
        fp16=False,
        word_timestamps=True,
        verbose=False,
    )

    # Save full transcription
    txt_path = args.output.replace(".jsonl", "_full.txt")
    with open(txt_path, "w") as f:
        f.write(result["text"].strip())
    print(f"Full transcription: {txt_path}")

    # Save segments with timestamps
    segments_path = args.output.replace(".jsonl", "_segments.json")
    segments = []
    for seg in result["segments"]:
        segments.append({
            "start": round(seg["start"], 2),
            "end": round(seg["end"], 2),
            "text": seg["text"].strip(),
        })

    with open(segments_path, "w") as f:
        json.dump(segments, f, indent=2, ensure_ascii=False)
    print(f"Segments: {segments_path} ({len(segments)} segments)")

    # Generate JSONL for fine-tuning
    with open(args.output, "w") as f:
        for seg in segments:
            if seg["end"] - seg["start"] < args.min_segment_duration:
                continue

            entry = {
                "audio": os.path.abspath(args.input),
                "text": seg["text"],
                "ref_audio": os.path.abspath(args.reference),
                "language": "English",
            }
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    # Count entries
    with open(args.output) as f:
        n_entries = sum(1 for _ in f)

    print(f"\nTraining JSONL: {args.output} ({n_entries} samples)")
    print(f"\nNext steps:")
    print(f"  1. Review transcription: {txt_path}")
    print(f"  2. Run prepare_data.py to extract audio codes")
    print(f"  3. Run sft_12hz.py to fine-tune")


if __name__ == "__main__":
    main()
