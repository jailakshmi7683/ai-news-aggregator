from datetime import datetime, timedelta, timezone
from typing import Optional

import feedparser
from pydantic import BaseModel
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import NoTranscriptFound


class Transcript(BaseModel):
    text: str


class ChannelVideo(BaseModel):
    title: str
    url: str
    video_id: str
    published_at: datetime
    description: str = ""
    transcript: Optional[str] = None


class YouTubeScraper:
    def __init__(self):
        self.transcript_api = YouTubeTranscriptApi()

    def _get_rss_url(self, channel_id: str) -> str:
        return f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"

    def _extract_video_id(self, video_url: str) -> str:
        if "youtube.com/watch?v=" in video_url:
            return video_url.split("v=")[1].split("&")[0]
        if "youtu.be/" in video_url:
            return video_url.split("youtu.be/")[1].split("?")[0]
        if "/shorts/" in video_url:
            return video_url.split("/shorts/")[1].split("?")[0]
        return video_url

    def get_transcript(self, video_id: str) -> Optional[Transcript]:
        try:
            fetched = self.transcript_api.fetch(video_id)
            return Transcript(text=" ".join(s.text for s in fetched.snippets))
        except NoTranscriptFound:
            # no English track: fall back to the first available language
            try:
                first = next(iter(self.transcript_api.list(video_id)))
                return Transcript(text=" ".join(s.text for s in first.fetch().snippets))
            except Exception as e:
                print(f"Transcript error for {video_id}: {type(e).__name__}")
                return None
        except Exception as e:
            print(f"Transcript error for {video_id}: {type(e).__name__}")
            return None

    def get_latest_videos(self, channel_id: str, hours: int = 24) -> list[ChannelVideo]:
        feed = feedparser.parse(self._get_rss_url(channel_id))
        if not feed.entries:
            return []

        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        videos = []

        for entry in feed.entries:
            if "/shorts/" in entry.link:
                continue

            published_time = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
            if published_time >= cutoff_time:
                videos.append(
                    ChannelVideo(
                        title=entry.title,
                        url=entry.link,
                        video_id=self._extract_video_id(entry.link),
                        published_at=published_time,
                        description=entry.get("summary", ""),
                    )
                )

        return videos

    def scrape_channel(self, channel_id: str, hours: int = 150) -> list[ChannelVideo]:
        videos = self.get_latest_videos(channel_id, hours)
        for video in videos:
            transcript = self.get_transcript(video.video_id)
            video.transcript = transcript.text if transcript else None
        return videos


if __name__ == "__main__":
    scraper = YouTubeScraper()

    transcript = scraper.get_transcript("Shqtk_2Jd3c")
    print("transcript chars:", len(transcript.text) if transcript else 0)
    # print(transcript.text)

    for v in scraper.scrape_channel("UCn8ujwUInbJkBhffxqAPBVQ", hours=24 * 10):
        print(v.published_at.date(), v.title)
        print("  transcript chars:", len(v.transcript) if v.transcript else 0)