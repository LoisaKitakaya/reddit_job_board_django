from ninja import ModelSchema
from posts.models import Post


class Results(ModelSchema):
    class Meta:
        model = Post
        fields = "__all__"
