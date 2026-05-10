import csv
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from scheduler.models import StudentProfile

class Command(BaseCommand):
    help = "Import students from CSV file"

    def handle(self, *args, **kwargs):
        file_path = 'students.csv'  # Path to your CSV file

        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                username = row['username'].strip()  # remove spaces
                student_id = row['student_id'].strip()  # remove spaces

                # Create or update User
                user, created_user = User.objects.get_or_create(username=username)
                if created_user:
                    user.set_unusable_password()  # No password needed
                    user.save()
                    self.stdout.write(self.style.SUCCESS(f'Created user: {username}'))

                # Create or update StudentProfile
                profile, created_profile = StudentProfile.objects.update_or_create(
                    student_id=student_id,
                    defaults={'user': user}
                )

                if created_profile:
                    self.stdout.write(self.style.SUCCESS(f'Added student ID: {student_id}'))
                else:
                    self.stdout.write(self.style.WARNING(f'Updated student ID: {student_id}'))
