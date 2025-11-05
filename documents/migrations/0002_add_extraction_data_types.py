# Generated manually for adding new data types to ExtractedInformation

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='extractedinformation',
            name='data_type',
            field=models.CharField(
                choices=[
                    ('name', 'Name'),
                    ('email', 'Email'),
                    ('phone', 'Phone'),
                    ('education', 'Education'),
                    ('experience', 'Work Experience'),
                    ('skills', 'Skills'),
                    ('certifications', 'Certifications'),
                    ('projects', 'Projects'),
                    ('languages', 'Languages'),
                    ('summary', 'Professional Summary'),
                ],
                help_text='Type of extracted data',
                max_length=20,
                verbose_name='data type'
            ),
        ),
    ]
