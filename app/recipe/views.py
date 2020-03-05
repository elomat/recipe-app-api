from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Tag
from recipe.serializers import TagSerializer


class RetrieveListTags(viewsets.GenericViewSet, 
					   mixins.ListModelMixin, 
					   mixins.CreateModelMixin):
	serializer_class = TagSerializer
	queryset = Tag.objects.all()
	authentication_classes = (TokenAuthentication,)
	permission_classes = (IsAuthenticated,)


	def get_queryset(self):
		return self.queryset.filter(user=self.request.user).order_by("-name")

	def perform_create(self, serializer):
		serializer.save(user=self.request.user)



