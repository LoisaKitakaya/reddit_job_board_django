from typing import List
from ninja import Router
from .schema import Results
from posts.models import Post

router = Router()


@router.get("/reddit_posts", response=List[Results])
def get_reddit_posts(
    request,
    post_owner: str = "",
    post_trigger: str = "",
    subreddit: str = "",
    limit: int = 10,
):
    if post_owner:
        return Post.objects.filter(
            post_owner_reddit_username=post_owner,
        )[:limit]

    if post_trigger:
        return Post.objects.filter(
            post_trigger=post_trigger,
        )[:limit]

    if subreddit:
        return Post.objects.filter(
            subreddit=subreddit,
        )[:limit]

    if post_owner:
        return Post.objects.filter()[:limit]

    return Post.objects.all()[:limit]
