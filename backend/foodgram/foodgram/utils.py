import io
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont

from recipe.models import Ingredient


def download(ingredient_receipes):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = (
        "attachment; filename='shopping_cart.pdf'"
    )
    canvas.pdfmetrics.registerFont(
        TTFont('FreeSans', './FreeSans.ttf'))
    buffer = io.BytesIO()
    pdf_file = canvas.Canvas(buffer)
    pdf_file.setFont('FreeSans', 24)
    pdf_file.drawString(200, 800, 'Список покупок.')
    pdf_file.setFont('FreeSans', 14)
    from_bottom = 750
    for ingredient in ingredient_receipes:
        unit = Ingredient.objects.get(id=ingredient['ingredient'])

        pdf_file.drawString(50,
                            from_bottom,
                            f"{unit.name}: "
                            f"{ingredient['total_amount']} - "
                            f"{unit.measurement_unit}")
        from_bottom -= 20
        if from_bottom <= 50:
            from_bottom = 800
            pdf_file.showPage()
            pdf_file.setFont('FreeSans', 14)

    pdf_file.showPage()
    pdf_file.save()
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response
