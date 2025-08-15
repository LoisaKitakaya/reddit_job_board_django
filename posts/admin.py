from django.urls import path
from posts.models import Post
from django.urls import reverse
from django.contrib import admin
from django.contrib import messages
from posts.tasks import generate_leads
from django.http import HttpResponseRedirect


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

    def has_add_permission(self, request):
        return False

    def get_urls(self):
        urls = super().get_urls()

        custom_urls = [
            path(
                "generate-leads/",
                self.admin_site.admin_view(self.generate_leads_view),
                name="post-generate-leads",
            ),
        ]

        return custom_urls + urls

    def generate_leads_view(self, request):
        try:
            generate_leads(posts_limit=20)  # type: ignore

            self.message_user(
                request,
                "Lead generation task successful",
                level=messages.SUCCESS,
            )

        except Exception as e:
            self.message_user(
                request,
                f"Error queuing lead generation task: {str(e)}",
                level=messages.ERROR,
            )

        return HttpResponseRedirect(reverse("admin:posts_post_changelist"))

    change_list_template = "admin/posts/post/change_list.html"
