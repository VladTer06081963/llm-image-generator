# AGENTS.md - Guidelines for Agentic Coding Agents

This file provides instructions for AI agents operating in this repository. It covers build/test/lint commands, code style guidelines, and project-specific conventions.

## 📁 Project Overview

This repository contains two main components:
1. `app.py` - A Gradio web interface for generating images using the Z-Image-Turbo model
2. `MLX_z-image/` - An MLX implementation of Z-Image-Turbo optimized for Apple Silicon

The main application (`app.py`) serves as a frontend that calls the MLX-based image generation script located in the `MLX_z-image/` directory.

## 🔧 Build/Lint/Test Commands

### Setting Up the Environment

The project uses a virtual environment located at `qwen-env/`. To activate it:

```bash
source qwen-env/bin/activate
```

### Installing Dependencies

Dependencies for both the main app and the MLX image generation component:

```bash
# Install main app dependencies (if requirements.txt exists in root)
pip install -r requirements.txt 2>/dev/null || echo "No root requirements.txt found"

# Install MLX_z-image dependencies
pip install -r MLX_z-image/requirements.txt
```

### Running the Application

To start the Gradio interface:

```bash
# Activate virtual environment first
source qwen-env/bin/activate
python app.py
```

The application will be available at http://192.168.50.250:7860 (as configured in app.py).

### Running the MLX Image Generation Script Directly

You can also run the image generation script directly:

```bash
cd MLX_z-image
python run.py --help  # See available options
python run.py --width 1024 --height 1024 --steps 9 --seed 42 --output "test.png"
```

### Testing Approach

This project does not have automated unit tests in the traditional sense. Testing is primarily done through:

1. **Manual verification** via the Gradio web interface
2. **Direct execution** of the MLX image generation script with various parameters
3. **Visual inspection** of generated images

To test a single image generation:
1. Activate the virtual environment
2. Run the generation script with specific parameters
3. Check the output file for correctness

Example:
```bash
source qwen-env/bin/activate
cd MLX_z-image
python run.py --width 512 --height 512 --steps 5 --seed 123 --output "test_output.png"
```

### Linting

There are no configured linting tools in this repository. However, you can use standard Python linters:

```bash
# Install common linters (if needed)
pip install flake8 pylint black

# Run linting on Python files
flake8 app.py MLX_z-image/*.py
pylint app.py MLX_z-image/*.py
black --check app.py MLX_z-image/*.py
```

### Type Checking

For type checking with mypy:

```bash
pip install mypy
mypy app.py
```

Note: The MLX_z-image directory may have typing limitations due to MLX framework specifics.

## 📝 Code Style Guidelines

Based on analysis of `app.py`, here are the code style conventions used in this project:

### Imports
- Standard library imports first (grouped logically)
- Third-party imports second
- Local application imports last
- Using `from typing import Any` for type hints when needed
- Multi-line imports when necessary (not observed in current code but acceptable)

### Formatting
- Indentation: 4 spaces (standard Python)
- Maximum line length: Not strictly enforced but appears to be around 100 characters
- Blank lines: Used to separate logical sections and function definitions
- Trailing commas: Used in multi-line function calls and dictionaries when appropriate

### Types
- Type hints are used selectively:
  - Function return types: `-> list[dict[str, Any]]`, `-> tuple`
  - Parameter types: Explicit when beneficial (`prompt: str`, `steps: int`, etc.)
  - Complex types use `typing.Any` when flexibility is needed
  - Recent Python 3.9+ syntax for collection types (`list[dict]` instead of `List[Dict]`)

### Naming Conventions
- Variables: `snake_case` (e.g., `output_filename`, `prompt_file`)
- Functions: `snake_case` (e.g., `load_history`, `generate_image`)
- Constants: `UPPER_SNAKE_CASE` (e.g., `OUTPUT_DIR`, `HISTORY_FILE`)
- Classes: Not present in current code but would follow `PascalCase`
- Gradio components: Descriptive names matching their purpose (e.g., `prompt`, `width`, `generate_btn`)

### Error Handling
- Using try/except blocks for subprocess calls and file operations
- Checking return codes from subprocess calls
- Providing user-friendly error messages in the interface
- Graceful degradation when files don't exist (e.g., history file)
- Specific exception handling rather than bare except clauses

### Documentation
- Comment blocks in Russian/English explaining major sections
- Inline comments for complex operations
- Docstrings are not consistently used but could be added for public functions
- Gradio interface components have clear labels and placeholder text

### Specific Patterns Observed
1. **Path handling**: Using `pathlib.Path` for cross-platform compatibility
2. **Configuration**: Constants defined at the top of the file for easy modification
3. **History management**: Separate functions for loading/saving history with display formatting
4. **Subprocess usage**: Proper handling of stdout/stderr, timeout considerations
5. **UI separation**: Clear separation between logic and Gradio interface components
6. **Localization**: User-facing strings in Russian (consistent throughout)

### Gradio-Specific Conventions
- Component variables named descriptively
- Event handlers defined after component creation
- CSS styling included directly in the Python file for simplicity
- Use of `gr.Blocks` for complex layouts
- Consistent use of `elem_id` and `elem_classes` for styling
- Examples provided in `gr.Examples` component for user guidance

### Security Considerations
- Input validation (checking for empty prompts)
- Using `subprocess.run` with explicit argument lists (not shell=True)
- Proper path resolution with `Path.resolve()` to avoid path traversal
- Limited file permissions (not explicitly set but using safe defaults)

## 🚂 Directory Structure Conventions

```
.
├── app.py                    # Main Gradio application
├── README.md                 # Project overview
├── qwen-env/                 # Virtual environment
├── generated_images/         # Output directory for images
├── MLX_z-image/              # MLX image generation implementation
│   ├── run.py                # Main generation script
│   ├── prompt.txt            # Input prompt file
│   ├── res.png               # Default output
│   ├── requirements.txt      # Dependencies for MLX components
│   └── [other MLX files]     # Model implementation files
└── prompt_history.json       # History of generations
```

## 🔄 Workflow Recommendations

1. **For UI changes**: Modify `app.py` and test via `python app.py`
2. **For MLX model changes**: Work within `MLX_z-image/` directory and test via `python run.py`
3. **For history/features**: Modify the history-related functions in `app.py`
4. **For parameter adjustments**: Update the slider ranges and defaults in the Gradio interface

## 🐛 Troubleshooting

Common issues and their solutions:

1. **Module not found errors**: Ensure virtual environment is activated
2. **CUDA/MLX errors**: Verify Apple Silicon compatibility and MLX installation
3. **Out of memory**: Reduce width/height parameters or use lower bits quantization
4. **Slow generation**: Check that you're using Apple Silicon optimizations (MLX framework)
5. **File permission errors**: Ensure write access to `generated_images/` directory
6. **History not loading**: Check that `prompt_history.json` is valid JSON

## 📚 Resources

- MLX Framework: https://github.com/ml-explore/mlx
- Gradio Documentation: https://www.gradio.app/
- Hugging Face Models: https://huggingface.co/
- Apple Silicon Optimization Guide: Apple Developer Documentation

---

*This AGENTS.md file is intended to guide AI agents in making changes consistent with the existing codebase practices.*