# Generated by Django 5.1.7 on 2025-05-03 00:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ImagemColetas',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('imagem', models.ImageField(upload_to='coletas/', verbose_name='Imagem')),
                ('criado_em', models.DateTimeField(auto_now_add=True, verbose_name='Data de criação')),
            ],
            options={
                'verbose_name': 'Imagem da Coleta',
                'verbose_name_plural': 'Imagens da Coleta',
                'db_table': 'imagem_coletas',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='ImagemPerfil',
            fields=[
                ('criado_em', models.DateTimeField(auto_now_add=True)),
                ('atualizado_em', models.DateTimeField(auto_now_add=True)),
                ('id', models.SmallAutoField(primary_key=True, serialize=False)),
                ('imagem', models.TextField()),
                ('file_id', models.CharField(max_length=100)),
            ],
            options={
                'db_table': 'imagem_perfil',
                'managed': False,
            },
        ),
        migrations.DeleteModel(
            name='MateriaisPontosColeta',
        ),
    ]
