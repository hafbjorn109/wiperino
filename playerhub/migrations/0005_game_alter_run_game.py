# Generated by Django 5.2 on 2025-05-02 11:09

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('playerhub', '0004_run_moderator_session_code_alter_run_session_code'),
    ]

    operations = [
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
            ],
        ),
        migrations.AlterField(
            model_name='run',
            name='game',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='playerhub.game'),
        ),
    ]
