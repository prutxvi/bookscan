import requests
from bs4 import BeautifulSoup
import time

def fetch_goodreads_reviews(book_title, max_reviews=5):
    """
    Searches Goodreads, gets first relevant book result, scrapes user reviews.
    More robust selectors & debug prints for troubleshooting.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    search_url = f"https://www.goodreads.com/search?q={book_title.replace(' ', '+')}"

    try:
        # Search for book
        res = requests.get(search_url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.content, 'html.parser')
        book_link = soup.select_one("a.bookTitle")
        if not book_link:
            print("No book link found.")
            return []

        book_page = "https://www.goodreads.com" + book_link['href']
        print(f"Book page: {book_page}")

        # Fetch book detail page
        res = requests.get(book_page, headers=headers, timeout=10)
        soup = BeautifulSoup(res.content, 'html.parser')

        # Print first 2000 chars of HTML to help diagnose
        print("\n---- PAGE HTML PREVIEW ----")
        print(soup.prettify()[:2000])
        print("\n---- END PREVIEW ----")

        reviews = []
        # Try the old and new selectors
        # 1. Old container
        for rev in soup.select("div.reviewText span.readable span"):
            text = rev.get_text(strip=True)
            if len(text) > 40:
                reviews.append(text)
            if len(reviews) >= max_reviews:
                return reviews

        # 2. Newer Goodreads (sometimes)
        if not reviews:
            for rev in soup.select("span.Formatted"):
                text = rev.get_text(strip=True)
                if len(text) > 40:
                    reviews.append(text)
                if len(reviews) >= max_reviews:
                    return reviews

        # 3. Even newer (try this if others fail, actual selector may vary)
        if not reviews:
            for rev in soup.select("div.ReviewText__content"):
                text = rev.get_text(strip=True)
                if len(text) > 40:
                    reviews.append(text)
                if len(reviews) >= max_reviews:
                    return reviews

        return reviews

    except Exception as e:
        print(f"Error scraping Goodreads: {e}")
        return []
