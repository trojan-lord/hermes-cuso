#!/usr/bin/env python3
"""
Marshall Voice Extractor - Speaker Filtering Pipeline
=====================================================
Filters Demucs-separated vocal tracks to extract only segments where
the target speaker is talking, using ECAPA-TDNN speaker embeddings.

This is the actual working script used to extract Marshall's voice from
28 Demucs vocal tracks. Processed 5+ hours of audio in ~150 seconds on CPU.

Usage:
  python3 extract_speaker.py --reference reference.spk --input-dir demucs/ --output filtered.wav

Requirements:
  - qwen-tts Python package
  - librosa, soundfile, torch, numpy
  - Reference .spk file from qwen-codec --talker
"""

import argparse
import json
import os
import struct
import sys
import time
from pathlib import Path

import librosa
import numpy as np
import soundfile as sf
import torch
import warnings
warnings.filterwarnings("ignore", message=".*flash-attn.*")


def load_spk_embedding(path: str) -> np.ndarray:
    """Load a .spk file (2048 float32 values) as a numpy vector."""
    with open(path, "rb") as f:
        data = f.read()
    n_floats = len(data) // 4
    embedding = struct.unpack(f"{n_floats}f", data)
    return np.array(embedding, dtype=np.float32)


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Compute cosine similarity between two vectors."""
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(a, b) / (norm_a * norm_b))


def chunk_audio(audio_path: str, chunk_sec: float, overlap: float, sr: int = 24000):
    """Split audio into overlapping chunks. Returns list of (chunk, start_sec, end_sec)."""
    audio, _ = librosa.load(audio_path, sr=sr, mono=True)
    chunk_samples = int(chunk_sec * sr)
    step_samples = int((chunk_sec - overlap) * sr)
    chunks = []
    start = 0
    while start + chunk_samples <= len(audio):
        chunks.append((audio[start:start+chunk_samples], start/sr, (start+chunk_samples)/sr))
        start += step_samples
    if start < len(audio) and len(audio) - start > int(1.0 * sr):
        chunks.append((audio[start:], start/sr, len(audio)/sr))
    return chunks


def extract_embeddings(chunks, model):
    """Extract speaker embeddings using ECAPA-TDNN from Qwen3 TTS model."""
    inner_model = model.model
    embeddings = []
    for i, chunk in enumerate(chunks):
        with torch.no_grad():
            spk_emb = inner_model.extract_speaker_embedding(chunk, 24000)
            embeddings.append(spk_emb.cpu().numpy().flatten())
        if (i + 1) % 100 == 0:
            print(f"    ... processed {i+1}/{len(chunks)} chunks")
    return embeddings


def main():
    parser = argparse.ArgumentParser(description="Speaker Filtering Pipeline")
    parser.add_argument("--reference", type=str, required=True,
        help="Path to reference .spk file (2048-dim speaker embedding)")
    parser.add_argument("--reference-wav", type=str, default=None,
        help="Path to reference WAV (for manifest). If omitted, derived from .spk path.")
    parser.add_argument("--input-dir", type=str, required=True,
        help="Directory containing Demucs vocal tracks (vocals.wav files)")
    parser.add_argument("--output", type=str, required=True,
        help="Output path for stitched filtered audio")
    parser.add_argument("--threshold", type=float, default=0.85,
        help="Cosine similarity threshold (0.80-0.95)")
    parser.add_argument("--chunk-sec", type=float, default=4.0,
        help="Chunk duration in seconds")
    parser.add_argument("--overlap", type=float, default=1.5,
        help="Overlap between chunks in seconds")
    parser.add_argument("--model-path", type=str, default="Qwen/Qwen3-TTS-12Hz-1.7B-Base",
        help="HuggingFace model ID or local path")
    parser.add_argument("--device", type=str, default="auto",
        help="Device: auto, cuda:0, cpu")
    parser.add_argument("--jsonl-output", type=str, default=None,
        help="Optional: save match metadata as JSONL")
    args = parser.parse_args()

    if args.device == "auto":
        args.device = "cuda:0" if torch.cuda.is_available() else "cpu"
    print(f"Device: {args.device}")

    # Reference WAV defaults to same name as .spk but with .wav extension
    if args.reference_wav is None:
        args.reference_wav = args.reference.replace(".spk", ".wav")

    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)

    # Load reference
    print(f"Loading reference: {args.reference}")
    ref_embedding = load_spk_embedding(args.reference)
    print(f"  Dim: {len(ref_embedding)}, norm: {np.linalg.norm(ref_embedding):.4f}")

    # Load model
    print(f"\nLoading speaker encoder model...")
    start_load = time.time()
    from qwen_tts import Qwen3TTSModel
    model = Qwen3TTSModel.from_pretrained(
        args.model_path,
        device_map=args.device,
        dtype=torch.bfloat16 if "cuda" in args.device else torch.float32,
    )
    print(f"  Loaded in {time.time()-start_load:.1f}s\n")

    # Find vocal tracks
    vocal_tracks = []
    for entry in sorted(os.listdir(args.input_dir)):
        vocals_path = os.path.join(args.input_dir, entry, "vocals.wav")
        if os.path.isfile(vocals_path):
            vocal_tracks.append((entry, vocals_path))
        elif entry.endswith("vocals.wav"):
            vocal_tracks.append((entry, os.path.join(args.input_dir, entry)))

    print(f"Found {len(vocal_tracks)} vocal tracks")
    print(f"Threshold: {args.threshold}, Chunk: {args.chunk_sec}s, Overlap: {args.overlap}s\n")

    all_matches = []
    total_start = time.time()

    for track_idx, (track_name, track_path) in enumerate(vocal_tracks):
        t0 = time.time()
        chunks = chunk_audio(track_path, args.chunk_sec, args.overlap)
        print(f"[{track_idx+1}/{len(vocal_tracks)}] {track_name}: {len(chunks)} chunks", end="", flush=True)

        embeddings = extract_embeddings([c[0] for c in chunks], model)

        track_matches = []
        for ci, (emb, (_, start_sec, end_sec)) in enumerate(zip(embeddings, chunks)):
            sim = cosine_similarity(ref_embedding, emb)
            if sim >= args.threshold:
                chunk_data = chunks[ci][0]
                track_matches.append({
                    "track": track_name,
                    "start": round(start_sec, 2),
                    "end": round(end_sec, 2),
                    "similarity": round(float(sim), 4),
                })

        all_matches.extend(track_matches)
        elapsed = time.time() - t0
        print(f" -> {len(track_matches)} matches ({elapsed:.1f}s)")

    total_time = time.time() - total_start
    print(f"\n{'='*60}")
    print(f"Total: {len(all_matches)} matches from {len(vocal_tracks)} tracks in {total_time:.0f}s")

    # Sort and show top matches
    all_matches.sort(key=lambda x: x["similarity"], reverse=True)
    print(f"\nTop 10 by similarity:")
    for m in all_matches[:10]:
        print(f"  [{m['similarity']:.4f}] {m['track']} {m['start']:.1f}s-{m['end']:.1f}s")

    # Deduplicate overlapping segments
    deduped = []
    for m in all_matches:
        is_dup = False
        for i, existing in enumerate(deduped):
            if m["track"] == existing["track"]:
                overlap_start = max(m["start"], existing["start"])
                overlap_end = min(m["end"], existing["end"])
                if overlap_end > overlap_start:
                    if m["similarity"] > existing["similarity"]:
                        deduped[i] = m
                    is_dup = True
                    break
        if not is_dup:
            deduped.append(m)
    deduped.sort(key=lambda x: (x["track"], x["start"]))
    print(f"After dedup: {len(deduped)} segments")

    # Stitch matches
    print(f"\nStitching...")
    sr = 24000
    silence = np.zeros(int(0.3 * sr), dtype=np.float32)
    segments = []

    for i, m in enumerate(deduped):
        # Reload the chunk audio from the source track
        audio, _ = librosa.load(
            os.path.join(args.input_dir, m["track"], "vocals.wav")
            if os.path.exists(os.path.join(args.input_dir, m["track"], "vocals.wav"))
            else os.path.join(args.input_dir, f"{m['track']}.wav"),
            sr=sr, mono=True
        )
        chunk_start = int(m["start"] * sr)
        chunk_end = int(m["end"] * sr)
        segments.append(audio[chunk_start:chunk_end])
        if i < len(deduped) - 1:
            segments.append(silence)

    combined = np.concatenate(segments)
    sf.write(args.output, combined, sr)
    print(f"Stitched: {len(combined)/sr:.1f}s -> {args.output}")

    # Save metadata
    if args.jsonl_output:
        with open(args.jsonl_output, "w") as f:
            json.dump(deduped, f, indent=2, ensure_ascii=False)
        print(f"Metadata: {args.jsonl_output}")

    print(f"\nDone! Next: transcribe with Whisper, then fine-tune.")


if __name__ == "__main__":
    main()
