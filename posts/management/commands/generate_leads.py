import praw
import datetime
from google import genai
from posts.models import Post
from django.conf import settings
from django.utils import timezone
from django.db import IntegrityError
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand


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
Freelance Job Categories

A comprehensive list of common freelance job categories, along with examples of specific job types within each.

- Writing & Content Creation
  - Blog writing
  - Copywriting
  - Technical writing
  - Ghostwriting
  - Content editing
  - SEO writing
  - Social media content
  - Scriptwriting
  - Proofreading

- Graphic Design & Illustration
  - Logo design
  - Brochure design
  - Web graphics
  - Illustration
  - Infographics
  - Book covers
  - Packaging design
  - UI/UX design

- Web Development
  - Front-end development (HTML/CSS/JS)
  - Back-end development (PHP/Node.js)
  - Full-stack development
  - WordPress customization
  - E-commerce site building
  - API integration

- Programming & Software Development
  - Mobile app development (iOS/Android)
  - Custom software scripting
  - Database management
  - Game development
  - Automation scripts
  - AI/ML model building

- Digital Marketing
  - SEO optimization
  - Social media management
  - Email marketing
  - PPC advertising (Google Ads/Facebook Ads)
  - Content marketing strategy
  - Influencer outreach

- Video & Animation
  - Video editing
  - Animation (2D/3D)
  - Motion graphics
  - Explainer videos
  - YouTube editing
  - Drone footage editing
  - Voiceover integration

- Audio Production
  - Music composition
  - Sound editing
  - Podcast production
  - Voiceover recording
  - Audio mixing/mastering
  - Jingle creation

- Virtual Assistance
  - Administrative support
  - Email management
  - Scheduling
  - Data entry
  - Research
  - Customer service
  - Travel planning

- Translation & Localization
  - Document translation
  - Website localization
  - Subtitling
  - Transcription
  - Multilingual SEO

- Consulting & Business Services
  - Business plan writing
  - Financial consulting
  - HR advice
  - Market research
  - Legal consulting
  - Project management

- Photography & Image Editing
  - Product photography
  - Event photography
  - Photo retouching
  - Stock image creation
  - Portrait editing

- Sales & Lead Generation
  - Cold calling
  - Email outreach
  - CRM management
  - Sales funnel setup
  - Lead qualification

- Engineering & Architecture
  - CAD drafting
  - 3D modeling
  - Structural engineering
  - Architectural design
  - Electrical schematics

- Data Science & Analytics
  - Data analysis
  - Visualization (Tableau/Power BI)
  - Machine learning modeling
  - Statistical reporting
  - Big data processing

- Teaching & Tutoring
  - Online tutoring (subjects like math, languages)
  - Course creation
  - Exam preparation
  - Skill workshops (e.g., coding bootcamps)
"""

JOB_SKILLS = f"""
Freelance Job Categories

A comprehensive list of common freelance job categories, along with examples of required skills and tools for jobs within each.

- Writing & Content Creation
  - Strong command of language and grammar
  - Research and fact-checking abilities
  - SEO and keyword optimization knowledge
  - Creativity in storytelling and persuasion
  - Tools: Microsoft Word, Google Docs, Grammarly, WordPress, Hemingway App

- Graphic Design & Illustration
  - Proficiency in visual composition and color theory
  - Drawing and illustration skills
  - Understanding of typography and branding
  - Digital design principles
  - Tools: Adobe Photoshop, Illustrator, InDesign, Canva, Figma

- Web Development
  - Knowledge of HTML, CSS, and JavaScript
  - Front-end frameworks like React or Vue.js
  - Back-end languages such as PHP, Python or Node.js
  - Responsive and mobile-first design
  - Tools: Visual Studio Code, Git, Chrome DevTools, Bootstrap

- Programming & Software Development
  - Proficiency in languages like Python, Java, or C++
  - Algorithm and data structure knowledge
  - Debugging and problem-solving skills
  - Version control systems
  - Tools: IDEs (PyCharm, IntelliJ), GitHub, Jupyter Notebook

- Digital Marketing
  - SEO and SEM strategies
  - Social media platform expertise
  - Content marketing and analytics
  - Email campaign management
  - Tools: Google Analytics, Google Ads, Hootsuite, Mailchimp, Ahrefs

- Video & Animation
  - Video editing and sequencing skills
  - Animation principles (timing, motion)
  - Storyboarding and scripting
  - Knowledge of video formats and resolutions
  - Tools: Adobe Premiere Pro, After Effects, Final Cut Pro, Blender

- Audio Production
  - Sound editing and mixing techniques
  - Music theory and composition
  - Recording and microphone handling
  - Mastering and audio effects
  - Tools: Adobe Audition, Logic Pro, Audacity, GarageBand

- Virtual Assistance
  - Organizational and time management skills
  - Strong communication and interpersonal abilities
  - Basic administrative knowledge
  - Research and data entry proficiency
  - Tools: Microsoft Office Suite, Google Workspace, Trello, Asana, Slack

- Translation & Localization
  - Fluency in multiple languages
  - Cultural nuance and context understanding
  - Terminology management
  - Proofreading in target languages
  - Tools: SDL Trados, MemoQ, Google Translate (for reference), OmegaT

- Consulting & Business Services
  - Industry-specific expertise
  - Analytical and strategic thinking
  - Report writing and presentation skills
  - Project management
  - Tools: Microsoft Excel, PowerPoint, Zoom, CRM software like Salesforce

- Photography & Image Editing
  - Composition and lighting techniques
  - Camera operation and settings knowledge
  - Post-processing skills
  - Understanding of file formats and resolution
  - Tools: Adobe Lightroom, Photoshop, DSLR cameras, GIMP

- Sales & Lead Generation
  - Persuasion and negotiation skills
  - Prospecting and cold outreach techniques
  - CRM management
  - Market research abilities
  - Tools: HubSpot, Salesforce, LinkedIn Sales Navigator, Mailchimp

- Engineering & Architecture
  - Technical drawing and modeling skills
  - Knowledge of engineering principles or architectural standards
  - Problem-solving in design and structures
  - Compliance with regulations
  - Tools: AutoCAD, SolidWorks, Revit, SketchUp

- Data Science & Analytics
  - Statistical analysis and modeling
  - Programming in Python or R
  - Data visualization techniques
  - Machine learning basics
  - Tools: Pandas, NumPy, Tableau, SQL, Scikit-learn

- Teaching & Tutoring
  - Subject matter expertise
  - Effective communication and patience
  - Lesson planning and curriculum development
  - Assessment and feedback skills
  - Tools: Zoom, Google Classroom, Khan Academy tools, Moodle
"""


client = genai.Client(api_key=settings.GEMINI_API_KEY)


def categorize_title(title: str) -> str:

    prompt = f"""
    Here is a job title: {title}.

    Here is a list of freelance job categories:
    {JOB_CATEGORIES}

    Task: Categorize the job title into exactly one fitting category from the provided list. Follow these steps:
    1. Analyze the job title for key themes (e.g., skills, tasks, or industry mentioned).
    2. Match it to the most relevant category in the list based on the examples under each category.
    3. If it fits multiple, choose the best single match. If it doesn't fit any well, use "Uncategorized".
    4. Use the exact category name from the list (e.g., "Web Development"), preserving capitalization.

    Examples:
    - Title: "Need a logo designer for startup" -> "Graphic Design & Illustration"
    - Title: "Python script for data automation" -> "Programming & Software Development"
    - Title: "Tutor for high school math online" -> "Teaching & Tutoring"
    - Title: "Random unrelated task" -> "Uncategorized"

    Return only the chosen category name, nothing else.
    """

    try:
        response = client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=prompt,
        )

        return response.text.strip()  # type: ignore
    except Exception as e:
        return "Uncategorized"


def required_skills(title: str) -> str:
    prompt = f"""
    Here is a job title: {title}.

    Here is a list of skills/tools required for each freelance job category:
    {JOB_SKILLS}

    Task: Select 3-5 most fitting skills/tools for the job title from the provided list. Follow these steps:
    1. Infer the implied category from the title (e.g., based on tasks or keywords).
    2. Pull skills/tools only from the matching category section(s) in the list.
    3. Choose the most relevant ones that a freelancer would need for this specific title.
    4. If no good fits, return exactly "Unspecified".
    5. Format as a comma-separated string: 'Skill1, Skill2, Skill3, ...' (no quotes, no extras, trim spaces).

    Examples:
    - Title: "Build a WordPress e-commerce site" -> 'Knowledge of HTML, CSS, and JavaScript, Back-end languages such as PHP, Python or Node.js, WordPress customization, Tools: Visual Studio Code, Git, Chrome DevTools, Bootstrap'
    - Title: "SEO content writer for blog" -> 'Strong command of language and grammar, Research and fact-checking abilities, SEO and keyword optimization knowledge, Tools: Microsoft Word, Google Docs, Grammarly, WordPress, Hemingway App'
    - Title: "Unrelated nonsense task" -> 'Unspecified'

    Return only the formatted string, nothing else.
    """

    try:
        response = client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=prompt,
        )

        return response.text.strip()  # type: ignore
    except Exception as e:
        return "Unspecified"


class Command(BaseCommand):
    help = "Generate leads from Reddit posts"

    def add_arguments(self, parser):
        parser.add_argument(
            "--posts_limit",
            type=int,
            default=10,
            help="Number of posts to fetch per subreddit.",
        )

    def handle(self, *args, **options):
        posts_limit = options["posts_limit"]

        reddit = praw.Reddit(
            client_id=settings.CLIENT_ID,
            client_secret=settings.CLIENT_SECRET,
            refresh_token=settings.REFRESH_TOKEN,
            user_agent=settings.USER_AGENT,
        )

        current_time = timezone.now()
        one_day_ago = current_time - timedelta(days=1)

        self.stdout.write("=" * 50)
        self.stdout.write("🚀 Starting Reddit Leads Generation...")
        self.stdout.write("=" * 50)

        for target_sub in TARGET_SUBS:
            subreddit = reddit.subreddit(target_sub)

            self.stdout.write(f"📥 Compiling from: {subreddit.display_name}")

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
                        "desired_skills": required_skills(title),
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

                            self.stdout.write(f"Created post: {submission.id}, title: {title}")

                        else:
                            self.stdout.write(f"Skipped post: {submission.id}, title: {title}")

                    except IntegrityError as e:
                        raise Exception(
                            f"Error saving lead/post for {submission.author.name if submission.author else "N/A"}: {e}"
                        )

            except Exception as e:
                raise Exception(
                    f"Error processing subreddit {subreddit.display_name}: {e}"
                )
