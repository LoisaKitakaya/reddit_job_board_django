import uuid
from posts.models import Post
from django.test import TestCase
from ninja.testing import TestClient
from posts.api.rest.api import router
from api.rest.api import api
from datetime import datetime, timezone

# Create your tests here.


class BackendTests(TestCase):
    def setUp(self) -> None:
        self.now = datetime.now(tz=timezone.utc)

        Post.objects.create(
            reddit_post_id="1msnn0n",
            post_title="[Hiring] Photoshop Pros Wanted – $45/hr – Remote 🎨",
            post_url="https://www.reddit.com/r/forhire/comments/1msnn0n/hiring_photoshop_pros_wanted_45hr_remote/",
            post_owner_reddit_username="roxyygaming",
            subreddit="forhire",
            post_category="Photography & Image Editing",
            desired_skills="Tools: Adobe Photoshop, Post-processing skills, Proficiency in visual composition and color theory, Digital design principles, Understanding of file formats and resolution",
            post_trigger="task",
            post_time=self.now,
        )

    def tearDown(self) -> None:
        self.now = None

    def test_api_endpoint(self):
        client = TestClient(router)

        response = client.get("/reddit_posts")

        self.assertEqual(response.status_code, 200)

        for data in response.json()["posts"]:
            self.assertEqual(
                type(data["id"]),
                str,
            )

            self.assertEqual(
                data["reddit_post_id"],
                "1msnn0n",
            )

            self.assertEqual(
                data["post_title"],
                "[Hiring] Photoshop Pros Wanted – $45/hr – Remote 🎨",
            )

            self.assertEqual(
                data["post_url"],
                "https://www.reddit.com/r/forhire/comments/1msnn0n/hiring_photoshop_pros_wanted_45hr_remote/",
            )

            self.assertEqual(
                data["post_owner_reddit_username"],
                "roxyygaming",
            )

            self.assertEqual(
                data["subreddit"],
                "forhire",
            )

            self.assertEqual(
                data["post_category"],
                "Photography & Image Editing",
            )

            self.assertEqual(
                data["desired_skills"],
                "Tools: Adobe Photoshop, Post-processing skills, Proficiency in visual composition and color theory, Digital design principles, Understanding of file formats and resolution",
            )

            self.assertEqual(
                data["post_trigger"],
                "task",
            )

            formatted_time = f"{self.now.strftime('%Y-%m-%dT%H:%M:%S')}.{self.now.microsecond // 1000:03d}Z"  # type: ignore

            self.assertEqual(data["post_time"], formatted_time)
