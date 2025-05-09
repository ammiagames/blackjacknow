# Generated by Django 5.1.4 on 2025-05-04 18:20

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Card",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "suit",
                    models.CharField(
                        choices=[("h", "h"), ("d", "d"), ("s", "s"), ("c", "c")],
                        max_length=1,
                    ),
                ),
                (
                    "rank",
                    models.CharField(
                        choices=[
                            ("2", "2"),
                            ("3", "3"),
                            ("4", "4"),
                            ("5", "5"),
                            ("6", "6"),
                            ("7", "7"),
                            ("8", "8"),
                            ("9", "9"),
                            ("T", "T"),
                            ("J", "J"),
                            ("Q", "Q"),
                            ("K", "K"),
                            ("A", "A"),
                        ],
                        max_length=2,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Deck",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="DeckCard",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("position", models.IntegerField()),
                (
                    "card",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="game.card"
                    ),
                ),
                (
                    "deck",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="deck_cards",
                        to="game.deck",
                    ),
                ),
            ],
            options={
                "ordering": ["position"],
            },
        ),
        migrations.CreateModel(
            name="GameSession",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("chip_count", models.IntegerField(default=1000)),
                ("bet_amount", models.IntegerField(default=0)),
                ("is_active", models.BooleanField(default=True)),
                ("result", models.CharField(blank=True, max_length=20)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "deck",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="game.deck"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="CardInHand",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("is_player", models.BooleanField(default=False)),
                ("position", models.IntegerField()),
                (
                    "card",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="game.card"
                    ),
                ),
                (
                    "game_session",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="game.gamesession",
                    ),
                ),
            ],
            options={
                "ordering": ["position"],
            },
        ),
        migrations.CreateModel(
            name="HandHistory",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("hand_id", models.IntegerField()),
                ("player_total", models.IntegerField()),
                ("dealer_total", models.IntegerField()),
                ("result", models.CharField(max_length=50)),
                ("bet_amount", models.IntegerField()),
                ("chip_count_after", models.IntegerField()),
                ("timestamp", models.DateTimeField(auto_now_add=True)),
                (
                    "game_session",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="game.gamesession",
                    ),
                ),
            ],
            options={
                "ordering": ["-timestamp"],
            },
        ),
    ]
