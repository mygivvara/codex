"""Generated by Django 4.0.4 on 2022-04-26 03:09."""
from pathlib import Path

from django.db import migrations, models


def add_library_folders(apps, _schema_editor):
    """Add library folders if they're missing."""
    folder_model = apps.get_model("codex", "folder")
    top_folders = folder_model.objects.filter(parent_folder=None)

    # Create missing library folders
    top_folder_paths = top_folders.values_list("path", flat=True)
    library_model = apps.get_model("codex", "library")
    libraries_missing_top_folders = library_model.objects.exclude(
        path__in=top_folder_paths
    )

    create_folders = []
    for library in libraries_missing_top_folders:
        path = library.path
        name = Path(library.path).name
        folder = folder_model(library=library, path=path, name=name)
        create_folders.append(folder)

    if create_folders:
        print("\ncreating library folders...")
    new_folders = folder_model.objects.bulk_create(create_folders)
    for folder in new_folders:
        print(f"created library folder {folder.pk}: {folder.path}")

    # Update previously top folders to descend from library fodlers.
    library_paths = library_model.objects.all().values_list("path", flat=True)
    orphan_top_folders = top_folders.exclude(path__in=library_paths)
    update_folders = []
    for folder in orphan_top_folders:
        for library_path in library_paths:
            if Path(folder.path).is_relative_to(library_path):
                old_parent = folder.parent_folder
                folder.parent_folder = folder_model.objects.get(path=library_path)
                update_folders.append(folder)
                print(
                    "updating",
                    folder.path,
                    "parent from",
                    old_parent,
                    "to",
                    folder.parent_folder.pk,
                )
                break
    count = folder_model.objects.bulk_update(update_folders, ["parent_folder"])
    print(f"updated {count} folders.")

    # Link comics to new folders
    comic_model = apps.get_model("codex", "comic")
    ThroughModel = comic_model.folders.through  # noqa:N806
    tms = []
    for new_folder in new_folders:
        comic_pks = comic_model.objects.filter(
            path__startswith=new_folder.path
        ).values_list("pk", flat=True)
        for comic_pk in comic_pks:
            tm = ThroughModel(comic_id=comic_pk, folder_id=new_folder.pk)
            tms.append(tm)

    print(f"linking {len(tms)} comics to new folders...")
    objs = ThroughModel.objects.bulk_create(tms)
    if objs:
        print(f"linked {len(objs)} comics to new folders.")


class Migration(migrations.Migration):
    """Remove cover_image, sort_name. add issue_suffix & file_format."""

    dependencies = [
        ("codex", "0013_int_issue_count_longer_charfields"),
    ]

    operations = [
        migrations.AlterField(  # Fixes django 4.1 bug removing fields
            model_name="comic",
            name="sort_name",
            field=models.CharField(db_index=False, max_length=32),
        ),
        migrations.AlterField(  # Fixes django 4.1 bug removing fields
            model_name="failedimport",
            name="sort_name",
            field=models.CharField(db_index=False, max_length=32),
        ),
        migrations.AlterField(  # Fixes django 4.1 bug removing fields
            model_name="folder",
            name="sort_name",
            field=models.CharField(db_index=False, max_length=32),
        ),
        migrations.AlterField(  # Fixes django 4.1 bug removing fields
            model_name="imprint",
            name="sort_name",
            field=models.CharField(db_index=False, max_length=32),
        ),
        migrations.AlterField(  # Fixes django 4.1 bug removing fields
            model_name="publisher",
            name="sort_name",
            field=models.CharField(db_index=False, max_length=32),
        ),
        migrations.AlterField(  # Fixes django 4.1 bug removing fields
            model_name="series",
            name="sort_name",
            field=models.CharField(db_index=False, max_length=32),
        ),
        migrations.AlterField(  # Fixes django 4.1 bug removing fields
            model_name="volume",
            name="sort_name",
            field=models.CharField(db_index=False, max_length=32),
        ),
        migrations.RemoveField(
            model_name="comic",
            name="cover_image",
        ),
        migrations.RemoveField(
            model_name="comic",
            name="sort_name",
        ),
        migrations.RemoveField(
            model_name="failedimport",
            name="sort_name",
        ),
        migrations.RemoveField(
            model_name="folder",
            name="sort_name",
        ),
        migrations.RemoveField(
            model_name="imprint",
            name="sort_name",
        ),
        migrations.RemoveField(
            model_name="publisher",
            name="sort_name",
        ),
        migrations.RemoveField(
            model_name="series",
            name="sort_name",
        ),
        migrations.RemoveField(
            model_name="volume",
            name="sort_name",
        ),
        migrations.AddField(
            model_name="comic",
            name="file_format",
            field=models.CharField(
                default="comic",
                max_length=5,
                # Removed in the future
                # validators=[codex.models.validate_file_format_choice],
            ),
        ),
        migrations.AddField(
            model_name="comic",
            name="issue_suffix",
            field=models.CharField(db_index=True, default="", max_length=16),
        ),
        migrations.AlterField(
            model_name="comic",
            name="issue",
            field=models.DecimalField(
                db_index=True, decimal_places=2, max_digits=10, null=True
            ),
        ),
        migrations.RunPython(add_library_folders),
    ]
