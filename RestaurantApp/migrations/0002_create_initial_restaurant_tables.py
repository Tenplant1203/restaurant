from django.db import migrations

INITIAL_TABLES = [
    (1, 2),
    (2, 2),
    (3, 2),
    (4, 2),
    (5, 4),
    (6, 4),
    (7, 4),
    (8, 4),
    (9, 6),
    (10, 6),
    (11, 6),
    (12, 6),
    (13, 8),
    (14, 8),
    (15, 8),
    (16, 8),
    (17, 10),
    (18, 10),
    (19, 10),
    (20, 10),
]


def create_initial_restaurant_tables(apps, _schema_editor):
    restaurant_table = apps.get_model("RestaurantApp", "RestaurantTable")
    for number, capacity in INITIAL_TABLES:
        restaurant_table.objects.get_or_create(
            number=number,
            defaults={"capacity": capacity},
        )


class Migration(migrations.Migration):

    dependencies = [
        ("RestaurantApp", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(
            create_initial_restaurant_tables,
            migrations.RunPython.noop,
        ),
    ]
