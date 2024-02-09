# Copyright 2023-2024 ByteBrain AI
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
