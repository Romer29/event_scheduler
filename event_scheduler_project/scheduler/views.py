from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from .models import Event
from .forms import EventForm
from django.contrib.auth.decorators import login_required, user_passes_test



# =====================
# ROLE CHECKS
# =====================
def admin_required(user):
    return user.is_authenticated and user.is_staff


# =====================
# EVENT LIST
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


# =====================
# EVENT DETAILS
# =====================
class EventDetailView(DetailView):
    model = Event
    template_name = 'scheduler/event_detail.html'


# =====================
# EVENT CREATE (LOGIN REQUIRED)
# =====================
@method_decorator(login_required, name='dispatch')
class EventCreateView(CreateView):
    model = Event
    form_class = EventForm
    template_name = 'scheduler/event_form.html'
    success_url = reverse_lazy('scheduler:event_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        # Admin-created events auto-approved, users need approval
        form.instance.is_approved = self.request.user.is_staff
        return super().form_valid(form)


# =====================
# EVENT UPDATE (ADMIN ONLY)
# =====================
@method_decorator([login_required, user_passes_test(admin_required)], name='dispatch')
class EventUpdateView(UpdateView):
    model = Event
    form_class = EventForm
    template_name = 'scheduler/event_form.html'
    success_url = reverse_lazy('scheduler:event_list')


# =====================
# EVENT DELETE (ADMIN ONLY)
# =====================
@method_decorator([login_required, user_passes_test(admin_required)], name='dispatch')
class EventDeleteView(DeleteView):
    model = Event
    template_name = 'scheduler/event_confirm_delete.html'
    success_url = reverse_lazy('scheduler:event_list')


# =====================
# FRONT PAGE (Redirects depending on role)
# =====================
@login_required
def frontpage(request):
    if request.user.is_staff:
        return render(request, 'scheduler/admin_dashboard.html')
    else:
        return render(request, 'scheduler/user_dashboard.html')


# =====================
# ADMIN APPROVALS
# =====================
@user_passes_test(lambda u: u.is_staff)
def admin_approvals(request):
    pending_events = Event.objects.filter(is_approved=False)
    return render(request, 'scheduler/admin_approvals.html', {'pending_events': pending_events})


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


# =====================
# AUTHENTICATION
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")  # can be your 'ID' field
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            if user.is_staff:
                return redirect('scheduler:admin_approvals')
            else:
                return redirect('scheduler:event_list')
        else:
            messages.error(request, "Invalid ID or password.")
    return render(request, "scheduler/login.html")


def logout_view(request):
    logout(request)
    return redirect('scheduler:role_select')


# =====================
# ROLE SELECTION PAGE
# =====================
def role_select(request):
    return render(request, 'role_select.html')

def admin_dashboard(request):
    return render(request, 'scheduler/admin_dashboard.html')

@user_passes_test(lambda u: u.is_staff)
def admin_approvals(request):
    pending_events = Event.objects.filter(is_approved=False)
    return render(request, 'scheduler/admin_approvals.html', {'pending_events': pending_events})

def add_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('scheduler:event_list')  # redirect to event list after saving
    else:
        form = EventForm()

    return render(request, 'scheduler/add_event.html', {'form': form})

def edit_event(request, event_id):
    event = get_object_or_404(Event, pk=event_id)

    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            return redirect('scheduler:event_list')  # redirect to event list or dashboard
    else:
        form = EventForm(instance=event)

    return render(request, 'scheduler/edit_event.html', {'form': form, 'event': event})

def delete_event(request, event_id):
    event = get_object_or_404(Event, pk=event_id)

    if request.method == 'POST':
        event.delete()
        return redirect('scheduler:event_list')  # redirect to list after deletion

    return render(request, 'scheduler/delete_event.html', {'event': event})

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Event
from django.contrib import messages

def add_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.is_approved = False  # Needs admin approval
            # For public users, created_by can be None
            event.created_by = None
            event.save()
            return render(request, 'scheduler/thank_you.html')  # Optional thank you page
    else:
        form = EventForm()
    return render(request, 'scheduler/add_event.html', {'form': form})

    return render(request, 'scheduler/add_event.html')

@method_decorator(login_required, name='dispatch')
class EventCreateView(CreateView):
    model = Event
    form_class = EventForm
    template_name = 'scheduler/event_form.html'
    success_url = reverse_lazy('scheduler:event_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        # Auto-approve only for admin
        form.instance.is_approved = self.request.user.is_staff
        form.instance.status = 'Approved' if self.request.user.is_staff else 'Pending'
        return super().form_valid(form)
    
    # Only admin users can access
@user_passes_test(lambda u: u.is_staff)
def admin_approvals(request):
    pending_events = Event.objects.filter(is_approved=False).order_by('-start_time')
    return render(request, 'scheduler/admin_approvals.html', {'all_events': pending_events})
