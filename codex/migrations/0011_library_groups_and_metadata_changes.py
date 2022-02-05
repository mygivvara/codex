"""Generated by Django 4.0.1 on 2022-01-31 22:09 & tweaked by aj."""
from decimal import Decimal

from django.db import migrations, models


OLD_COVER_ARTIST_ROLES = ("Cover", "CoverArtist")


def critical_rating_to_decimal(apps, _schema_editor):
    """Migrate comics with charfield ratings to decimal if possible."""
    comic_model = apps.get_model("codex", "comic")
    update_comics = []
    comics_with_ratings = comic_model.objects.exclude(
        critical_rating__isnull=True, critical_rating=""
    ).only("pk", "critical_rating", "critical_rating_decimal")
    for comic in comics_with_ratings:
        try:
            comic.critical_rating_decimal = Decimal(comic.critical_rating)
            update_comics.append(comic)
        except Exception:
            pass
    comic_model.objects.bulk_update(update_comics, ("critical_rating_decimal",))


def cover_to_cover_artist(apps, _schema_editor):
    """Change all roles named Cover to Cover Artist."""
    credit_role_model = apps.get_model("codex", "creditrole")
    cover_roles = credit_role_model.objects.filter(name__in=OLD_COVER_ARTIST_ROLES)
    update_roles = []
    for role in cover_roles:
        role.name = "Cover Artist"
        update_roles.append(role)
    credit_role_model.objects.bulk_update(update_roles, ("name",))


class Migration(migrations.Migration):
    """Library group ACLS and metadata changes."""

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
        ("codex", "0010_haystack"),
    ]

    operations = [
        migrations.AddField(
            model_name="comic",
            name="community_rating",
            field=models.DecimalField(
                db_index=True, decimal_places=2, default=None, max_digits=4, null=True
            ),
        ),
        migrations.AddField(
            model_name="library",
            name="groups",
            field=models.ManyToManyField(blank=True, to="auth.Group"),
        ),
        migrations.AddField(
            model_name="comic",
            name="critical_rating_decimal",
            field=models.DecimalField(
                db_index=True, decimal_places=2, default=None, max_digits=4, null=True
            ),
        ),
        migrations.RunPython(critical_rating_to_decimal),
        migrations.RemoveField(model_name="comic", name="critical_rating"),
        migrations.RenameField(
            model_name="comic",
            old_name="critical_rating_decimal",
            new_name="critical_rating",
        ),
        migrations.RenameField(
            model_name="comic",
            old_name="maturity_rating",
            new_name="age_rating",
        ),
        migrations.RemoveField(
            model_name="comic",
            name="user_rating",
        ),
        migrations.RunPython(cover_to_cover_artist),
    ]
