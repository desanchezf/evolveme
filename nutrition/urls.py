from django.urls import path

from nutrition.views import daily_diet_form_view, product_analyze_view, product_form_view

app_name = "nutrition"

urlpatterns = [
    path("product/", product_form_view, name="product_form"),
    path("product/analyze/", product_analyze_view, name="product_analyze"),
    path("daily-diet/", daily_diet_form_view, name="daily_diet_form"),
]
