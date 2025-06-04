# main.py
import os
import scraper
import formatter
import emailer
import datetime

def run_newsletter_service():
    print("Starting GitHub Trending Newsletter service...")

    # 1. Load configuration
    config = emailer.load_config()
    if not config:
        print("Failed to load configuration. Exiting.")
        return

    # 2. Scrape trending repositories
    print("Fetching trending repositories...")
    trending_repos = scraper.get_trending_repos(top_n=10)
    if not trending_repos:
        print("No trending repositories found or error in scraping. Exiting.")
        return
    print(f"Successfully fetched {len(trending_repos)} repositories.")

    # 3. Format results into HTML
    print("Formatting email content...")
    html_email_body = formatter.format_html(trending_repos)

    # 4. Send email
    subscribers = os.environ.get('SUBSCRIBERS')
    if not subscribers:
        print("Error: SUBSCRIBERS environment variable not set. Exiting")
        return

    subscribers = [subscriber.strip() for subscriber in subscribers.split(",")]
    print(f"Sending email to {len(subscribers)} subscribers...")
    subject = f"GitHub Trending Repositories - {datetime.date.today().strftime('%Y-%m-%d')}"
    success = emailer.send_email(subject, html_email_body, subscribers, config)

    if success:
        print("Newsletter sent successfully!")
    else:
        print("Failed to send newsletter.")

    print("GitHub Trending Newsletter service finished.")

if __name__ == "__main__":
    run_newsletter_service()