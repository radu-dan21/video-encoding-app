# Generated by Django 4.2 on 2023-05-20 16:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('entities', '0003_rename_file_path_basevideofile_file_name_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='filterresults',
            name='json_output',
        ),
        migrations.AddField(
            model_name='filterresults',
            name='output',
            field=models.CharField(blank=True, default=True, max_length=1024),
        ),
    ]