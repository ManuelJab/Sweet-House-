import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


def create_password_reset_code_if_missing(apps, schema_editor):
    PasswordResetCode = apps.get_model('tienda', 'PasswordResetCode')
    table_names = schema_editor.connection.introspection.table_names()
    if PasswordResetCode._meta.db_table not in table_names:
        schema_editor.create_model(PasswordResetCode)


class Migration(migrations.Migration):

    dependencies = [
        ('tienda', '0004_producto_ingredients_alter_producto_category'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunPython(
                    create_password_reset_code_if_missing,
                    reverse_code=migrations.RunPython.noop,
                ),
            ],
            state_operations=[
                migrations.CreateModel(
                    name='PasswordResetCode',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('email', models.EmailField(max_length=254)),
                        ('code_hash', models.CharField(max_length=128)),
                        ('attempts', models.PositiveSmallIntegerField(default=0)),
                        ('created_at', models.DateTimeField(auto_now_add=True)),
                        ('last_sent_at', models.DateTimeField(default=django.utils.timezone.now)),
                        ('expires_at', models.DateTimeField()),
                        ('verified_at', models.DateTimeField(blank=True, null=True)),
                        ('used_at', models.DateTimeField(blank=True, null=True)),
                        ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                    ],
                    options={
                        'ordering': ['-created_at'],
                        'indexes': [models.Index(fields=['email', 'created_at'], name='tienda_pass_email_5d4a41_idx'), models.Index(fields=['user', 'created_at'], name='tienda_pass_user_id_c79d85_idx'), models.Index(fields=['expires_at'], name='tienda_pass_expires_4d9672_idx')],
                    },
                ),
            ],
        ),
    ]
