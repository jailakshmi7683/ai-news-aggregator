from datetime import datetime, timedelta, timezone
from typing import Optional
import feedparser
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
from app.services.youtube import get_transcript


def get_rss_url(channel_id: str) -> str:
    return f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"


def extract_video_id(video_url: str) -> str:
    if "youtube.com/watch?v=" in video_url:
        return video_url.split("v=")[1].split("&")[0]
    if "youtu.be/" in video_url:
        return video_url.split("youtu.be/")[1].split("?")[0]
    return video_url


def get_latest_videos(channel_id: str, hours: int = 24) -> list[dict]:
    feed = feedparser.parse(get_rss_url(channel_id))
    if not feed.entries:
        return []

    cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
    videos = []

    for entry in feed.entries:
        published_time = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
        if published_time >= cutoff_time:
            video_id = extract_video_id(entry.link)
            videos.append({
                "title": entry.title,
                "url": entry.link,
                "video_id": video_id,
                "published_at": published_time,
                "description": entry.get("summary", ""),
            })

    return videos


def scrape_channel(channel_id: str, hours: int = 150) -> list[dict]:
    videos = get_latest_videos(channel_id, hours)
    for video in videos:
        video["transcript"] = get_transcript(video["video_id"])
    return videos


if __name__ == "__main__":
    #videos = get_latest_videos(channel_id="UCn8ujwUInbJkBhffxqAPBVQ", hours=24*9) #creator ID
    # videos = get_latest_videos(channel_id="UCBwmMxybNva6P_5VmxjzwqA", hours=24*9) #APNA COLLEGE
    # print(videos);
    videos = scrape_channel(channel_id="UCBwmMxybNva6P_5VmxjzwqA", hours=24)
    for v in videos:
        print(v["published_at"].date(), v["title"])
        print("  transcript chars:", len(v["transcript"]) if v["transcript"] else 0)