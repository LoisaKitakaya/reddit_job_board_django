from posts.models import Post
from django.contrib import admin


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        "post_title",
        "post_trigger",
        "post_time",
    )

    list_filter = ("subreddit", "post_category", "post_trigger")

    search_fields = (
        "post_title",
        "reddit_post_id",
        "subreddit",
        "post_owner_reddit_username",
    )

    readonly_fields = ("id",)

    fields = (
        "id",
        "reddit_post_id",
        "post_title",
        "post_url",
        "post_owner_reddit_username",
        "subreddit",
        "post_category",
        "desired_skills",
        "post_trigger",
        "post_time",
    )

    list_per_page = 25
