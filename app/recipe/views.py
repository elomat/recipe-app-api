from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Tag, Ingredient, Recipe
from recipe.serializers import IngredientSerializer, RecipeSerializer, RecipeDetailSerializer, TagSerializer


class BaseRecipeViewSet(viewsets.GenericViewSet,
					 mixins.ListModelMixin,
					 mixins.CreateModelMixin):
	authentication_classes = (TokenAuthentication,)
	permission_classes = (IsAuthenticated,)

	def get_queryset(self):
		return self.queryset.filter(user=self.request.user).order_by("-name")

	def perform_create(self, serializer):
		serializer.save(user=self.request.user)


class TagsViewSet(BaseRecipeViewSet):
	serializer_class = TagSerializer
	queryset = Tag.objects.all()
	

class IngredientsViewSet(BaseRecipeViewSet):
	serializer_class = IngredientSerializer
	queryset = Ingredient.objects.all()


class RecipeViewSet(viewsets.ModelViewSet):
	model = Recipe
	queryset = Recipe.objects.all()
	serializer_class = RecipeSerializer
	permission_classes = (IsAuthenticated,)
	authentication_classes = (TokenAuthentication,)

	def get_queryset(self):
		return self.queryset.filter(user=self.request.user).order_by("-id")

	def get_serializer_class(self):
		if self.action == 'retrieve':
			return RecipeDetailSerializer

		return self.serializer_class

	def perform_create(self, serializer):
		serializer.save(user=self.request.user)
