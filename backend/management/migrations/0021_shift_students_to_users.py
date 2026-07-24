from django.db import migrations, models
import django.db.models.deletion


def copy_students_to_users(apps, schema_editor):
    with schema_editor.connection.cursor() as cursor:
        cursor.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'student');")
        exists = cursor.fetchone()[0]
        if not exists:
            return

        # 1. Drop all existing foreign key constraints on enrollment targeting student table
        cursor.execute("""
            DO $$
            DECLARE
                r RECORD;
            BEGIN
                FOR r IN (
                    SELECT constraint_name 
                    FROM information_schema.table_constraints 
                    WHERE table_name = 'enrollment' AND constraint_type = 'FOREIGN KEY'
                      AND constraint_name LIKE '%student%'
                ) LOOP
                    EXECUTE 'ALTER TABLE enrollment DROP CONSTRAINT ' || quote_ident(r.constraint_name);
                END LOOP;
            END $$;
        """)

        # 2. Fetch all students
        cursor.execute("SELECT id, full_name, phone, phone2, jshshr, passport_serie, passport_number, is_active FROM student;")
        students = cursor.fetchall()

        for s_id, full_name, phone, phone2, jshshr, passport_serie, passport_number, is_active in students:
            parts = (full_name or '').strip().split(' ', 1)
            first_name = parts[0] if len(parts) > 0 else ''
            last_name = parts[1] if len(parts) > 1 else ''

            cursor.execute('SELECT id FROM "user" WHERE phone = %s;', [phone])
            user_row = cursor.fetchone()

            if user_row:
                new_user_id = user_row[0]
                cursor.execute('''
                    UPDATE "user" 
                    SET role = 'student', phone2 = %s, jshshr = %s, passport_serie = %s, passport_number = %s, first_name = %s, last_name = %s
                    WHERE id = %s;
                ''', [phone2, jshshr, passport_serie, passport_number, first_name, last_name, new_user_id])
            else:
                cursor.execute('''
                    INSERT INTO "user" (
                        password, is_superuser, is_staff, is_active, date_joined, email,
                        phone, phone2, role, first_name, last_name, jshshr, passport_serie, passport_number
                    ) VALUES (
                        '', false, false, %s, NOW(), '',
                        %s, %s, 'student', %s, %s, %s, %s, %s
                    ) RETURNING id;
                ''', [is_active, phone, phone2, first_name, last_name, jshshr, passport_serie, passport_number])
                new_user_id = cursor.fetchone()[0]

            cursor.execute("UPDATE enrollment SET student_id = %s WHERE student_id = %s;", [new_user_id, s_id])


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0020_alter_enrollment_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='phone2',
            field=models.CharField(blank=True, help_text="Qo'shimcha telefon raqami (namuna: 998909009090)", max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(choices=[('superuser', 'Superuser'), ('admin', 'Admin'), ('mechanic', 'Mexanik'), ('instructor', 'Instruktor'), ('coordinator', 'Kordinator'), ('student', "O'quvchi")], default='coordinator', max_length=20),
        ),
        migrations.RunPython(copy_students_to_users, reverse_code=migrations.RunPython.noop),
        migrations.AlterField(
            model_name='enrollment',
            name='student',
            field=models.ForeignKey(limit_choices_to={'role': 'student'}, on_delete=django.db.models.deletion.PROTECT, related_name='enrollments', to='management.user'),
        ),
        migrations.DeleteModel(
            name='Student',
        ),
    ]
