# =====================
# IMPORTS
# =====================
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy
from django.db.models import Q
from .models import StudentProfile
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Event
from .forms import EventForm


# =====================
# ROLE CHECKS
# =====================
def admin_required(user):
    return user.is_authenticated and user.is_staff

# Admin login view
def admin_login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_staff:  # Only staff users
            login(request, user)
            return redirect('scheduler:event_list')  # Admin dashboard
        else:
            messages.error(request, "Invalid credentials or not authorized as admin.")

    return render(request, 'scheduler/login.html')

# User login view (optional)
def user_login_view(request):
    if request.method == 'POST':
        student_id = request.POST['student_id']

        try:
            profile = StudentProfile.objects.get(student_id=student_id)
            user = profile.user
        except StudentProfile.DoesNotExist:
            messages.error(request, "Student ID not recognized.")
            return render(request, 'scheduler/user_login.html')

        # Log in the user without password

        login(request, user)
        return redirect('scheduler:student_event_view')  # redirect to user dashboard or events

    return render(request, 'scheduler/user_login.html')


def student_event_list(request):
    # Only show approved events
    events = Event.objects.filter(is_approved=True).order_by('start_time')
    
    # Optional: include search by title
    query = request.GET.get('q')
    if query:
        events = events.filter(title__icontains=query)

    return render(request, 'scheduler/student_event_list.html', {'events': events})


class StudentEventView(LoginRequiredMixin, ListView):
    model = Event
    template_name = 'scheduler/student_event_view.html'  # create this template
    context_object_name = 'events'

    def get_queryset(self):
        # Only approved events
        return Event.objects.filter(is_approved=True).order_by('start_time')
    
class StudentEventView(ListView):
    model = Event
    template_name = 'scheduler/student_event_view.html'
    context_object_name = 'events'

    def get_queryset(self):
        # Show all approved events and student's own (even if pending)
        return Event.objects.filter(
            Q(status='approved') | Q(created_by=self.request.user)
        ).order_by('-start_time')

class StudentEventView(ListView):
    model = Event
    template_name = 'scheduler/student_event_view.html'
    context_object_name = 'events'

    def get_queryset(self):
        # Show all public events
        return Event.objects.all().order_by('-start_time')
    
def StudentEventView(request):
    # Show only approved events to students
    events = Event.objects.filter(status='approved').order_by('start_time')
    return render(request, 'scheduler/student_event_view.html', {'events': events})

def StudentEventView(request):
    if request.user.is_authenticated:
        # Events created by the student
        my_events = Event.objects.filter(created_by=request.user).order_by('start_time')
        # Approved events by others
        approved_events = Event.objects.filter(status='approved').exclude(created_by=request.user)
        events = my_events | approved_events  # Combine QuerySets
    else:
        events = Event.objects.filter(status='approved').order_by('start_time')
    
    return render(request, 'scheduler/student_event_view.html', {'events': events})
    

    # List of student events
class StudentEventView(LoginRequiredMixin, ListView):
    model = Event
    template_name = 'scheduler/student_event_view.html'
    context_object_name = 'events'

    def get_queryset(self):
        # Show events created by this student
        return Event.objects.filter(created_by=self.request.user).order_by('-start_time')


# Event detail page for students
class StudentEventDetailView(LoginRequiredMixin, DetailView):
    model = Event
    template_name = 'scheduler/student_event_delete.html'
    context_object_name = 'event'

    def get_queryset(self):
        # Students can only see their own events
        return Event.objects.filter(created_by=self.request.user)

class EventDeleteView(DeleteView):
    model = Event
    template_name = 'scheduler/event_confirm_delete.html'
    success_url = reverse_lazy('scheduler:event_list')

    
class StudentEventDetailView(DetailView):
    model = Event
    template_name = 'scheduler/student_event_detail.html'
    context_object_name = 'event'

    def get_queryset(self):
        # Show all events (approved or not — all public)
        return Event.objects.all()

# Student can add event (default is is_approved=False)
class StudentEventCreateView(LoginRequiredMixin, CreateView):
    model = Event
    form_class = EventForm
    template_name = 'scheduler/student_event_create.html'

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.is_approved = False  # default pending approval
        return super().form_valid(form)

    def get_success_url(self):
        return redirect('scheduler:event_view')  # back to student event list


# Public Event List view
class EventListView(ListView):
    model = Event
    template_name = 'scheduler/event_list.html'
    context_object_name = 'all_events'
    ordering = ['start_time']


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_staff:  # only staff can login here
            login(request, user)
            return redirect('scheduler:event_list')  # redirect admin to events dashboard
        else:
            messages.error(request, "Invalid credentials or not authorized as admin.")
    
    return render(request, 'scheduler/login.html')

def logout_view(request):
    logout(request)
    return redirect('scheduler:role_select')

# =====================
# ROLE SELECTION

def role_select(request):
    events = Event.objects.all().order_by('-start_time')  # show all events
    return render(request, 'role_select.html', {'events': events})
# =====================
# FRONT PAGE / DASHBOARD
# =====================
@login_required
def frontpage(request):
    if request.user.is_staff:
        return render(request, 'scheduler/admin_dashboard.html')
    else:
    
        return render(request, 'scheduler/user_dashboard.html')
    

# =====================
# EVENT VIEWS
# =====================
class EventListView(ListView):
    model = Event
    template_name = 'scheduler/event_list.html'
    context_object_name = 'events'
    ordering = ['start_time']

    def get_queryset(self):
        query = self.request.GET.get('q')
        if self.request.user.is_authenticated and self.request.user.is_staff:
            events = Event.objects.all()
        else:
            events = Event.objects.filter(is_approved=True)
        if query:
            events = events.filter(Q(title__icontains=query) | Q(description__icontains=query))
        return events

class EventDetailView(DetailView):
    model = Event
    template_name = 'scheduler/event_detail.html'

@method_decorator(login_required, name='dispatch')
class EventCreateView(CreateView):
    model = Event
    form_class = EventForm
    template_name = 'scheduler/event_form.html'
    success_url = reverse_lazy('scheduler:event_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.is_approved = self.request.user.is_staff
        return super().form_valid(form)

@method_decorator([login_required, user_passes_test(admin_required)], name='dispatch')
class EventUpdateView(UpdateView):
    model = Event
    form_class = EventForm
    template_name = 'scheduler/event_form.html'
    success_url = reverse_lazy('scheduler:event_list')

@method_decorator([login_required, user_passes_test(admin_required)], name='dispatch')
class EventDeleteView(DeleteView):
    model = Event
    template_name = 'scheduler/event_confirm_delete.html'
    success_url = reverse_lazy('scheduler:event_list')

# =====================
# USER-SPECIFIC EVENT VIEWS
# =====================
@login_required
def event_view(request):
    events = Event.objects.filter(is_approved=True).order_by('start_time')
    return render(request, 'scheduler/event_view.html', {'events': events})

@login_required
def add_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user
            event.is_approved = False  # needs admin approval
            event.save()
            return render(request, 'scheduler/thank_you.html')
    else:
        form = EventForm()
    return render(request, 'scheduler/add_event.html', {'form': form})

@login_required
def edit_event(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            return redirect('scheduler:event_list')
    else:
        form = EventForm(instance=event)
    return render(request, 'scheduler/edit_event.html', {'form': form, 'event': event})

@login_required
def delete_event(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    if request.method == 'POST':
        event.delete()
        return redirect('scheduler:event_list')
    return render(request, 'scheduler/delete_event.html', {'event': event})

# =====================
# ADMIN APPROVALS
# =====================
@user_passes_test(lambda u: u.is_staff)
def admin_approvals(request):
    pending_events = Event.objects.filter(is_approved=False).order_by('-start_time')
    return render(request, 'scheduler/admin_approvals.html', {'all_events': pending_events})

@user_passes_test(lambda u: u.is_staff)
def approve_event(request, pk):
    event = get_object_or_404(Event, pk=pk)
    event.is_approved = True
    event.save()
    return redirect('scheduler:admin_approvals')

@user_passes_test(lambda u: u.is_staff)
def reject_event(request, pk):
    event = get_object_or_404(Event, pk=pk)
    event.delete()

    return redirect('scheduler:admin_approvals')


@login_required
def student_event_view(request):
    # Show only approved events + student's own events
    events = Event.objects.filter(
        models.Q(status='approved') | models.Q(created_by=request.user)
    ).order_by('start_time')
    return render(request, 'scheduler/student_event_view.html', {'events': events})

@login_required
def student_event_add(request):
    if request.method == 'POST':
        title = request.POST['title']
        description = request.POST.get('description', '')
        start_time = request.POST['start_time']
        end_time = request.POST['end_time']

        Event.objects.create(
            title=title,
            description=description,
            start_time=start_time,
            end_time=end_time,
            created_by=request.user,
            status='pending',  # auto set to pending
        )
        return redirect('scheduler:student_event_view')

    return render(request, 'scheduler/student_event_add.html')

@login_required
def approve_event(request, pk):
    event = get_object_or_404(Event, pk=pk)
    event.status = 'approved'  # ✅ lowercase
    event.save()
    messages.success(request, "Event approved successfully!")
    return redirect('scheduler:dashboard')

@method_decorator([login_required, user_passes_test(admin_required)], name='dispatch')
class EventDeleteView(DeleteView):
    model = Event
    template_name = 'scheduler/event_confirm_delete.html'
    success_url = reverse_lazy('scheduler:event_list')

# Only staff can reject/delete
@user_passes_test(lambda u: u.is_staff)
def approve_event(request, pk):
    event = get_object_or_404(Event, pk=pk)
    event.is_approved = True
    event.status = 'approved'
    event.save()
    return redirect('scheduler:admin_approvals')

@user_passes_test(lambda u: u.is_staff)
def reject_event(request, pk):
    event = get_object_or_404(Event, pk=pk)
    event.delete()
    return redirect('scheduler:admin_approvals')

