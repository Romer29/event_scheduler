from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User

# ------------------------
# Category Model
# ------------------------
class Category(models.Model):
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=20, default="primary")  # Bootstrap color hint

    def __str__(self):
        return self.name


# ------------------------
# Event Model
# ------------------------
class Event(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=200, blank=True, null=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    attendees = models.PositiveIntegerField(default=0)
    is_public = models.BooleanField(default=True)
    is_approved = models.BooleanField(default=False)  # optional, can remove later
    status = models.CharField(
    max_length=10,
    choices=STATUS_CHOICES,
    default='pending'
)
  # ✅ added
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    # For student detail view
    def get_absolute_url(self):
        return reverse('scheduler:student_event_detail', args=[str(self.id)])

    # For general event detail (optional, can reuse)
    def get_admin_absolute_url(self):
        return reverse('scheduler:event_detail', args=[str(self.id)])


# ------------------------
# Admin Profile
# ------------------------
class AdminProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    contact_number = models.CharField(max_length=15, blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} (Admin)"


# ------------------------
# Student Profile
# ------------------------
class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    student_id = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return f"{self.student_id} - {self.user.username}"
