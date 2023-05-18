# Generated by Django 4.2 on 2023-05-18 19:11

from django.db import migrations, models
import django.db.models.deletion
import django_jsonform.models.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BaseVideoFile',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255, unique=True)),
                ('created_at', models.DateField(auto_now_add=True)),
                ('file_path', models.CharField(blank=True, default='')),
                ('ffprobe_info', django_jsonform.models.fields.JSONField(blank=True, null=True)),
            ],
            options={
                'ordering': ['-id'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Filter',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255, unique=True)),
                ('created_at', models.DateField(auto_now_add=True)),
                ('ffmpeg_args', django_jsonform.models.fields.ArrayField(base_field=models.CharField(max_length=1999), size=None)),
            ],
            options={
                'ordering': ['-id'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='FilterResults',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255, unique=True)),
                ('created_at', models.DateField(auto_now_add=True)),
                ('json_output', django_jsonform.models.fields.JSONField(blank=True, null=True)),
                ('video_filter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='results', to='entities.filter')),
            ],
            options={
                'ordering': ['-id'],
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
            ],
            options={
                'ordering': ['-id'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ComparisonFilter',
            fields=[
                ('filter_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='entities.filter')),
            ],
            options={
                'ordering': ['-id'],
                'abstract': False,
            },
            bases=('entities.filter',),
        ),
        migrations.CreateModel(
            name='InformationFilter',
            fields=[
                ('filter_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='entities.filter')),
            ],
            options={
                'ordering': ['-id'],
                'abstract': False,
            },
            bases=('entities.filter',),
        ),
        migrations.CreateModel(
            name='OriginalVideoFile',
            fields=[
                ('basevideofile_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='entities.basevideofile')),
            ],
            options={
                'ordering': ['-id'],
                'abstract': False,
            },
            bases=('entities.basevideofile',),
        ),
        migrations.CreateModel(
            name='InformationFilterResult',
            fields=[
                ('filterresults_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='entities.filterresults')),
                ('video', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='info_filter_results', to='entities.originalvideofile')),
            ],
            options={
                'ordering': ['-id'],
                'abstract': False,
            },
            bases=('entities.filterresults',),
        ),
        migrations.CreateModel(
            name='EncodedVideoFile',
            fields=[
                ('basevideofile_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='entities.basevideofile')),
                ('encoding_time', models.FloatField(null=True)),
                ('original_video_file', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='encoded_video_files', to='entities.originalvideofile')),
                ('video_encoding', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='encoded_video_files', to='entities.videoencoding')),
            ],
            options={
                'unique_together': {('original_video_file', 'video_encoding')},
            },
            bases=('entities.basevideofile',),
        ),
        migrations.CreateModel(
            name='DecodedVideoFile',
            fields=[
                ('basevideofile_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='entities.basevideofile')),
                ('decoding_time', models.FloatField(null=True)),
                ('encoded_video_file', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='decoded_video_file', to='entities.encodedvideofile')),
            ],
            options={
                'ordering': ['-id'],
                'abstract': False,
            },
            bases=('entities.basevideofile',),
        ),
        migrations.CreateModel(
            name='ComparisonFilterResult',
            fields=[
                ('filterresults_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='entities.filterresults')),
                ('reference_video', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='entities.originalvideofile')),
                ('video_to_compare', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='entities.decodedvideofile')),
            ],
            options={
                'ordering': ['-id'],
                'abstract': False,
            },
            bases=('entities.filterresults',),
        ),
    ]
