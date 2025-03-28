import os
import re
import datetime
from urllib.parse import urlparse
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import requests
from bs4 import BeautifulSoup
import yaml
import markdown
from ebooklib import epub
from urllib.parse import urlparse, quote  # Import quote here
import uuid


def sanitize_content(content):
    """Sanitize content for EPUB compatibility while preserving special characters.
    
    Removes problematic characters while preserving common special characters like:
    - Smart quotes ('', "")
    - Em/en dashes (–, —)
    - Apostrophes (')
    - Other common special characters
    """
    # Remove NULL bytes and control characters
    content = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1F\uFFFE\uFFFF]', '', content)
    
    # Replace problematic characters with their safe alternatives
    replacements = {
        '\u2018': "'",  # Left single quote
        '\u2019': "'",  # Right single quote
        '\u201C': '"',  # Left double quote
        '\u201D': '"',  # Right double quote
        '\u2026': '...', # Ellipsis
        '\u2022': '•',  # Bullet point
        '\u2010': '-',  # Hyphen
        '\u2011': '-',  # Non-breaking hyphen
        '\u2012': '-',  # Figure dash
        '\u2015': '--', # Horizontal bar
        '\u2024': '.',  # One dot leader
        '\u2025': '..', # Two dot leader
        '\u2027': '·',  # Hyphenation point
        '\u2032': "'",  # Prime
        '\u2033': '"',  # Double prime
        '\u2034': '"',  # Triple prime
        '\u2035': "'",  # Reversed prime
        '\u2036': '"',  # Reversed double prime
        '\u2037': '"',  # Reversed triple prime
        '\u2038': '^',  # Caret
        '\u2039': '<',  # Single left-pointing angle quote
        '\u203A': '>',  # Single right-pointing angle quote
        '\u203B': '*',  # Reference mark
        '\u203C': '!!', # Double exclamation mark
        '\u203D': '?',  # Interrobang
        '\u203E': '_',  # Overline
        '\u2041': '*',  # Caret insertion point
        '\u2042': '§',  # Asterism
        '\u2043': '-',  # Hyphen bullet
        '\u2044': '/',  # Fraction slash
        '\u2045': '[',  # Left square bracket with quill
        '\u2046': ']',  # Right square bracket with quill
        '\u2047': '??', # Double question mark
        '\u2048': '?!', # Question exclamation mark
        '\u2049': '!?', # Exclamation question mark
        '\u204A': '§',  # Tironian sign et
        '\u204B': '¶',  # Reversed pilcrow sign
        '\u204C': '¶',  # Black leftwards bullet
        '\u204D': '¶',  # Black rightwards bullet
        '\u204E': '*',  # Low asterisk
        '\u204F': ';',  # Reversed semicolon
        '\u2050': '=0', # Close up
        '\u2051': '**', # Two asterisks aligned vertically
        '\u2052': '℠',  # Commercial minus sign
        '\u2053': '~',  # Swung dash
        '\u2054': '^',  # Inverted undertie
        '\u2055': '*',  # Flower punctuation mark
        '\u2056': '⁖',  # Three dot punctuation
        '\u2057': '"',  # Quadruple prime
        '\u2058': '⁘',  # Four dot punctuation
        '\u2059': '⁙',  # Five dot punctuation
        '\u205A': '⁚',  # Two dot punctuation
        '\u205B': '⁛',  # Four dot mark
        '\u205C': '⁜',  # Dotted cross
        '\u205D': '⁝',  # Tricolon
        '\u205E': '⁞',  # Vertical four dots
        '\u205F': ' ',  # Mathematical space
        '\u2060': '',   # Word joiner
        '\u2061': '',   # Function application
        '\u2062': '',   # Invisible times
        '\u2063': '',   # Invisible separator
        '\u2064': '',   # Invisible plus
        '\u206A': '',   # Inhibit symmetric swapping
        '\u206B': '',   # Activate symmetric swapping
        '\u206C': '',   # Inhibit arabic form shaping
        '\u206D': '',   # Activate arabic form shaping
        '\u206E': '',   # National digit shapes
        '\u206F': '',   # Nominal digit shapes
    }
    
    # Apply replacements
    for char, replacement in replacements.items():
        content = content.replace(char, replacement)
    
    # Remove any remaining non-printable characters
    content = ''.join(char for char in content if char.isprintable())
    
    return content

def process_image(src, book):
    try:
        encoded_src = quote(src, safe='/:')
        response = requests.get(encoded_src, stream=True)
        response.raise_for_status()
        image_data = response.content
        parsed_url = urlparse(encoded_src)
        image_filename = os.path.basename(parsed_url.path)

        if image_filename and image_data:
            try:
                image = Image.open(BytesIO(image_data))

                # Resize and compress for Kindle
                image = image.convert("RGB")  # Ensure RGB for compatibility
                width, height = image.size

                # Calculate new dimensions based on Kindle's max width (adjust as needed)
                max_width = 768 
                if width > max_width:
                    new_height = int(height * (max_width / width))
                    image = image.resize((max_width, new_height), Image.LANCZOS)  # High-quality downsampling

                img_byte_arr = BytesIO()
                image.save(img_byte_arr, format='JPEG', quality=75, optimize=True) # Use JPEG for smaller file size. Adjust quality as needed.
                image_data = img_byte_arr.getvalue()

            except Exception as e:
                print(f"Error processing image {encoded_src}: {e}")
                return None
            
            image_uuid = str(uuid.uuid4())
            internal_filename = f"images/{image_uuid}"
            image_id = image_uuid
            img = epub.EpubImage(file_name=internal_filename, media_type='image/jpeg', content=image_data)
            img.id = image_id
            book.add_item(img)
            return internal_filename
    except requests.exceptions.RequestException as e:
        print(f"Error fetching image {encoded_src}: {e}")
    return None


## cha
def parse_frontmatter(content):
    """Parses the frontmatter YAML from the Markdown content."""
    try:
        frontmatter_match = re.search(r"^---\n(.*?)\n---", content, re.DOTALL | re.MULTILINE)
        if frontmatter_match:
            frontmatter_yaml = frontmatter_match.group(1)
            frontmatter = yaml.safe_load(frontmatter_yaml)
            return frontmatter
        else:
            print("No frontmatter found.")
            return None
    except yaml.YAMLError as e:
        print(f"Error parsing frontmatter: {e}")
        return None


def append_tag_to_frontmatter(f, new_tag):
    """Appends a tag to the frontmatter of a Markdown file.

    Args:
        f: Open file object of the Markdown file (must be opened in 'r+' mode).
        new_tag: The tag to append.
    """
    f.seek(0)
    content = f.read()

    # Use a regex to extract the frontmatter section
    frontmatter_match = re.search(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not frontmatter_match:
        print(f"No frontmatter found in {f.name}")
        return False

    frontmatter_yaml = frontmatter_match.group(1)
    frontmatter = yaml.safe_load(frontmatter_yaml)
    original_frontmatter = frontmatter.copy()
    print("ORIGINAL: " + yaml.dump(original_frontmatter))

    if frontmatter:
        tags = frontmatter.get('tags', []).copy()
        if isinstance(tags, str):  # Handle comma-separated string tags
            tags = [t.strip() for t in tags.split(',')]

        if new_tag not in tags:
            tags.append(new_tag)
            frontmatter['tags'] = tags
            updated_frontmatter_yaml = yaml.dump(frontmatter, default_flow_style=False)
            print("UPDATED: " + updated_frontmatter_yaml)

            # Reconstruct the updated content
            updated_content = content.replace(
                frontmatter_match.group(0),  # Replace the entire frontmatter section
                f"---\n{updated_frontmatter_yaml}---",  # New frontmatter
                1  # Replace only the first occurrence
            )

            # Overwrite the file
            f.seek(0)
            f.write(updated_content)
            f.truncate()

            print(f"Tag '{new_tag}' appended to {f.name}")
            return True
        else:
            print(f"Tag '{new_tag}' already exists in {f.name}")
            return False
    else:
        print(f"No frontmatter found in {f.name}")
        return False


def create_chapter(filepath, book, tag_name, tag_criteria='does not contain'):
    with open(filepath, 'r+', encoding='utf-8') as f:
        content = f.read()
        frontmatter = parse_frontmatter(content)

        if frontmatter:
            # Handle tags whether they are a list or comma-separated string
            tags = frontmatter.get('tags', [])
            if isinstance(tags, str):
                tags = [t.strip() for t in tags.split(',')]
            
            # Process files based on tag criteria
            tag_match = tag_name in tags
            if (tag_criteria == 'contains' and tag_match) or \
               (tag_criteria == 'does not contain' and not tag_match):
                title = frontmatter.get('title', 'Untitled')
                author = frontmatter.get('author', 'Untitled')
                authors = [re.sub(r'[\[\]]', '', a).strip() for a in author]
                author_string = ", ".join(authors)
                publication_date = frontmatter.get('published', '')
                url = frontmatter.get('source', '')
                publication = urlparse(url).netloc if url else "Unknown"

                # Extract content after the frontmatter
                content_parts = content.split("---", 2)
                markdown_content = content_parts[-1].strip() if len(content_parts) > 2 else ""

                chapter_content = f"<h1>{title}</h1><p>{author_string}, {publication}, {publication_date}</p>\n{markdown_content}"
                html_content = markdown.markdown(chapter_content)
                html_content_utf8 = html_content.encode('utf-8', 'ignore').decode('utf-8')
                soup = BeautifulSoup(html_content_utf8, 'html.parser')
                
                for img in soup.find_all('img'):
                    src = img.get('src')
                    if src and src.startswith("http"):
                        internal_path = process_image(src, book)
                        if internal_path:
                            img['src'] = internal_path
                        else:
                            img.decompose()
                    else:
                        img.decompose()
                
                # Sanitize the final HTML content
                sanitized_html = sanitize_content(str(soup))
                chapter = epub.EpubHtml(
                    title=title,
                    file_name=f"{os.path.splitext(os.path.basename(filepath))[0]}.xhtml",
                    content=sanitized_html
                )
                if chapter:
                    book.add_item(chapter)
                    append_tag_to_frontmatter(f, "archive")
                    return chapter
    return None


def create_cover(publications, date_str):
    """Creates a book cover with publication names and date.
    
    Args:
        publications (list): List of publication names
        date_str (str): Date string in Month Day, Year format
    
    Returns:
        epub.EpubImage: Cover image item for the book
    """
    # Create a new image with a white background
    width = 1600  # Standard Kindle cover width
    height = 2560  # Standard Kindle cover height
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img)
    
    try:
        # Load fonts (using default if custom font fails)
        try:
            title_font = ImageFont.truetype("Arial", 100)
            pub_font = ImageFont.truetype("Arial", 80)
            date_font = ImageFont.truetype("Arial", 60)
        except:
            title_font = ImageFont.load_default()
            pub_font = ImageFont.load_default()
            date_font = ImageFont.load_default()

        # Draw title
        title = "Articles curated from"
        title_bbox = draw.textbbox((0, 0), title, font=title_font)
        title_width = title_bbox[2] - title_bbox[0]
        draw.text(((width - title_width) // 2, 200), title, font=title_font, fill='black')

        # Draw publications (up to 10)
        unique_pubs = list(set(publications))[:10]  # Remove duplicates and limit to 10
        pub_text = "\n".join(unique_pubs)
        pub_bbox = draw.multiline_textbbox((0, 0), pub_text, font=pub_font, align='center')
        pub_height = pub_bbox[3] - pub_bbox[1]
        draw.multiline_text(
            ((width - pub_bbox[2]) // 2, (height - pub_height) // 2),
            pub_text,
            font=pub_font,
            fill='black',
            align='center'
        )

        # Draw date
        date_text = f"on {date_str}"
        date_bbox = draw.textbbox((0, 0), date_text, font=date_font)
        date_width = date_bbox[2] - date_bbox[0]
        draw.text(
            ((width - date_width) // 2, height - 300),
            date_text,
            font=date_font,
            fill='black'
        )

        # Save to bytes
        img_bytes = BytesIO()
        img.save(img_bytes, format='JPEG', quality=95)
        
        # Create cover image item
        cover_image = epub.EpubImage(
            uid='cover_image',
            file_name='cover.jpg',
            media_type='image/jpeg',
            content=img_bytes.getvalue()
        )
        
        return cover_image
        
    except Exception as e:
        print(f"Error creating cover: {e}")
        return None


def create_epub(markdown_folder, tag_name, output_path, tag_criteria='does not contain', num_entries=None, selection_mode='newest', progress_callback=None):
    """Creates the EPUB book from Markdown files.
    
    Args:
        markdown_folder (str): Path to folder containing markdown files
        tag_name (str): Tag to filter files by
        output_path (str): Path to save EPUB file
        tag_criteria (str): How to filter by tag - 'contains' or 'does not contain'
        num_entries (int, optional): Number of entries to include. If None, includes all entries
        selection_mode (str): How to select entries - 'random', 'newest', or 'oldest'
        progress_callback (callable, optional): Function to call with progress updates
    """
    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(output_path)
    if not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
            if progress_callback:
                progress_callback(f"Created output directory: {output_dir}")
        except Exception as e:
            raise ValueError(f"Failed to create output directory: {str(e)}")

    # Check if output file exists
    if os.path.exists(output_path):
        # Generate a unique filename by adding timestamp
        base, ext = os.path.splitext(output_path)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"{base}_{timestamp}{ext}"
        if progress_callback:
            progress_callback(f"Output file already exists. Using new filename: {os.path.basename(output_path)}")

    book = epub.EpubBook()
    book.set_title(f"Articles {datetime.date.today().strftime('%Y-%b-%d')}")
    book.set_language('en')

    # Add default TOC and spine
    book.toc = []
    book.spine = ['nav']

    # Collect publications while processing files
    publications = []

    # Get all markdown files and their modification times
    md_files = []
    total_files = 0
    for filename in os.listdir(markdown_folder):
        if filename.endswith(".md"):
            total_files += 1
            filepath = os.path.join(markdown_folder, filename)
            # Check file against tag criteria
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                frontmatter = parse_frontmatter(content)
                if frontmatter:
                    tags = frontmatter.get('tags', [])
                    if isinstance(tags, str):
                        tags = [t.strip() for t in tags.split(',')]
                    
                    # Select files based on tag criteria
                    tag_match = tag_name in tags
                    if (tag_criteria == 'contains' and tag_match) or \
                       (tag_criteria == 'does not contain' and not tag_match):
                        mod_time = os.path.getmtime(filepath)
                        md_files.append((filepath, mod_time))

    # If no files match the criteria, raise an exception
    if not md_files:
        raise ValueError(f"No files found that {tag_criteria} the tag '{tag_name}'")

    # Select files based on mode and number
    if selection_mode == 'newest':
        md_files.sort(key=lambda x: x[1], reverse=True)
    elif selection_mode == 'oldest':
        md_files.sort(key=lambda x: x[1])
    elif selection_mode == 'random':
        import random
        random.shuffle(md_files)

    # Limit number of files if specified
    if num_entries:
        md_files = md_files[:num_entries]

    # Notify about number of files to process
    if progress_callback:
        progress_callback(f"Found {len(md_files)} files to process out of {total_files} total files")

    # Process selected files
    processed_files = 0
    for filepath, _ in md_files:
        try:
            chapter = create_chapter(filepath, book, tag_name, tag_criteria)
            if chapter:
                book.toc.append(chapter)
                book.spine.append(chapter)
                # Extract publication from frontmatter
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    frontmatter = parse_frontmatter(content)
                    if frontmatter:
                        url = frontmatter.get('source', '')
                        publication = urlparse(url).netloc if url else "Unknown"
                        if publication and publication != "Unknown":
                            publications.append(publication)
                
            processed_files += 1
            if progress_callback:
                progress_callback(f"Processing file {processed_files} of {len(md_files)}: {os.path.basename(filepath)}")
        except Exception as e:
            print(f"Error processing {os.path.basename(filepath)}: {e}")
            if progress_callback:
                progress_callback(f"Error processing {os.path.basename(filepath)}: {str(e)}")

    # Create and add cover
    date_str = datetime.date.today().strftime('%B %d, %Y')
    cover = create_cover(publications, date_str)
    if cover:
        book.add_item(cover)
        book.set_cover("cover.jpg", cover.content)
        if progress_callback:
            progress_callback("Added cover image")

    # Add navigation files
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    # Set the author
    book.add_author("Articles")

    try:
        epub.write_epub(output_path, book, {})
        if progress_callback:
            progress_callback(f"Successfully created EPUB at {output_path}")
        print(f"EPUB created successfully at {output_path}")
    except Exception as e:
        if progress_callback:
            progress_callback(f"Error creating EPUB: {str(e)}")
        print(f"Error creating EPUB: {e}")
        raise

if __name__ == "__main__":
    try:
        markdown_folder = r"/Users/adnan/Library/Mobile Documents/com~apple~CloudDocs/Docs/Misc/Writing/Adnan's Vault/Pocket"
        tag_name = "muscle"
        output_filename = "articles.epub"
        output_folder = r"/Users/adnan/Desktop/moved_to_kindle"
        output_path = os.path.join(output_folder, output_filename)
        create_epub(markdown_folder, tag_name, output_path, num_entries=10, selection_mode='newest', tag_criteria='contains')
    except Exception as e:
        print(f"Error: {str(e)}")