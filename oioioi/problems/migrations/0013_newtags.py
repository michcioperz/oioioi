# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2019-04-09 13:44
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import re


class Migration(migrations.Migration):

    dependencies = [
        ('problems', '0012_problem_statistics'),
    ]

    operations = [
        migrations.CreateModel(
            name='AlgorithmTag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20, unique=True, validators=[django.core.validators.MinLengthValidator(3), django.core.validators.MaxLengthValidator(20), django.core.validators.RegexValidator(re.compile('^[-a-zA-Z0-9_]+\\Z'), "Enter a valid 'slug' consisting of letters, numbers, underscores or hyphens.", 'invalid')], verbose_name='name')),
            ],
            options={
                'verbose_name': 'algorithm tag',
                'verbose_name_plural': 'algorithm tags',
            },
        ),
        migrations.CreateModel(
            name='AlgorithmTagThrough',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('problem', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='problems.Problem')),
                ('tag', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='problems.AlgorithmTag')),
            ],
        ),
        migrations.CreateModel(
            name='DifficultyTag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20, unique=True, validators=[django.core.validators.MinLengthValidator(3), django.core.validators.MaxLengthValidator(20), django.core.validators.RegexValidator(re.compile('^[-a-zA-Z0-9_]+\\Z'), "Enter a valid 'slug' consisting of letters, numbers, underscores or hyphens.", 'invalid')], verbose_name='name')),
            ],
            options={
                'verbose_name': 'difficulty tag',
                'verbose_name_plural': 'difficulty tags',
            },
        ),
        migrations.CreateModel(
            name='DifficultyTagThrough',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('problem', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='problems.Problem')),
                ('tag', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='problems.DifficultyTag')),
            ],
        ),
        migrations.CreateModel(
            name='OriginTag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20, unique=True, validators=[django.core.validators.MinLengthValidator(3), django.core.validators.MaxLengthValidator(20), django.core.validators.RegexValidator(re.compile('^[-a-zA-Z0-9_]+\\Z'), "Enter a valid 'slug' consisting of letters, numbers, underscores or hyphens.", 'invalid')], verbose_name='name')),
                ('display_depth', models.IntegerField(default=-1, help_text=b"Sometimes the parent-child relationship does not convey the full information about the tag hierarchy. Some tags are more 'broad' than others, and less broad tags should be grouped under them when displayed (for example in the task archive). For example you may want to display the following hierarchy - OI -> year X -> stage Y in year X -> tasks from stage Y in year X. These tasks would have to be tagged with 'OI / X' and 'OI / stage Y' so that we can search for them conveniently, so displaying them in this particular way requires additional information. The display depth lets you specify the 'broadness' which the tag has. For the OI example - 'OI' would have display depth equal to 0, all the 'year X' tags equal to 1, all the 'stage Y' tags equal to 2. Not all tags have to be used for grouping, and you may not want to specify the display depth at all (set it to -1). For instance 'PA / remote / round X' would be depth 2, but 'PA / remote / type A' and 'PA / distributed task' would be depth -1, since it makes no sense to group distributed tasks under type A tasks or the other way around. Display depth of -1 is displayed after all other depths.")),
                ('parent_tag', models.ForeignKey(blank=True, help_text=b"Tag X is the parent of tag Y, if the presence of Y implies the presence of X. For example: tags with names 'stage 1' and '23' both have the tag with name 'OI' as parent, which does not have a parent tag of its own. The tags can be written as a path from their most deep ancestor, e.g. 'OI / stage 1' or 'OI / 23'. An example of a deeperhierarchy would be: 'PA / remote / type A' and 'PA / remote / type B' tags, for tagging A/B type tasks from remote rounds of Potyczki Algorytmiczne. A task can (and probably should) have multiple origin tags, for example a task from Potyczki Algorytmiczne could have tags: 'PA / 2010', 'PA / remote / type A', 'PA / remote / round 3', which also imply tags 'PA / remote' and 'PA'. If you are still unsure, think of how users will filter the problemset: 'type A' can't be a subtag of 'round 3' or '2010' because the user will want to search tasks of type A from all rounds and all years of PA, however type A/B tasks only occur in remote rounds so we can be more specific and say that 'remote' is the parent of 'type A'.", null=True, on_delete=django.db.models.deletion.CASCADE, related_name='child_tags', to='problems.OriginTag')),
            ],
            options={
                'verbose_name': 'origin tag',
                'verbose_name_plural': 'origin tags',
            },
        ),
        migrations.CreateModel(
            name='OriginTagThrough',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('problem', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='problems.Problem')),
                ('tag', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='problems.OriginTag')),
            ],
        ),
        migrations.AddField(
            model_name='origintag',
            name='problems',
            field=models.ManyToManyField(through='problems.OriginTagThrough', to='problems.Problem'),
        ),
        migrations.AddField(
            model_name='difficultytag',
            name='problems',
            field=models.ManyToManyField(through='problems.DifficultyTagThrough', to='problems.Problem'),
        ),
        migrations.AddField(
            model_name='algorithmtag',
            name='problems',
            field=models.ManyToManyField(through='problems.AlgorithmTagThrough', to='problems.Problem'),
        ),
        migrations.AlterUniqueTogether(
            name='origintagthrough',
            unique_together=set([('problem', 'tag')]),
        ),
        migrations.AlterUniqueTogether(
            name='origintag',
            unique_together=set([('name', 'parent_tag')]),
        ),
        migrations.AlterUniqueTogether(
            name='algorithmtagthrough',
            unique_together=set([('problem', 'tag')]),
        ),
    ]
