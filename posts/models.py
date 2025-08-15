import uuid
from django.db import models


class Post(models.Model):
    TASK = "task"
    OFFER = "offer"
    UNSPECIFIC = "unspecific"

    TRIGGER = [
        (TASK, "Task"),
        (OFFER, "Offer"),
        (UNSPECIFIC, "Unspecific"),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    post_owner_reddit_username = models.CharField(
        max_length=100,
        db_index=True,
    )
    reddit_post_id = models.CharField(
        max_length=20,
        unique=True,
    )
    post_url = models.URLField(
        max_length=200,
    )
    post_title = models.CharField(
        max_length=300,
    )
    post_category = models.CharField(
        max_length=100,
        blank=True,
        null=True,
    )
    desired_skills = models.TextField(
        blank=True,
        null=True,
    )
    post_trigger = models.CharField(
        max_length=20,
        choices=TRIGGER,
        default=UNSPECIFIC,
        blank=True,
        null=True,
    )
    subreddit = models.CharField(
        max_length=100,
        db_index=True,
    )
    post_time = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
    )

    class Meta:
        db_table = "posts"
        ordering = ["-post_time"]
        verbose_name = "Reddit Post"
        verbose_name_plural = "Reddit Posts"

    def __str__(self):
        return f"{self.post_title}"
