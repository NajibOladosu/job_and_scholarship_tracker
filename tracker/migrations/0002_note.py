# Generated migration for Note model

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tracker', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Note',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text='Note title', max_length=200, verbose_name='title')),
                ('content', models.TextField(help_text='Rich text content (stored as HTML from Quill.js)', verbose_name='content')),
                ('plain_text', models.TextField(blank=True, help_text='Plain text version for search', verbose_name='plain text')),
                ('is_pinned', models.BooleanField(default=False, help_text='Pin note to top of list', verbose_name='is pinned')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='updated at')),
                ('application', models.ForeignKey(blank=True, help_text='Application this note is linked to (optional)', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='notes_list', to='tracker.application')),
                ('user', models.ForeignKey(help_text='User who created this note', on_delete=django.db.models.deletion.CASCADE, related_name='notes', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'note',
                'verbose_name_plural': 'notes',
                'ordering': ['-is_pinned', '-updated_at'],
                'indexes': [
                    models.Index(fields=['user', '-is_pinned', '-updated_at'], name='tracker_not_user_id_idx'),
                    models.Index(fields=['application', '-updated_at'], name='tracker_not_applica_idx'),
                    models.Index(fields=['user', 'application'], name='tracker_not_user_ap_idx'),
                ],
            },
        ),
    ]
