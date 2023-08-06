import requests
from bs4 import BeautifulSoup


def crawl_website(url):
    visited_urls = set()

    def crawl(url):
        response = requests.get(url)
        html_content = response.content

        soup = BeautifulSoup(html_content, "html.parser")

        # Extract all URLs from the page
        all_urls = set()
        for tag in soup.find_all(["a"]):
            href = tag.get("href")
            if href and href.startswith("/"):
                all_urls.add(f"https://zio.dev{href}")

        # Process the URLs as needed
        for new_url in all_urls:
            if new_url not in visited_urls:
                visited_urls.add(new_url)
                print(new_url)
                crawl(new_url)

    crawl(url)


def main():
    crawl_website("https://zio.dev")
