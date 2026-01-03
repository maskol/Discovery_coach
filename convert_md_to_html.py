#!/usr/bin/env python3
"""Convert markdown to formatted HTML for printing"""

import markdown2
import sys
from pathlib import Path


def convert_md_to_html(md_file: str, output_file: str = None):
    """Convert markdown file to HTML with nice styling"""

    # Read markdown file
    md_content = Path(md_file).read_text()

    # Convert to HTML with extras
    html_content = markdown2.markdown(
        md_content,
        extras=[
            "fenced-code-blocks",
            "tables",
            "header-ids",
            "toc",
            "break-on-newline",
            "code-friendly",
        ],
    )

    # Add CSS styling for print
    full_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>AI Architecture Review</title>
    <style>
        @media print {{
            body {{ margin: 1cm; }}
            code {{ page-break-inside: avoid; }}
            pre {{ page-break-inside: avoid; }}
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
            line-height: 1.6;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            color: #24292e;
        }}
        
        h1 {{
            border-bottom: 2px solid #eaecef;
            padding-bottom: 0.3em;
            font-size: 2em;
            margin-top: 24px;
            margin-bottom: 16px;
        }}
        
        h2 {{
            border-bottom: 1px solid #eaecef;
            padding-bottom: 0.3em;
            font-size: 1.5em;
            margin-top: 24px;
            margin-bottom: 16px;
        }}
        
        h3 {{
            font-size: 1.25em;
            margin-top: 24px;
            margin-bottom: 16px;
        }}
        
        code {{
            background-color: rgba(27, 31, 35, 0.05);
            border-radius: 3px;
            font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
            font-size: 85%;
            padding: 0.2em 0.4em;
        }}
        
        pre {{
            background-color: #f6f8fa;
            border-radius: 3px;
            font-size: 85%;
            line-height: 1.45;
            overflow: auto;
            padding: 16px;
        }}
        
        pre code {{
            background-color: transparent;
            border: 0;
            display: inline;
            line-height: inherit;
            margin: 0;
            overflow: visible;
            padding: 0;
            word-wrap: normal;
        }}
        
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 16px 0;
        }}
        
        table th, table td {{
            border: 1px solid #dfe2e5;
            padding: 6px 13px;
        }}
        
        table tr:nth-child(2n) {{
            background-color: #f6f8fa;
        }}
        
        table th {{
            background-color: #f6f8fa;
            font-weight: 600;
        }}
        
        blockquote {{
            border-left: 0.25em solid #dfe2e5;
            color: #6a737d;
            padding: 0 1em;
            margin: 0;
        }}
        
        a {{
            color: #0366d6;
            text-decoration: none;
        }}
        
        a:hover {{
            text-decoration: underline;
        }}
        
        hr {{
            border: 0;
            border-top: 2px solid #eaecef;
            margin: 24px 0;
        }}
    </style>
</head>
<body>
{html_content}
</body>
</html>"""

    # Determine output file
    if output_file is None:
        output_file = Path(md_file).with_suffix(".html")

    # Write HTML file
    Path(output_file).write_text(full_html)
    print(f"✓ Converted {md_file} → {output_file}")
    print(f"✓ Open {output_file} in your browser and press Cmd+P to print")

    return output_file


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python convert_md_to_html.py <markdown_file> [output_file]")
        sys.exit(1)

    md_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    convert_md_to_html(md_file, output_file)
