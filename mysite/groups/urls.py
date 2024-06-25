from django.urls import path, re_path
from django.conf.urls import include
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from . import views

app_name = "groups"

urlpatterns = [
    path('', views.GroupListView.as_view(), name="group_list"),
    path('<slug:slug>/', views.GroupView.as_view(), name="group_detail"),
    path('<slug:slug>/delete', login_required(views.DeleteGroupView.as_view()), name="delete_group"),
    path('<slug:slug>/join/', login_required(views.JoinGroupView.as_view()), name="join_group"),
    path('<slug:slug>/leave/', login_required(views.LeaveGroupView.as_view()), name="leave_group"),
]