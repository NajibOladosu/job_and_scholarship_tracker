# Generated migration for Tag, Interview, Interviewer, Referral models and Application archive fields

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tracker', '0002_note'),
    ]

    operations = [
        # Create Tag model
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Tag name (e.g., Remote, High Salary)', max_length=50, verbose_name='name')),
                ('color', models.CharField(default='#6366f1', help_text='Hex color code for tag display', max_length=7, verbose_name='color')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='updated at')),
                ('user', models.ForeignKey(help_text='User who owns this tag', on_delete=django.db.models.deletion.CASCADE, related_name='tags', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'tag',
                'verbose_name_plural': 'tags',
                'ordering': ['name'],
                'indexes': [
                    models.Index(fields=['user', 'name'], name='tracker_tag_user_name_idx'),
                ],
            },
        ),

        # Add unique constraint for user+name on Tag
        migrations.AddConstraint(
            model_name='tag',
            constraint=models.UniqueConstraint(fields=['user', 'name'], name='unique_tag_per_user'),
        ),

        # Add archive fields to Application
        migrations.AddField(
            model_name='application',
            name='is_archived',
            field=models.BooleanField(default=False, help_text='Whether this application has been archived', verbose_name='is archived'),
        ),
        migrations.AddField(
            model_name='application',
            name='archived_at',
            field=models.DateTimeField(blank=True, help_text='Date and time when application was archived', null=True, verbose_name='archived at'),
        ),

        # Add tags many-to-many relationship to Application
        migrations.AddField(
            model_name='application',
            name='tags',
            field=models.ManyToManyField(blank=True, help_text='Tags for organizing and categorizing applications', related_name='applications', to='tracker.tag'),
        ),

        # Create Interview model
        migrations.CreateModel(
            name='Interview',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('interview_type', models.CharField(choices=[('phone', 'Phone Interview'), ('video', 'Video Interview'), ('onsite', 'On-site Interview'), ('panel', 'Panel Interview')], help_text='Type of interview', max_length=20, verbose_name='interview type')),
                ('scheduled_date', models.DateTimeField(help_text='Date and time of interview', verbose_name='scheduled date')),
                ('duration_minutes', models.PositiveIntegerField(default=60, help_text='Expected duration in minutes', verbose_name='duration (minutes)')),
                ('location', models.TextField(blank=True, help_text='Physical location for on-site interviews', verbose_name='location')),
                ('meeting_link', models.URLField(blank=True, help_text='Video conferencing link (Zoom, Google Meet, etc.)', max_length=500, verbose_name='meeting link')),
                ('notes', models.TextField(blank=True, help_text='Preparation notes, topics, feedback', verbose_name='notes')),
                ('status', models.CharField(choices=[('scheduled', 'Scheduled'), ('completed', 'Completed'), ('cancelled', 'Cancelled'), ('rescheduled', 'Rescheduled')], default='scheduled', help_text='Interview status', max_length=20, verbose_name='status')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='updated at')),
                ('application', models.ForeignKey(help_text='Application this interview is for', on_delete=django.db.models.deletion.CASCADE, related_name='interviews', to='tracker.application')),
                ('user', models.ForeignKey(help_text='User who owns this interview', on_delete=django.db.models.deletion.CASCADE, related_name='interviews', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'interview',
                'verbose_name_plural': 'interviews',
                'ordering': ['scheduled_date'],
                'indexes': [
                    models.Index(fields=['application', 'scheduled_date'], name='tracker_int_app_date_idx'),
                    models.Index(fields=['user', 'scheduled_date'], name='tracker_int_user_date_idx'),
                    models.Index(fields=['status', 'scheduled_date'], name='tracker_int_status_date_idx'),
                ],
            },
        ),

        # Create Interviewer model
        migrations.CreateModel(
            name='Interviewer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Full name of interviewer', max_length=200, verbose_name='name')),
                ('title', models.CharField(help_text='Job title or position', max_length=200, verbose_name='title')),
                ('email', models.EmailField(blank=True, help_text='Email address', max_length=254, verbose_name='email')),
                ('phone', models.CharField(blank=True, help_text='Phone number', max_length=20, verbose_name='phone')),
                ('linkedin_url', models.URLField(blank=True, help_text='LinkedIn profile URL', max_length=500, verbose_name='LinkedIn URL')),
                ('notes', models.TextField(blank=True, help_text='Additional notes about interviewer', verbose_name='notes')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('interview', models.ForeignKey(help_text='Interview this person is conducting', on_delete=django.db.models.deletion.CASCADE, related_name='interviewers', to='tracker.interview')),
            ],
            options={
                'verbose_name': 'interviewer',
                'verbose_name_plural': 'interviewers',
                'ordering': ['name'],
            },
        ),

        # Create Referral model
        migrations.CreateModel(
            name='Referral',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Name of person providing referral', max_length=200, verbose_name='name')),
                ('relationship', models.CharField(help_text='Your relationship to referrer (e.g., former colleague, mentor)', max_length=200, verbose_name='relationship')),
                ('company', models.CharField(help_text='Company where referrer works', max_length=200, verbose_name='company')),
                ('email', models.EmailField(help_text='Email address of referrer', max_length=254, verbose_name='email')),
                ('phone', models.CharField(blank=True, help_text='Phone number', max_length=20, verbose_name='phone')),
                ('referred_date', models.DateField(help_text='Date when referral was made', verbose_name='referred date')),
                ('notes', models.TextField(blank=True, help_text='Additional notes about referral', verbose_name='notes')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('application', models.ForeignKey(help_text='Application this referral is for', on_delete=django.db.models.deletion.CASCADE, related_name='referrals', to='tracker.application')),
                ('user', models.ForeignKey(help_text='User who owns this referral', on_delete=django.db.models.deletion.CASCADE, related_name='referrals', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'referral',
                'verbose_name_plural': 'referrals',
                'ordering': ['-referred_date'],
                'indexes': [
                    models.Index(fields=['application', '-referred_date'], name='tracker_ref_app_date_idx'),
                    models.Index(fields=['user', '-referred_date'], name='tracker_ref_user_date_idx'),
                ],
            },
        ),
    ]
