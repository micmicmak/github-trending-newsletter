# scraper.py
import requests
from bs4 import BeautifulSoup

# def get_trending_repos(top_n=10): # Original line
def get_trending_repos(top_n=10, time_range="weekly"): # Modified line to accept time_range
    # url = "https://github.com/trending" # Original line
    url = f"https://github.com/trending?since={time_range}" # MODIFIED LINE
    
    # You can also specify a language if desired, e.g.:
    # language_path = "/python" # or "/javascript", etc. or "" for all languages
    # url = f"https://github.com/trending{language_path}?since={time_range}"

    headers = {
        "User-Agent": "GitHubTrendingNewsletter/1.0 (YourGitHubUsername; YourEmailOrProjectURL)"
    }
    try:
        print(f"Fetching trending repositories from: {url}") # Good to log the URL
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status() # Raise an exception for HTTP errors
    except requests.RequestException as e:
        print(f"Error fetching trending page: {e}")
        return []

    soup = BeautifulSoup(response.content, "lxml") # or 'html.parser'
    repos_data = []

    # ... (rest of your scraping logic remains the same) ...
    # GitHub's HTML structure can change. Inspect the page to find the correct selectors.
    # This is a common structure, but VERIFY IT.
    repo_articles = soup.find_all("article", class_="Box-row")

    for article in repo_articles[:top_n]:
        try:
            h2_tag = article.find("h2", class_="h3 lh-condensed")
            if not h2_tag or not h2_tag.a:
                continue
            repo_link_tag = h2_tag.a
            # The repo name might contain spaces if it's like "user / repo name"
            # Let's adjust the stripping to be more robust
            repo_name_parts = [part.strip() for part in repo_link_tag.text.split('/')]
            repo_name_full = " / ".join(repo_name_parts).replace("\n", "").strip()

            repo_url = "https://github.com" + repo_link_tag["href"]

            description_tag = article.find("p", class_="col-9 color-fg-muted my-1 pr-4")
            description = description_tag.text.strip() if description_tag else "No description."

            # Language
            lang_span = article.find("span", itemprop="programmingLanguage")
            language = lang_span.text.strip() if lang_span else "N/A"

            # Stars and Forks
            # Selectors for stars and forks need to be robust.
            # Example: <a href="/user/repo/stargazers" class="Link Link--muted d-inline-block mr-3">
            #           <svg>...</svg> 1,234 </a>
            # The text includes the icon, so we need to be careful.
            
            # General approach for stars/forks: find all link tags that are siblings of the description or part of the metadata div
            meta_tags = article.find_all("a", class_="Link--muted")
            stars = "N/A"
            forks = "N/A"

            for tag in meta_tags:
                href = tag.get("href", "")
                if "/stargazers" in href:
                    stars = tag.text.strip().split()[0] # Take the first part, e.g., "1,234" from "1,234 stars"
                elif "/forks" in href: # GitHub might use /network/members or similar for forks
                    forks = tag.text.strip().split()[0]

            # Stars today (often in a span like <span class="d-inline-block float-sm-right">)
            stars_today_tag = article.find("span", class_="d-inline-block float-sm-right")
            # The text is usually like "123 stars this week"
            stars_today_text = stars_today_tag.text.strip() if stars_today_tag else ""
            stars_today = "N/A"
            if "stars this week" in stars_today_text: # Adjust if the text changes for weekly
                stars_today = stars_today_text.split()[0]
            elif "stars today" in stars_today_text: # Fallback for daily if selector is the same
                 stars_today = stars_today_text.split()[0]


            repos_data.append({
                "name": repo_name_full,
                "url": repo_url,
                "description": description,
                "language": language,
                "stars": stars,
                "forks": forks,
                "stars_today": stars_today # This field might represent "stars this week" now
            })
        except Exception as e:
            print(f"Error parsing a repository entry: {e}")
            # Consider logging the problematic HTML snippet for debugging
            # print(f"Problematic article HTML: {article.prettify()}")
            continue # Skip this repo if parsing fails
            
    return repos_data

if __name__ == "__main__":
    # Test with weekly
    print("--- Weekly Trending Repos ---")
    trending_weekly = get_trending_repos(time_range="weekly")
    for i, repo in enumerate(trending_weekly):
        print(f"{i+1}. {repo['name']} - Stars this week: {repo['stars_today']}")

    # Test with daily (optional)
    # print("\n--- Daily Trending Repos ---")
    # trending_daily = get_trending_repos(time_range="daily")
    # for repo in trending_daily:
    # print(repo)