import io
from django.http import FileResponse
from django.db.models import Sum
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from recipe.models import ShoppingList, Recipe, Ingredient, IngredientsRecipe


LINES = [
    'This is line 1',
    'This is line 2',
    'This is line 3'
]


class FileDownloadListAPIView(generics.ListAPIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request, format=None):
        canvas.pdfmetrics.registerFont(
            TTFont('FreeSans', './FreeSans.ttf'))
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer)
        textob = p.beginText()
        textob.setFont('FreeSans', 25)
        shopping_lists = ShoppingList.objects.filter(user=request.user)
        recepies = Recipe.objects.filter(
            is_in_shopping_cart__in=shopping_lists)
        ingredient_receipes = IngredientsRecipe.objects.filter(
            recipe__in=recepies
        ).values('ingredient').annotate(total_amount=Sum('amount'))
        number_ingredient = 1
        for ingredient in ingredient_receipes:
            unit = Ingredient.objects.get(id=ingredient['ingredient'])

            result = (f"{number_ingredient}){unit.title}: "
                      f"{ingredient['total_amount']} - "
                      f"{unit.measurement_unit}")
            number_ingredient += 1
            textob.textLine(result)
        p.drawText(textob)
        p.showPage()
        p.save()

        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True,
                            filename="ingredients.pdf")
