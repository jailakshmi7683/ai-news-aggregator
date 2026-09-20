from typing import Optional
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import NoTranscriptFound


def get_transcript(video_id: str) -> Optional[str]:
    api = YouTubeTranscriptApi()
    try:
        return " ".join(s.text for s in api.fetch(video_id))
    except NoTranscriptFound:
        # no English track: use the first available one (e.g. auto-generated Hindi)
        try:
            transcript = next(iter(api.list(video_id)))
            return " ".join(s.text for s in transcript.fetch())
        except Exception as e:
            print(f"Transcript error for {video_id}: {type(e).__name__}")
            return None
    except Exception as e:
        print(f"Transcript error for {video_id}: {type(e).__name__}")
        return None

if __name__ == "__main__":
    # print(get_transcript("jqd6_bbjhS8"))
    print(get_transcript("E8zpgNPx8jE"))
