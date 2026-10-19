#!/usr/bin/env python3
"""
Reusable HTML text extraction script for web research.
Write to /tmp/extract.py at session start, then pipe every curl call through it.

Usage:
    curl -sL -H 'User-Agent: Mozilla/5.0 ...' 'URL' | python3 /tmp/extract.py
    curl -sL -H 'User-Agent: Mozilla/5.0 ...' 'URL2' | python3 /tmp/extract.py

Optional: pass a keyword to search for and print from that offset:
    curl ... | python3 /tmp/extract.py --find "Marshall"
"""
import sys
from html.parser import HTMLParser

class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text = []
        self.skip = False

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript"):
            self.skip = True

    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript"):
            self.skip = False

    def handle_data(self, d):
        if not self.skip:
            s = d.strip()
            if s:
                self.text.append(s)

    def get_text(self):
        return " ".join(self.text)


def main():
    p = TextExtractor()
    html_content = sys.stdin.read()
    p.feed(html_content)
    text = p.get_text()

    # Optional: search for a keyword and print from that offset
    if "--find" in sys.argv:
        idx = sys.argv.index("--find")
        if idx + 1 < len(sys.argv):
            keyword = sys.argv[idx + 1]
            pos = text.lower().find(keyword.lower())
            if pos >= 0:
                start = max(0, pos - 200)
                print(text[start:start + 8000])
            else:
                print(f'Keyword "{keyword}" not found. First 3000 chars:')
                print(text[:3000])
    else:
        print(text[:8000])


if __name__ == "__main__":
    main()
