# Гайд: локальный генератор изображений на Mac Apple Silicon

## Что получится в итоге

Локальный генератор изображений на базе Z-Image-Turbo с веб-интерфейсом Gradio.
Работает полностью офлайн, ~130 сек на генерацию 1024×1024.

## Требования

- Mac Apple Silicon (M1 / M2 / M3 / M4)
- 16+ ГБ RAM (рекомендуется 32 ГБ)
- Python 3.10+
- Git

---

## Шаг 1 — Подготовка папки и окружения

```bash
mkdir -p ~/Desktop/lesson/llm
cd ~/Desktop/lesson/llm

python3 -m venv qwen-env
source qwen-env/bin/activate
```

---

## Шаг 2 — Установка Z-Image

```bash
git clone https://github.com/uqer1244/MLX_z-image.git
cd MLX_z-image
pip install -r requirements.txt
cd ..
```

---

## Шаг 3 — Установка Gradio

```bash
pip install gradio
```

---

## Шаг 4 — Проверка что всё работает (без интерфейса)

```bash
echo "a photorealistic cat wearing a tiny top hat" > MLX_z-image/prompt.txt

python MLX_z-image/run.py --steps 9 --width 1024 --height 1024 --seed 42
```

При первом запуске скачается модель (~5 ГБ). Результат сохранится в `MLX_z-image/res.png`.

---

## Шаг 5 — Создать app.py

Создай файл `app.py` в папке `llm/` со следующим содержимым:

```python
import gradio as gr
import subprocess
import os
import json
import time
from datetime import datetime
from pathlib import Path

OUTPUT_DIR = Path("generated_images")
OUTPUT_DIR.mkdir(exist_ok=True)

ZIMAGE_DIR = Path("MLX_z-image")
HISTORY_FILE = "prompt_history.json"

def load_history():
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

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = str(OUTPUT_DIR.resolve() / f"image_{timestamp}.png")

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
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=ZIMAGE_DIR)
        elapsed = round(time.time() - start)

        if result.returncode != 0:
            error_msg = result.stderr or result.stdout or "Неизвестная ошибка"
            return None, f"❌ Ошибка:\n{error_msg}", load_history_display()

        if not os.path.exists(output_path):
            return None, "❌ Файл не был создан", load_history_display()

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

        return output_path, f"✅ Готово за {elapsed} сек. → {output_path}", load_history_display()

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


css = """
#generate-btn { background: #1a1a1a !important; color: white !important; border: none !important; font-size: 15px !important; padding: 12px !important; }
#generate-btn:hover { background: #333 !important; }
"""

with gr.Blocks(title="Z-Image Generator", css=css, theme=gr.themes.Soft()) as demo:

    gr.Markdown("## 🎨 Z-Image-Turbo — генератор изображений")
    gr.Markdown("MLX · Apple Silicon · локально · ~130 сек на генерацию")

    with gr.Row():
        with gr.Column(scale=1):
            prompt = gr.Textbox(label="Промпт", placeholder="Опиши что хочешь сгенерировать...", lines=4)

            with gr.Row():
                width = gr.Slider(256, 2048, value=1024, step=64, label="Ширина")
                height = gr.Slider(256, 2048, value=1024, step=64, label="Высота")

            steps = gr.Slider(1, 20, value=9, step=1, label="Шаги (рекомендуется 9)")
            seed = gr.Number(value=42, label="Seed (0 = случайный)", precision=0)

            generate_btn = gr.Button("✦ Генерировать", elem_id="generate-btn", variant="primary")
            status = gr.Textbox(label="Статус", interactive=False)

        with gr.Column(scale=1):
            output_image = gr.Image(label="Результат", type="filepath", height=500)

    with gr.Accordion("📋 История промптов", open=False):
        history_display = gr.Markdown(load_history_display())
        refresh_btn = gr.Button("🔄 Обновить")

    with gr.Accordion("💡 Примеры промптов", open=False):
        gr.Examples(
            examples=[
                ["caricature of a cat wearing a top hat, bold black ink lines, cartoon, white background", 9, 1024, 1024, 42],
                ["steampunk city at dusk, clockwork spires, hot air balloons, gas lanterns, ink illustration", 9, 1024, 576, 77],
                ["Плюшевые мишки сидят на мягком диване, уютная комната", 9, 1024, 1024, 42],
                ["minimalist Japanese zen garden, morning mist, raked sand, bonsai", 9, 1024, 1024, 0],
            ],
            inputs=[prompt, steps, width, height, seed],
        )

    generate_btn.click(
        fn=generate_image,
        inputs=[prompt, steps, width, height, seed],
        outputs=[output_image, status, history_display],
    )
    refresh_btn.click(fn=load_history_display, outputs=history_display)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860, share=False, inbrowser=True)
```

---

## Шаг 6 — Создать .gitignore

```bash
cat > ~/Desktop/lesson/llm/.gitignore << 'EOF'
qwen-env/
generated_images/
prompt_history.json
MLX_z-image/Z-Image-Turbo-MLX/
*.png
EOF
```

---

## Шаг 7 — Настройка VS Code (опционально)

Создай файл `.vscode/settings.json`:

```json
{
    "python.defaultInterpreterPath": "/Users/ИМЯ/Desktop/lesson/llm/qwen-env/bin/python",
    "python.analysis.extraPaths": [
        "/Users/ИМЯ/Desktop/lesson/llm/qwen-env/lib/python3.13/site-packages"
    ]
}
```

Замени `ИМЯ` на своё имя пользователя Mac.

---

## Запуск (каждый раз)

```bash
cd ~/Desktop/lesson/llm
source qwen-env/bin/activate
python app.py
```

Браузер откроется на `http://localhost:7860`

---

## Итоговая структура проекта

```
llm/
├── app.py
├── README.md
├── .gitignore
├── .vscode/
│   └── settings.json
├── MLX_z-image/          ← клонирован с GitHub
│   ├── run.py
│   ├── prompt.txt
│   ├── requirements.txt
│   └── Z-Image-Turbo-MLX/  ← скачивается автоматически, не в git
├── generated_images/       ← не в git
├── prompt_history.json     ← не в git
└── qwen-env/               ← не в git
```

---

## Советы по промптам

- Английский язык даёт лучшее качество, но русский тоже работает
- Для карикатур: `cartoon, bold black ink lines, white background`
- Для фото: `photorealistic, studio lighting, sharp focus`
- Для иллюстраций: `detailed ink illustration, cross-hatching, dramatic lighting`
- Seed фиксирует результат — одинаковый seed + промпт = одинаковая картинка
- Рекомендуемые шаги: 9 (быстро и качественно для Turbo-модели)