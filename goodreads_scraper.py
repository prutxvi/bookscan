import requests
from bs4 import BeautifulSoup
import time
import html


def _unique_preserve_order(seq):
    seen = set()
    out = []
    for s in seq:
        if s not in seen:
            seen.add(s)
            out.append(s)
    return out


def fetch_goodreads_reviews(book_title, max_reviews=5):
    """
    Searches Goodreads, finds the first book result, and scrapes user reviews.
    Uses multiple selectors and a heuristic fallback that looks for long text
    blocks on the page to handle changes in Goodreads markup.
    Returns a list of review strings (may be empty).
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://www.goodreads.com/'
    }
    search_url = "https://www.goodreads.com/search"

    try:
        # Search for book (use params to let requests handle encoding)
        res = requests.get(search_url, params={'q': book_title}, headers=headers, timeout=10)
        soup = BeautifulSoup(res.content, 'html.parser')
        book_link = soup.select_one("a.bookTitle") or soup.select_one("a[href*='/book/show/']")
        if not book_link:
            print("No book link found on search results for:", book_title)
            return []

        book_page = "https://www.goodreads.com" + book_link['href']
        print(f"Book page: {book_page}")

        # Fetch book detail page
        res = requests.get(book_page, headers=headers, timeout=10)
        soup = BeautifulSoup(res.content, 'html.parser')

        # Print short HTML preview to help diagnose (trimmed)
        print("\n---- PAGE HTML PREVIEW ----")
        preview = soup.prettify()[:2000]
        print(preview)
        print("\n---- END PREVIEW ----")

        reviews = []

        # 1) Try known selectors (legacy and newer)
        selectors = [
            "div.reviewText span.readable span",
            "span.Formatted",
            "div.ReviewText__content",
            "div.review:nth-of-type(n)",
            "div.reviewText",
        ]
        for sel in selectors:
            for rev in soup.select(sel):
                text = rev.get_text(" ", strip=True)
                text = html.unescape(text)
                if len(text) > 40:
                    reviews.append(text)
                if len(reviews) >= max_reviews:
                    return _unique_preserve_order(reviews)[:max_reviews]

        # 2) Look for elements with data-testid attributes commonly used in newer markup
        for tag in soup.find_all(attrs={"data-testid": True}):
            if 'review' in tag['data-testid'].lower() or 'content' in tag['data-testid'].lower():
                text = tag.get_text(" ", strip=True)
                text = html.unescape(text)
                if len(text) > 40:
                    reviews.append(text)
                if len(reviews) >= max_reviews:
                    return _unique_preserve_order(reviews)[:max_reviews]

        # 3) Heuristic fallback: scan for long text blocks in common tags
        candidates = []
        for tag in soup.find_all(['div', 'span', 'p']):
            # skip nav/header/footer-ish sections by checking for very small tags or script/style
            if tag.name in ('script', 'style'):
                continue
            text = tag.get_text(" ", strip=True)
            if not text:
                continue
            # Exclude short snippets and lines that are clearly not reviews
            if len(text) < 80:
                continue
            low = text.lower()
            if any(low.startswith(prefix) for prefix in ['about the author', 'also by', 'read more']):
                continue
            # Filter out repeated site chrome
            if 'goodreads' in low and len(text) < 200:
                continue
            candidates.append(html.unescape(text))

        # Deduplicate and return the top long candidates
        candidates = _unique_preserve_order(candidates)
        if candidates:
            return candidates[:max_reviews]

        # If all else fails, return whatever longer texts we could find from paragraphs
        alt = []
        for p in soup.find_all('p'):
            text = p.get_text(" ", strip=True)
            if len(text) > 60:
                alt.append(html.unescape(text))
            if len(alt) >= max_reviews:
                break
        return _unique_preserve_order(alt)[:max_reviews]

    except Exception as e:
        print(f"Error scraping Goodreads: {e}")
        return []
