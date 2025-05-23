# Obsidian2Epub

A Python application that converts Obsidian markdown files to EPUB format, specifically designed for Kindle reading. It processes articles with proper formatting, handles images, and maintains typography.

## Features

- Convert Obsidian markdown files to EPUB format
- Filter articles by tags
- Support for both "contains" and "does not contain" tag criteria
- Automatic image processing and optimization for Kindle
- Customizable selection of articles (newest, oldest, or random)
- Limit number of articles in the output
- Preserves typography (em dashes, en dashes, etc.)
- Generates a custom cover with publication sources
- Modern GUI interface

## Requirements

- Python 3.6 or higher
- Required packages (install via `pip install -r requirements.txt`):
  - Pillow
  - beautifulsoup4
  - ebooklib
  - markdown
  - requests
  - PyYAML
  - ttkbootstrap

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/Obsidian2Epub.git
cd Obsidian2Epub
```

2. Create and activate a virtual environment:
```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### GUI Interface

Run the GUI application:
```bash
python ui.py
```

The GUI allows you to:
- Select the markdown folder
- Specify tag name and criteria
- Choose number of entries and selection mode
- Set output filename and directory
- Monitor conversion progress

### Command Line

You can also use the script directly:
```python
from mdconverter import create_epub

create_epub(
    markdown_folder="path/to/markdown/folder",
    tag_name="your_tag",
    output_path="output.epub",
    num_entries=10,
    selection_mode='newest',
    tag_criteria='does not contain'
)
```

## Markdown File Format

Your markdown files should include YAML frontmatter with the following fields:
```yaml
---
title: Article Title
author: Author Name
published: Publication Date
source: URL
tags: [tag1, tag2]
---
```


## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 