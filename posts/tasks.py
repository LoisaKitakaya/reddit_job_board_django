import praw
import datetime
from google import genai
from posts.models import Post
from celery import shared_task
from django.conf import settings
from django.utils import timezone
from django.db import IntegrityError
from datetime import datetime, timedelta


TARGET_SUBS = [
    "slavelabour",
    "WebDeveloperJobs",
    "WebDevJobs",
    "DeveloperJobs",
    "forhire",
    "freelance_forhire",
    "programmers_forhire",
    "DoneDirtCheap",
    "VirtualAssistant",
    "B2BForHire",
    "jobbit",
    "remotedaily",
    "PythonJobs",
    "remotejs",
    "CodingJobs",
    "remotepython",
]

OFFER_TRIGGER_PHRASES = [
    "[OFFER]",
    "[Offer]",
    "[offer]",
    "[FOR HIRE]",
    "[For Hire]",
    "[For hire]",
    "[for hire]",
]

TASK_TRIGGER_PHRASES = [
    "[TASK]",
    "[Task]",
    "[task]",
    "[HIRING]",
    "[Hiring]",
    "[hiring]",
]

JOB_CATEGORIES = """
Example of job categories:

Social Media Management & Digital Marketing

Web & Mobile Development

Graphic Design & Visual Arts

Video Editing & Multimedia Production

Virtual Assistance & Administrative Support

Content Writing & Editorial Services

Sales, Outreach & Business Development

Software Development & Technical Support

Gaming & Interactive Media

Miscellaneous Freelance Services
"""


def categorize_title(title: str) -> str:
    client = genai.Client(api_key=settings.GEMINI_API_KEY)

    prompt = f"Here is a job title: {title}. Here is a list of job categories: {JOB_CATEGORIES}. Based on the job title, from the provided list, pick a fitting category for the job or offer being made. Return only the category you have settled on. NOTE: if the provided categories do not match the title, generate a new category, however, prioritize using only the provided categories."

    try:
        response = client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=prompt,
        )

        return response.text.strip()  # type: ignore
    except Exception as e:
        return "Uncategorized"


@shared_task
def generate_leads(posts_limit: int = 10):
    reddit = praw.Reddit(
        client_id=settings.CLIENT_ID,
        client_secret=settings.CLIENT_SECRET,
        refresh_token=settings.REFRESH_TOKEN,
        user_agent=settings.USER_AGENT,
    )

    current_time = timezone.now()
    one_day_ago = current_time - timedelta(days=1)

    print("=" * 50)
    print("🚀 Starting Reddit Leads Generation...")
    print("=" * 50)

    for target_sub in TARGET_SUBS:
        subreddit = reddit.subreddit(target_sub)

        print(f"📥 Compiling from: {subreddit.display_name}")

        try:
            for submission in subreddit.new(limit=posts_limit):
                if submission.created_utc < one_day_ago.timestamp():
                    continue

                title = submission.title

                post_trigger = None

                for trigger in OFFER_TRIGGER_PHRASES:
                    if trigger in title:
                        post_trigger = Post.OFFER

                        break

                for trigger in TASK_TRIGGER_PHRASES:
                    if trigger in title:
                        post_trigger = Post.TASK

                        break

                if not post_trigger:
                    continue

                post_time = timezone.make_aware(
                    datetime.fromtimestamp(submission.created_utc),
                    timezone=timezone.get_fixed_timezone(0),
                )

                post_data = {
                    "post_owner_reddit_username": (
                        submission.author.name if submission.author else "N/A"
                    ),
                    "reddit_post_id": submission.id,
                    "post_url": submission.url,
                    "post_title": title,
                    "post_category": categorize_title(title),
                    "post_trigger": post_trigger,
                    "subreddit": subreddit.display_name,
                    "post_time": post_time,
                }

                post_exitsts = Post.objects.filter(
                    reddit_post_id=submission.id
                ).exists()

                try:
                    if not post_exitsts:

                        Post.objects.create(**post_data)

                        print(
                            f"{'Created' if post_exitsts else 'Skipped'} post: {submission.id}, title: {title}"
                        )

                except IntegrityError as e:
                    raise Exception(
                        f"Error saving lead/post for {submission.author.name if submission.author else "N/A"}: {e}"
                    )

        except Exception as e:
            raise Exception(
                f"Error processing subreddit {subreddit.display_name}: {e}"
            )



@shared_task
def delete_old_posts():
    one_week_ago = timezone.now() - timedelta(days=7)

    Post.objects.filter(post_time__lt=one_week_ago).delete()
