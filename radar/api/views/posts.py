from radar.lib.permissions import IsAdminOrReadOnly
from radar.lib.serializers import MetaSerializerMixin, ModelSerializer
from radar.lib.views import ListCreateApiView, RetrieveUpdateDestroyAPIView
from radar.models import Post


class PostSerializer(MetaSerializerMixin, ModelSerializer):
    class Meta:
        model_class = Post


class PostList(ListCreateApiView):
    serializer_class = PostSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_query(self):
        return Post.query


class PostDetail(RetrieveUpdateDestroyAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_query(self):
        return Post.query
