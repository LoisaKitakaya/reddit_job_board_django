from typing import List
from posts.models import Post
from ninja import ModelSchema, Schema


class PostsSchema(ModelSchema):
    class Meta:
        model = Post
        fields = "__all__"


class Results(Schema):
    posts: List[PostsSchema]
    total_count: int
    limit: int
    offset: int
