from typing import Optional

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.agent.digest_agent import DigestAgent
from app.database.repository import Repository


def process_digests(limit: Optional[int] = None) -> dict:
    agent = DigestAgent()
    repo = Repository()

    articles = repo.get_articles_without_digest(limit=limit)
    processed = 0
    failed = 0

    for article in articles:
        try:
            digest_result = agent.generate_digest(
                title=article["title"],
                content=article["content"],
                article_type=article["type"]
            )

            if digest_result:
                repo.create_digest(
                    article_type=article["type"],
                    article_id=article["id"],
                    url=article["url"],
                    title=digest_result.title,
                    summary=digest_result.summary
                )
                processed += 1
            else:
                failed += 1
        except Exception as e:
            failed += 1
            print(f"Error processing {article['type']} article {article['id']}: {e}")

    return {
        "total": len(articles),
        "processed": processed,
        "failed": failed
    }


if __name__ == "__main__":
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else None
    result = process_digests(limit=limit)
    print(f"Total articles: {result['total']}")
    print(f"Processed: {result['processed']}")
    print(f"Failed: {result['failed']}")