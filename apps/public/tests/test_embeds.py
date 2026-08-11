from django.test import SimpleTestCase

from apps.public.embeds import is_external_audio_url, youtube_embed_src, youtube_video_id


class YoutubeEmbedHelperTests(SimpleTestCase):
    def test_watch_url_becomes_nocookie_embed_without_autoplay(self):
        src = youtube_embed_src("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        self.assertEqual(
            src,
            "https://www.youtube-nocookie.com/embed/dQw4w9WgXcQ?rel=0",
        )
        self.assertNotIn("autoplay", src)

    def test_short_embed_and_live_urls_resolve_same_id(self):
        self.assertEqual(youtube_video_id("https://youtu.be/dQw4w9WgXcQ"), "dQw4w9WgXcQ")
        self.assertEqual(
            youtube_video_id("https://www.youtube.com/embed/dQw4w9WgXcQ"),
            "dQw4w9WgXcQ",
        )
        self.assertEqual(
            youtube_video_id("https://www.youtube.com/live/dQw4w9WgXcQ"),
            "dQw4w9WgXcQ",
        )

    def test_non_youtube_url_returns_empty(self):
        self.assertEqual(youtube_embed_src("https://example.com/video.mp4"), "")
        self.assertEqual(youtube_embed_src(""), "")

    def test_external_audio_url_detection(self):
        self.assertTrue(is_external_audio_url("https://cdn.example.com/a.mp3"))
        self.assertFalse(is_external_audio_url("https://cdn.example.com/a.mp4"))
        self.assertFalse(is_external_audio_url(""))
