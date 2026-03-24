from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='portfolio',
            name='category',
            field=models.CharField(
                choices=[
                    ('case-study', 'Case Study'),
                    ('it-consultancy', 'IT Consultancy'),
                    ('uix-design', 'UI/UX Design'),
                    ('software', 'Software'),
                ],
                default='case-study',
                max_length=30,
            ),
        ),
    ]
