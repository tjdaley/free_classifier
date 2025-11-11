#!/usr/bin/env python3
"""
Simple multi-LLM, multimodal file classifier (CLI)

Copyright (c) 2025 by Thomas J. Daley. All rights reserved.
See accompanying LICENSE file in repository root for details.

- Recursively walks a root directory, skipping folders that start with "."
- Converts each file to up to 5 PNG "pages" (PDF pages, images, or text rendered to image)
- Sends those images + a prompt (from file) to the chosen LLM
- Prints "<provider> | <path> -> <classification>"

Configuration (via env or .env):
  LLM_NAME   : one of "openai", "anthropic", "gemini"
  LLM_API_KEY: API key for that provider
  PROMPT_FILE: path to a prompt text file

Usage:
  $ pip install -r requirements.txt
  $ python classify_docs.py /path/to/root

Notes:
- For PDFs we use PyMuPDF (pure Python) to render images—no system deps.
- For image files we normalize to PNG bytes.
- For text-like files we render the first chunk of text onto a white PNG to preserve “layout” for the LLM.
- Keep it simple: one request per file, first 5 pages/images max.
"""

from __future__ import annotations

import argparse
import base64
import csv
import io
import os
from pathlib import Path
from typing import List, Optional, Tuple

from pydantic import Field
from pydantic_settings import BaseSettings

# Image/PDF helpers
from PIL import Image, ImageDraw, ImageFont
import fitz  # PyMuPDF

# Providers
# Install: openai anthropic google-generativeai

TEXT_EXTS = {".txt", ".md", ".eml", ".log", ".csv"}
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff"}
PDF_EXTS = {".pdf"}

MAX_PAGES = 5
TEXT_CHARS_LIMIT = 8000  # keep it short to fit onto one or two images if needed


class AppSettings(BaseSettings):
    llm_name: str = Field(..., alias="LLM_NAME")        # "openai" | "anthropic" | "gemini"
    llm_model: str = Field("default-model", alias="LLM_MODEL")
    llm_api_key: str = Field(..., alias="LLM_API_KEY")
    prompt_file: Path = Field(..., alias="PROMPT_FILE")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


def is_hidden_dir(path: Path) -> bool:
    return path.name.startswith(".")


def read_prompt(prompt_path: Path) -> str:
    return prompt_path.read_text(encoding="utf-8").strip()


def img_to_png_bytes(img: Image.Image) -> bytes:
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def render_pdf_to_images(pdf_path: Path, max_pages: int = MAX_PAGES, zoom: float = 2.0) -> List[bytes]:
    """
    Render first `max_pages` pages of a PDF to PNG bytes using PyMuPDF.
    Zoom 2.0 ~ 144 DPI; adjust up/down if needed.

    Args:
        pdf_path: Path to the PDF file.
        max_pages: Maximum number of pages to render.
        zoom: Zoom factor for rendering.

    Returns:
        List of PNG byte strings, one per page.
    """
    images: List[bytes] = []
    with fitz.open(pdf_path.as_posix()) as doc:
        pages = min(len(doc), max_pages)
        for i in range(pages):
            page = doc.load_page(i)
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat, alpha=False)
            images.append(pix.tobytes("png"))
    return images


def load_image_file(img_path: Path) -> List[bytes]:
    """
    Normalize any single image to PNG bytes (one page).
    """
    with Image.open(img_path) as im:
        im = im.convert("RGB")
        return [img_to_png_bytes(im)]


def wrap_text_to_image(text: str, width_px: int = 1600, height_px: int = 2000, margin: int = 40, line_spacing: int = 6) -> bytes:
    """
    Draw text onto a white PNG. Uses a default Pillow font for simplicity.

    Args:
        text: The text to render.
        width_px: Width of the image in pixels.
        height_px: Height of the image in pixels.
        margin: Margin in pixels.
        line_spacing: Extra spacing between lines in pixels.

    Returns:
        PNG byte string of the rendered text image.
    """
    # Basic wrapping—greedy by words
    font = ImageFont.load_default()
    draw_img = Image.new("RGB", (width_px, height_px), "white")
    draw = ImageDraw.Draw(draw_img)

    max_text_width = width_px - 2 * margin
    words = text.split()
    lines = []
    cur = ""
    for w in words:
        test = (cur + " " + w).strip()
        if draw.textlength(test, font=font) <= max_text_width:
            cur = test
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)

    y = margin
    for line in lines:
        draw.text((margin, y), line, fill="black", font=font)
        y += font.getbbox(line)[3] - font.getbbox(line)[1] + line_spacing
        if y > height_px - margin:
            break

    return img_to_png_bytes(draw_img)


def load_text_as_images(path: Path) -> List[bytes]:
    """
    Read the first N chars and render as a single image.
    (We keep it to one image for simplicity.)
    """
    text = path.read_text(errors="ignore", encoding="utf-8")[:TEXT_CHARS_LIMIT]
    return [wrap_text_to_image(text)]


def file_to_images(path: Path) -> Optional[List[bytes]]:
    """
    Convert a file to up to 5 PNG images (bytes) depending on type.
    Returns None if the file type is unsupported.
    """
    ext = path.suffix.lower()
    try:
        if ext in PDF_EXTS:
            return render_pdf_to_images(path, MAX_PAGES)
        elif ext in IMAGE_EXTS:
            return load_image_file(path)
        elif ext in TEXT_EXTS:
            return load_text_as_images(path)
        else:
            # Unknown—try best effort: if it's tiny binary or unknown, skip.
            return None
    except Exception as e:
        print(f"[warn] Skipping {path}: {e}")
        return None


# =========== LLM CALLS ===========

def to_b64_images(png_bytes_list: List[bytes]) -> List[str]:
    return [base64.b64encode(b).decode("utf-8") for b in png_bytes_list[:MAX_PAGES]]


def classify_with_openai(api_key: str, prompt: str, pngs: List[bytes], model: str = "gpt-4o-mini") -> str:
    """
    Minimal OpenAI image+text call using Chat Completions (gpt-4o-mini).

    Args:
        api_key: OpenAI API key.
        prompt: Text prompt to send.
        pngs: List of PNG byte strings.
    Returns:
        Classification label as a string.
    """
    from openai import OpenAI
    client = OpenAI(api_key=api_key)

    b64s = to_b64_images(pngs)
    content = [{"type": "text", "text": prompt}]
    for b64 in b64s:
        content.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/png;base64,{b64}"}
        })

    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a careful document classifier. Respond with a short, lowercase label like: bank_statement, credit_card_statement, email, text_message, social_media_message, or other."},
            {"role": "user", "content": content}
        ],
        temperature=0
    )
    return (resp.choices[0].message.content or "").strip()


def classify_with_anthropic(api_key: str, prompt: str, pngs: List[bytes], model: str = "claude-3-5-sonnet-latest") -> str:
    """
    Minimal Anthropic Claude 3.5 Sonnet image+text call.

    Args:
        api_key: Anthropic API key.
        prompt: Text prompt to send.
        pngs: List of PNG byte strings.
    Returns:
        Classification label as a string.
    """
    import anthropic
    client = anthropic.Anthropic(api_key=api_key)

    parts = [{"type": "text", "text": prompt}]
    for b in pngs[:MAX_PAGES]:
        parts.append({
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": "image/png",
                "data": base64.b64encode(b).decode("utf-8"),
            },
        })

    resp = client.messages.create(
        model=model,
        max_tokens=200,
        temperature=0,
        system="You classify documents. Output a short, lowercase label only.",
        messages=[{"role": "user", "content": parts}],
    )
    return (resp.content[0].text if resp.content else "").strip()


def classify_with_gemini(api_key: str, prompt: str, pngs: List[bytes], model: str = "gemini-1.5-flash") -> str:
    """
    Minimal Google Gemini (1.5 Flash) image+text call.

    Args:
        api_key: Google Generative AI API key.
        prompt: Text prompt to send.
        pngs: List of PNG byte strings.
    Returns:
        Classification label as a string.
    """
    import google.generativeai as genai
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model)

    # Build a list of parts: prompt text + image blobs
    parts = [prompt]
    for b in pngs[:MAX_PAGES]:
        parts.append({"mime_type": "image/png", "data": b})

    resp = model.generate_content(parts)
    return (getattr(resp, "text", "") or "").strip()


def classify_images(llm_name: str, api_key: str, prompt: str, pngs: List[bytes], model: str) -> str:
    name = llm_name.strip().lower()
    if name == "openai":
        return classify_with_openai(api_key, prompt, pngs, model)
    if name == "anthropic":
        return classify_with_anthropic(api_key, prompt, pngs, model)
    if name == "gemini":
        return classify_with_gemini(api_key, prompt, pngs, model)
    raise ValueError(f"Unsupported LLM_NAME: {llm_name}")


# =========== WALK + RUN ===========

def iter_files(root: Path):
    """
    Yield all files under root, skipping directories that start with '.'.
    """
    for dirpath, dirnames, filenames in os.walk(root):
        # mutate dirnames in-place to skip dot-directories
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]
        for fn in filenames:
            # skip dot-files too
            if fn.startswith("."):
                continue
            yield Path(dirpath) / fn


def main():
    parser = argparse.ArgumentParser(description="Classify documents in a folder using an LLM.")
    parser.add_argument("root", type=Path, help="Root folder to scan")
    parser.add_argument("--dry-run", action="store_true", help="Scan & render only; do not call the LLM")
    args = parser.parse_args()

    settings = AppSettings()  # pulls from env/.env
    prompt = read_prompt(settings.prompt_file)

    root = args.root
    if not root.exists() or not root.is_dir():
        raise SystemExit(f"Root folder not found: {root}")

    from tqdm import tqdm
    files = list(iter_files(root))
    results = []
    for path in tqdm(files, desc="Classifying", unit="file"):
        imgs = file_to_images(path)
        if not imgs:
            # Not a supported type—just note and continue
            print(f"[skip] {path}")
            continue

        if args.dry_run:
            print(f"[dry] {path} -> {len(imgs)} page(s)")
            continue

        try:
            label = classify_images(settings.llm_name, settings.llm_api_key, prompt, imgs, settings.llm_model)
            # keep output very simple / greppable
            results.append({'path': path, 'label': label, 'llm': settings.llm_name, 'model': settings.llm_model, 'filename': path.name})
        except Exception as e:
            print(f"[error] {path}: {e}")

    # Write results to CSV
    output_csv = root / "filelist.csv"
    with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['filename', 'label', 'llm', 'model', 'path']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in results:
            writer.writerow(row)

    print(f"\nResults written to: {output_csv}")


if __name__ == "__main__":
    main()
