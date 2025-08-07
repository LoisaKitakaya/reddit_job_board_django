import praw
import datetime
from google import genai
from posts.models import Post
from django.conf import settings
from celery import shared_task


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

    current_time = datetime.datetime.now(datetime.timezone.utc).timestamp()
    one_day_ago = current_time - 86400

    for target_sub in TARGET_SUBS:
        subreddit = reddit.subreddit(target_sub)

        try:
            for submission in subreddit.new(limit=posts_limit):
                if submission.created_utc < one_day_ago:
                    continue

                title = submission.title

                for offer_trigger in OFFER_TRIGGER_PHRASES:
                    if offer_trigger in title:
                        Post.objects.create(
                            post_owner_reddit_username=(
                                submission.author.name if submission.author else "N/A"
                            ),
                            reddit_post_id=submission.id,
                            post_url=submission.url,
                            post_title=title,
                            post_category=categorize_title(title),
                            post_trigger="offer",
                            subreddit=subreddit.display_name,
                            post_time=datetime.datetime.fromtimestamp(
                                submission.created_utc, tz=datetime.timezone.utc
                            ).strftime("%Y-%m-%d %H:%M:%S"),
                        )

                        break

                for task_trigger in TASK_TRIGGER_PHRASES:
                    if task_trigger in title:
                        Post.objects.create(
                            post_owner_reddit_username=(
                                submission.author.name if submission.author else "N/A"
                            ),
                            reddit_post_id=submission.id,
                            post_url=submission.url,
                            post_title=title,
                            post_category=categorize_title(title),
                            post_trigger="task",
                            subreddit=subreddit.display_name,
                            post_time=datetime.datetime.fromtimestamp(
                                submission.created_utc, tz=datetime.timezone.utc
                            ).strftime("%Y-%m-%d %H:%M:%S"),
                        )

                        break

        except Exception as e:
            raise Exception(f"Error processing subreddit {subreddit.display_name}: {e}")
