# Generated by Django 4.2 on 2023-10-08 14:39

from django.db import migrations, models
import django_jsonform.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('entities', '0007_alter_bdmetric_original_video_file'),
    ]

    operations = [
        migrations.AddField(
            model_name='comparisonfilter',
            name='description',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='informationfilter',
            name='description',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='comparisonfilter',
            name='ffmpeg_args',
            field=django_jsonform.models.fields.ArrayField(base_field=models.CharField(max_length=1999), help_text='Arguments that will be passed to ffmpeg for metric computation.', size=None),
        ),
        migrations.AlterField(
            model_name='comparisonfilter',
            name='regex_for_value_extraction',
            field=models.CharField(help_text="Regular expression that will be used for extracting the quality score (float) from ffmpeg's output. Must include a capture group with the name 'value'.", max_length=1999),
        ),
        migrations.AlterField(
            model_name='informationfilter',
            name='ffmpeg_args',
            field=django_jsonform.models.fields.ArrayField(base_field=models.CharField(max_length=1999), help_text='Arguments that will be passed to ffmpeg for metric computation.', size=None),
        ),
    ]
