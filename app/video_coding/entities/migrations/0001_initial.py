# Generated by Django 4.2 on 2023-05-31 19:48

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django_jsonform.models.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ComparisonFilter',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255, unique=True)),
                ('created_at', models.DateField(auto_now_add=True)),
                ('ffmpeg_args', django_jsonform.models.fields.ArrayField(base_field=models.CharField(max_length=1999), size=None)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='InformationFilter',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255, unique=True)),
                ('created_at', models.DateField(auto_now_add=True)),
                ('ffmpeg_args', django_jsonform.models.fields.ArrayField(base_field=models.CharField(max_length=1999), size=None)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='OriginalVideoFile',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255, unique=True)),
                ('created_at', models.DateField(auto_now_add=True)),
                ('ffprobe_info', django_jsonform.models.fields.JSONField(blank=True, null=True)),
                ('file_name', models.CharField(blank=True, default='', validators=[django.core.validators.RegexValidator(regex='^(.+)\\.(.){1,5}')])),
                ('status', models.CharField(choices=[('R', 'Ready'), ('I', 'Computing original video metrics'), ('E', 'Encoding child videos'), ('C', 'Computing encoded video(s) metrics'), ('D', 'Done'), ('F', 'Failed')], default='R', max_length=1)),
                ('error_message', models.CharField(blank=True, default='', max_length=1024)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='VideoEncoding',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255, unique=True)),
                ('created_at', models.DateField(auto_now_add=True)),
                ('ffmpeg_args', django_jsonform.models.fields.ArrayField(base_field=models.CharField(max_length=1999), size=None)),
                ('video_extension', models.CharField(blank=True, choices=[('', '---'), ('webm', 'webm'), ('mkv', 'mkv'), ('flv', 'flv'), ('vob', 'vob'), ('ogv', 'ogv'), ('ogg', 'ogg'), ('rrc', 'rrc'), ('gifv', 'gifv'), ('mng', 'mng'), ('mov', 'mov'), ('avi', 'avi'), ('qt', 'qt'), ('wmv', 'wmv'), ('yuv', 'yuv'), ('rm', 'rm'), ('asf', 'asf'), ('amv', 'amv'), ('mp4', 'mp4'), ('m4p', 'm4p'), ('m4v', 'm4v'), ('mpg', 'mpg'), ('mp2', 'mp2'), ('mpeg', 'mpeg'), ('mpe', 'mpe'), ('mpv', 'mpv'), ('m4v', 'm4v'), ('svi', 'svi'), ('3gp', '3gp'), ('3g2', '3g2'), ('mxf', 'mxf'), ('roq', 'roq'), ('nsv', 'nsv'), ('flv', 'flv'), ('f4v', 'f4v'), ('f4p', 'f4p'), ('f4a', 'f4a'), ('f4b', 'f4b'), ('mod', 'mod')], default='', help_text="If blank, the original video's extension will be used for the encoded videos", max_length=5)),
            ],
            options={
                'ordering': ['-id'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='InformationFilterResult',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255, unique=True)),
                ('created_at', models.DateField(auto_now_add=True)),
                ('output', models.TextField(blank=True, default='')),
                ('compute_time', models.FloatField(null=True)),
                ('video', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='info_filter_results', to='entities.originalvideofile')),
                ('video_filter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='results', to='entities.informationfilter')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='EncodedVideoFile',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255, unique=True)),
                ('created_at', models.DateField(auto_now_add=True)),
                ('ffprobe_info', django_jsonform.models.fields.JSONField(blank=True, null=True)),
                ('file_name', models.CharField(blank=True, default='', validators=[django.core.validators.RegexValidator(regex='^(.+)\\.(.){1,5}')])),
                ('encoding_time', models.FloatField(null=True)),
                ('original_video_file', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='encoded_video_files', to='entities.originalvideofile')),
                ('video_encoding', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='encoded_video_files', to='entities.videoencoding')),
            ],
            options={
                'unique_together': {('original_video_file', 'video_encoding')},
            },
        ),
        migrations.CreateModel(
            name='DecodedVideoFile',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255, unique=True)),
                ('created_at', models.DateField(auto_now_add=True)),
                ('ffprobe_info', django_jsonform.models.fields.JSONField(blank=True, null=True)),
                ('file_name', models.CharField(blank=True, default='', validators=[django.core.validators.RegexValidator(regex='^(.+)\\.(.){1,5}')])),
                ('decoding_time', models.FloatField(null=True)),
                ('encoded_video_file', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='decoded_video_file', to='entities.encodedvideofile')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ComparisonFilterResult',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255, unique=True)),
                ('created_at', models.DateField(auto_now_add=True)),
                ('output', models.TextField(blank=True, default='')),
                ('compute_time', models.FloatField(null=True)),
                ('reference_video', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comparison_filter_results', to='entities.originalvideofile')),
                ('video_filter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='results', to='entities.comparisonfilter')),
                ('video_to_compare', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='filter_results', to='entities.decodedvideofile')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
