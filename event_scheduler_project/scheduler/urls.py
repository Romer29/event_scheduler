from django.urls import path
from . import views

app_name = 'scheduler'

urlpatterns = [
    path('', views.role_select, name='role_select'),
    path('events/', views.EventListView.as_view(), name='event_list'),
    path('event/<int:pk>/', views.EventDetailView.as_view(), name='event_detail'),
    path('user-login/', views.user_login_view, name='user_login'),
    path('event-view/', views.student_event_view, name='student_event_view'),
    path('event-add/', views.student_event_add, name='student_event_add'),
    path('student-events/', views.StudentEventView.as_view(), name='student_event_list'),
    path('student-events/add/', views.StudentEventCreateView.as_view(), name='student_event_create'),
    path('student-events/<int:pk>/', views.StudentEventDetailView.as_view(), name='student_event_detail'),
    path('event/create/', views.EventCreateView.as_view(), name='event_create'),
    path('event/<int:pk>/update/', views.EventUpdateView.as_view(), name='event_update'),
    path('event/<int:pk>/delete/', views.EventDeleteView.as_view(), name='event_delete'),
    path('event/add/', views.add_event, name='add_event'),
    path('event/edit/<int:event_id>/', views.edit_event, name='edit_event'),
    path('event/delete/<int:event_id>/', views.delete_event, name='delete_event'),
    path('dashboard/approvals/', views.admin_approvals, name='admin_approvals'),
    path('dashboard/approve/<int:pk>/', views.approve_event, name='approve_event'),
    path('dashboard/reject/<int:pk>/', views.reject_event, name='reject_event'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]