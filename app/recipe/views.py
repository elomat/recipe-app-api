from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Tag, Ingredient, Recipe
from recipe.serializers import IngredientSerializer, RecipeImageSerializer, \
							   RecipeDetailSerializer, RecipeSerializer, TagSerializer


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

	def _params_to_int(self, qs):
		return [int(qs_str) for qs_str in qs.split(",")]

	def get_queryset(self):
		tags = self.request.query_params.get('tags')
		ingredients = self.request.query_params.get('ingredients')

		queryset = self.queryset

		if tags:
			tags_ids = self._params_to_int(tags)

			queryset.filter(tags__id__in=tags_ids)

		if ingredients:
			ingredient_ids = self._params_to_int(ingredients)
			
			queryset.filter(ingredients__id__in=ingredient_ids)

		return queryset.filter(user=self.request.user)

	def get_serializer_class(self):
		if self.action == 'retrieve':
			return RecipeDetailSerializer
		elif self.action == 'upload_image':
			return RecipeImageSerializer

		return self.serializer_class

	def perform_create(self, serializer):
		serializer.save(user=self.request.user)

	@action(methods=['POST'], detail=True, url_path='upload-image')
	def upload_image(self, request, pk=None):
		recipe = self.get_object()
		serializer = self.get_serializer(
				recipe,
				data=request.data
			)

		if serializer.is_valid():
			serializer.save()
			return Response(
					serializer.data,
					status=status.HTTP_200_OK
				)

		return Response(
				serializer.errors,
				status=status.HTTP_400_BAD_REQUEST
			)

