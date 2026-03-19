import gradio as gr
import subprocess
import os
import json
import time
from datetime import datetime
from pathlib import Path

# Папка для сохранения результатов
OUTPUT_DIR = Path("generated_images")
OUTPUT_DIR.mkdir(exist_ok=True)

ZIMAGE_DIR = Path("MLX_z-image")
HISTORY_FILE = "prompt_history.json"

from typing import Any

def load_history() -> list[dict[str, Any]]:
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_history(history):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def generate_image(prompt, steps, width, height, seed):
    if not prompt.strip():
        return None, "❌ Введи промпт", load_history_display()

    # Формируем имя файла с абсолютным путём
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"image_{timestamp}.png"
    output_path = str(OUTPUT_DIR.resolve() / output_filename)

    # Пишем промпт в файл
    prompt_file = ZIMAGE_DIR / "prompt.txt"
    with open(prompt_file, "w", encoding="utf-8") as f:
        f.write(prompt)

    cmd = [
        "python", "run.py",
        "--width", str(int(width)),
        "--height", str(int(height)),
        "--steps", str(int(steps)),
        "--output", output_path,
    ]

    if seed > 0:
        cmd += ["--seed", str(int(seed))]

    start = time.time()
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=ZIMAGE_DIR
        )
        elapsed = round(time.time() - start)

        if result.returncode != 0:
            error_msg = result.stderr or result.stdout or "Неизвестная ошибка"
            return None, f"❌ Ошибка:\n{error_msg}", load_history_display()

        if not os.path.exists(output_path):
            return None, "❌ Файл не был создан", load_history_display()

        # Сохраняем в историю
        history = load_history()
        history.insert(0, {
            "timestamp": datetime.now().strftime("%d.%m.%Y %H:%M"),
            "prompt": prompt,
            "steps": int(steps),
            "width": int(width),
            "height": int(height),
            "seed": int(seed),
            "model": "Z-Image-Turbo",
            "file": output_path,
            "time": elapsed,
        })
        history = history[:50]
        save_history(history)

        status = f"✅ Готово за {elapsed} сек. → {output_path}"
        return output_path, status, load_history_display()

    except Exception as e:
        return None, f"❌ Ошибка: {str(e)}", load_history_display()


def load_history_display():
    history = load_history()
    if not history:
        return "История пуста"
    lines = []
    for item in history[:10]:
        lines.append(
            f"**{item['timestamp']}** — {item['prompt'][:60]}{'...' if len(item['prompt']) > 60 else ''}\n"
            f"  {item['model']} | {item['width']}×{item['height']} | {item['steps']} шагов | {item.get('time', '?')} сек."
        )
    return "\n\n".join(lines)


# ── UI ──────────────────────────────────────────────────────────────────────
css = """
body { font-family: 'SF Pro Display', -apple-system, sans-serif; }
.container { max-width: 1200px; }
#generate-btn { background: #1a1a1a !important; color: white !important; border: none !important; font-size: 15px !important; padding: 12px !important; }
#generate-btn:hover { background: #333 !important; }
.status-box textarea { font-size: 13px !important; }
"""

with gr.Blocks(title="Z-Image Generator") as demo:

    gr.Markdown("## 🎨 Z-Image-Turbo — генератор изображений")
    gr.Markdown("MLX · Apple Silicon · локально на твоём Mac · ~130 сек на генерацию")

    with gr.Row():

        # ── Левая колонка: настройки ──
        with gr.Column(scale=1):
            prompt = gr.Textbox(
                label="Промпт",
                placeholder="Опиши что хочешь сгенерировать...",
                lines=4,
            )

            with gr.Row():
                width = gr.Slider(256, 2048, value=1024, step=64, label="Ширина")
                height = gr.Slider(256, 2048, value=1024, step=64, label="Высота")

            steps = gr.Slider(1, 20, value=9, step=1, label="Шаги (рекомендуется 9)")

            seed = gr.Number(value=42, label="Сид (0 = случайный)", precision=0)

            generate_btn = gr.Button("✦ Генерировать", elem_id="generate-btn", variant="primary")
            status = gr.Textbox(label="Статус", interactive=False, elem_classes="status-box")

        # ── Правая колонка: результат ──
        with gr.Column(scale=1):
            output_image = gr.Image(label="Результат", type="filepath", height=500)

    # ── История ──
    with gr.Accordion("📋 История промптов (последние 10)", open=False):
        history_display = gr.Markdown(load_history_display())
        refresh_btn = gr.Button("🔄 Обновить историю")

    # ── Примеры промптов ──
    with gr.Accordion("💡 Примеры промптов", open=False):
        gr.Examples(
            examples=[
                ["caricature of a cat wearing a top hat, bold black ink lines, cartoon illustration, white background", 9, 1024, 1024, 42],
                ["cyberpunk city at night, neon lights, rain reflections, cinematic", 9, 1024, 576, 0],
                ["oil painting portrait of an old sailor, dramatic lighting, texture", 9, 768, 1024, 42],
                ["minimalist Japanese zen garden, morning mist, raked sand, bonsai", 9, 1024, 1024, 0],
                ["cute cartoon dog wearing sunglasses, flat design, colorful, white background", 9, 1024, 1024, 42],
            ],
            inputs=[prompt, steps, width, height, seed],
        )



    # ── Events ──
    generate_btn.click(
        fn=generate_image,
        inputs=[prompt, steps, width, height, seed],
        outputs=[output_image, status, history_display],
    )

    refresh_btn.click(fn=load_history_display, outputs=history_display)

if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        inbrowser=True,
        theme=gr.themes.Soft(primary_hue=gr.themes.colors.orange).set(
            block_label_background_fill="#4d2b0b",
            block_label_background_fill_dark="#4d2b0b",
            block_label_text_color="white",
            block_label_text_color_dark="white",
            slider_color="#4d2b0b",
            slider_color_dark="#4d2b0b",
            button_primary_background_fill="#4d2b0b",
            button_primary_background_fill_hover="#3a1f08",
            button_primary_background_fill_dark="#4d2b0b",
            button_primary_background_fill_hover_dark="#3a1f08",
            checkbox_label_background_fill_selected="#4d2b0b",
            checkbox_label_background_fill_selected_dark="#4d2b0b",
            checkbox_background_color_selected="#4d2b0b",
            checkbox_background_color_selected_dark="#4d2b0b",
        ),
        css=css,
    )