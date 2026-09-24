import sys
from pathlib import Path
from typing import Optional

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.database.repository import Repository
from app.scrapers.anthropic_news import AnthropicScraper


def process_anthropic_markdown(limit: Optional[int] = None) -> dict:
    scraper = AnthropicScraper()
    repo = Repository()

    articles = repo.get_anthropic_articles_without_markdown(limit=limit)
    processed = 0
    failed = 0

    for article in articles:
        guid = article.guid
        try:
            markdown = scraper.url_to_markdown(article.url)
            if markdown:
                repo.update_anthropic_article_markdown(guid, markdown)
                processed += 1
            else:
                failed += 1
        except Exception as e:
            repo.session.rollback()
            failed += 1
            print(f"Error processing {guid}: {e}")
            continue

    return {
        "total": len(articles),
        "processed": processed,
        "failed": failed,
    }


if __name__ == "__main__":
    print(process_anthropic_markdown())