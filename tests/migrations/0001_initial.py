# Generated by Django 2.2.19 on 2021-03-31 07:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='BaseModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='BaseToGFKModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='ClassLevel1',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='ClassLevel2',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('fkey', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tests.ClassLevel1')),
            ],
        ),
        migrations.CreateModel(
            name='FKDummyModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='InvalidFKNonRootModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='O2ODummyModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='ChildModel',
            fields=[
                ('basemodel_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='tests.BaseModel')),
                ('child_field', models.CharField(max_length=255)),
            ],
            bases=('tests.basemodel',),
        ),
        migrations.CreateModel(
            name='SubClassOfBaseModel',
            fields=[
                ('basemodel_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='tests.BaseModel')),
            ],
            bases=('tests.basemodel',),
        ),
        migrations.CreateModel(
            name='OneToOneToBaseModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('o2oto', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='tests.BaseModel')),
            ],
        ),
        migrations.CreateModel(
            name='ManyToManyToBaseModelWithRelatedName',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('m2m', models.ManyToManyField(related_name='custom_related_m2m_name', to='tests.BaseModel')),
            ],
        ),
        migrations.CreateModel(
            name='ManyToManyToBaseModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('m2m', models.ManyToManyField(to='tests.BaseModel')),
            ],
        ),
        migrations.CreateModel(
            name='InvalidFKRootModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('invalid_fk', models.ForeignKey(db_constraint=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='invalid_non_root_fk', to='tests.InvalidFKNonRootModel')),
                ('valid_fk', models.ForeignKey(db_constraint=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='valid_non_root_fk', to='tests.InvalidFKNonRootModel')),
            ],
        ),
        migrations.AddField(
            model_name='invalidfknonrootmodel',
            name='invalid_fk',
            field=models.ForeignKey(db_constraint=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='invalid_root_fk', to='tests.InvalidFKRootModel'),
        ),
        migrations.AddField(
            model_name='invalidfknonrootmodel',
            name='valid_fk',
            field=models.ForeignKey(db_constraint=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='valid_root_fk', to='tests.InvalidFKRootModel'),
        ),
        migrations.CreateModel(
            name='GFKModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.PositiveIntegerField()),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType')),
            ],
        ),
        migrations.CreateModel(
            name='ForeignKeyToBaseModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('fkeyto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tests.BaseModel')),
            ],
        ),
        migrations.CreateModel(
            name='ClassLevel3',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('fkey', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tests.ClassLevel2')),
            ],
        ),
        migrations.AddField(
            model_name='basemodel',
            name='fkey',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tests.FKDummyModel'),
        ),
        migrations.AddField(
            model_name='basemodel',
            name='o2o',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='tests.O2ODummyModel'),
        ),
    ]