# -*- coding: utf-8 -*-
# Generated by Django 1.9.11 on 2016-12-22 18:30
from __future__ import unicode_literals
from operator import mul, itemgetter

from django.db import migrations, models
from django.conf import settings
from django.db.models import Max


def gen_pp(apps, schema_editor):
    Profile = apps.get_model('judge', 'Profile')
    Problem = apps.get_model('judge', 'Problem')
    _pp_step = getattr(settings, 'DMOJ_PP_STEP', 0.95)
    table = [pow(_pp_step, i) for i in xrange(getattr(settings, 'DMOJ_PP_ENTRIES', 100))]
    bonus_function =  getattr(settings, 'DMOJ_PP_BONUS_FUNCTION', lambda n: 300 * (1 - 0.997 ** n))
    for row in Profile.objects.all():
        data = (Problem.objects.filter(submission__user=row, submission__points__isnull=False, is_public=True)
                .annotate(max_points=Max('submission__points')).order_by('-max_points')
                .values_list('max_points', flat=True))
        extradata = Problem.objects.filter(submission__user=row, submission__result='AC', is_public=True) \
                        .values('id').distinct().count()
        size = min(len(data), len(table))
        row.performance_points = sum(map(mul, table[:size], data[:size])) + bonus_function(extradata)
        row.save()


class Migration(migrations.Migration):

    dependencies = [
        ('judge', '0054_tickets'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='performance_points',
            field=models.FloatField(db_index=True, default=0),
        ),
        migrations.RunPython(gen_pp, reverse_code=migrations.RunPython.noop),
    ]
