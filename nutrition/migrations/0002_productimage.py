# Generated manually for ProductImage

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("nutrition", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="ProductImage",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("image", models.ImageField(upload_to="nutrition/products/%Y/%m/", verbose_name="Imagen")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="images",
                        to="nutrition.product",
                        verbose_name="Producto",
                    ),
                ),
            ],
            options={
                "verbose_name": "Imagen de producto",
                "verbose_name_plural": "Imágenes de producto",
                "ordering": ["created_at"],
            },
        ),
    ]
