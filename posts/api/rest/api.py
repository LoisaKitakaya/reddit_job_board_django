from typing import List
from ninja import Router
from .schema import Results
from posts.models import Post

router = Router()


@router.get("/reddit_posts", response=Results)
def get_reddit_posts(
    request,
    post_owner: str = "",
    post_trigger: str = "",
    post_category: str = "",
    desired_skill: str = "",
    subreddit: str = "",
    limit: int = 20,
    offset: int = 0,
):
    queryset = Post.objects.all()

    if post_owner:
        queryset = queryset.filter(post_owner_reddit_username=post_owner)
    if post_trigger:
        queryset = queryset.filter(post_trigger=post_trigger)
    if post_category:
        queryset = queryset.filter(post_category=post_category)
    if desired_skill:
        queryset = queryset.filter(desired_skill__icontains=desired_skill)
    if subreddit:
        queryset = queryset.filter(subreddit=subreddit)

    total_count = queryset.count()

    posts = queryset[offset : offset + limit]

    return {
        "posts": posts,
        "total_count": total_count,
        "limit": limit,
        "offset": offset,
    }
