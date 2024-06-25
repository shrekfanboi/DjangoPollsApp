from typing import Any
from django.db.models.base import Model as Model
from django.db.models.query import QuerySet
from django.forms import BaseModelForm
from django.http.response import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404, HttpRequest, HttpResponse
from django.views.generic import DetailView, ListView
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.contrib.auth.hashers import make_password
from django.views.generic import View
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.views import LoginView, PasswordResetView
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic.edit import ModelFormMixin, FormMixin
from django.db.models import Count
from polls.models import User, Blog, Comment
from polls.forms import (
    LoginForm, UserModelForm, CustomPasswordResetForm, EditUserProfileForm,
    BlogCreateForm
)
from groups.models import Group
from groups.forms import CreateGroupForm
from groups.views import CreateGroupView
from .utils import get_index_context

class IndexView(ListView):
    model = Blog
    template_name = 'polls/index.html'
    context_object_name = 'blogs'
    ordering = ['-created_at']

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super(ListView, self).get_context_data(**kwargs)
        context.update(get_index_context(context))
        return context

class PollsView(View):
    def get(self, request, *args, **kwargs):
        index_view = IndexView.as_view()
        return index_view(request, *args, **kwargs)
    def post(self, request, *args, **kwargs):
        create_view = CreateGroupView.as_view()
        return create_view(request, *args, **kwargs)
    
class BlogDetailView(DetailView):
    model = Blog
    template_name = 'polls/blog_detail.html'
    context_object_name = 'blog'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        blog = self.object

        if request.user.is_authenticated and not blog.views.filter(id=request.user.id).exists():
            blog.views.add(request.user)
            blog.save()
        return super().get(request, *args, **kwargs)

    

class CreateBlogView(CreateView):
    model = Blog
    form_class = BlogCreateForm
    template_name = 'polls/create_blog.html'
    success_url = reverse_lazy('polls:index')
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        group_slug = self.request.GET.get('group')
        kwargs.update({'user': self.request.user})
        if group_slug:
            group = get_object_or_404(Group, slug=group_slug)
            kwargs.update({'group': group})
        return kwargs

class UpdateBlogView(UpdateView):
    model = Blog
    form_class = BlogCreateForm
    template_name = 'polls/create_blog.html'

    def get_success_url(self) -> str:
        return reverse_lazy('polls:blog_detail', kwargs={'pk': self.object.id})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()  
        kwargs.update({'user': self.request.user})
        return kwargs

class DeleteBlogView(View):
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'redirect': reverse_lazy("polls:login")}, status=401)
        blog = get_object_or_404(Blog, pk=kwargs.get('pk'))
        blog.delete()
        return JsonResponse({'success': True, 'redirect': reverse_lazy("polls:index")}, status=200)

class UserProfileView(DetailView):
    model = User
    template_name = 'polls/user_profile.html'

    def get_object(self, queryset=None):
        username = self.kwargs.get('username')
        return get_object_or_404(User, username=username)

class EditProfileView(UpdateView):
    model = User
    form_class=  EditUserProfileForm
    template_name = 'polls/edit_profile.html'

    def get_success_url(self):
        return reverse_lazy('polls:user_profile', kwargs={'username': self.request.user.username})

    def get_object(self, queryset=None):
        return self.request.user
    
    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs


class RegisterUserView(UserPassesTestMixin, CreateView):
    model = User
    form_class = UserModelForm
    template_name = 'polls/register.html'
    success_url = reverse_lazy('polls:index')
    

    def form_valid(self, form):
        response = super().form_valid(form)
        user = self.object
        login(self.request, user, backend='django.contrib.auth.backends.ModelBackend')
        return response
    
    def test_func(self):
        return not self.request.user.is_authenticated
    
    def handle_no_permission(self):
        return redirect('polls:index')

class LoginUserView(LoginView):
    template_name = 'polls/login.html'
    authentication_form = LoginForm
    redirect_authenticated_user = True    

class MyPasswordResetView(UserPassesTestMixin, PasswordResetView):
    template_name = 'polls/reset_password.html'
    form_class = CustomPasswordResetForm

    def test_func(self):
        return not self.request.user.is_authenticated
    
    def handle_no_permission(self):
        return redirect('index')

class UserDeleteView(View):
    def post(self, request, *args, **kwargs):
        user = self.request.user
        user.delete()
        logout(request)
        return JsonResponse({'success': True, 'redirect':'/polls/'}, status=200)

class CreateCommentView(View):
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'redirect': reverse_lazy("login")}, status=401)
        blog = get_object_or_404(Blog, pk=kwargs.get('pk'))
        comment_content = request.POST.get('comment')
        comment = Comment.objects.create(
            blog=blog, author=request.user, content=comment_content
        )
        return render(request, 'polls/comment.html', {'comment': comment})

class LikeBlogView(View):
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'redirect': reverse_lazy("login")}, status=401)
        blog = get_object_or_404(Blog, pk=kwargs.get('pk'))
        user = request.user
        if blog.dislikes.filter(id=user.id).exists():
            blog.dislikes.remove(user)
        if blog.likes.filter(id=user.id).exists():
            blog.likes.remove(user)
        else:
            blog.likes.add(user)
        return JsonResponse({'success': True, 'likes': blog.likes.count(), 'dislikes': blog.dislikes.count()}, status=200)
    
class DislikeBlogView(View):
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'redirect': reverse_lazy("login")}, status=401)
        blog = get_object_or_404(Blog, pk=kwargs.get('pk'))
        user = request.user
        if blog.likes.filter(id=user.id).exists():
            blog.likes.remove(user)
        if blog.dislikes.filter(id=user.id).exists():
            blog.dislikes.remove(user)
        else:
            blog.dislikes.add(user)
        return JsonResponse({'success': True, 'dislikes': blog.dislikes.count(), 'likes': blog.likes.count()}, status=200)

class LikeCommentView(View):
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'redirect': reverse_lazy("login")}, status=401)
        comment = get_object_or_404(Comment, pk=kwargs.get('comment_id'))
        user = request.user
        if comment.dislikes.filter(id=user.id).exists():
            comment.dislikes.remove(user)
        if comment.likes.filter(id=user.id).exists():
            comment.likes.remove(user)
        else:
            comment.likes.add(user)
        return JsonResponse({'success': True, 'likes': comment.likes.count(), "dislikes": comment.dislikes.count()}, status=200)

class DislikeCommentView(View):
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'redirect': reverse_lazy("login")}, status=401)
        comment = get_object_or_404(Comment, pk=kwargs.get('comment_id'))
        user = request.user
        if comment.likes.filter(id=user.id).exists():
            comment.likes.remove(user)
        if comment.dislikes.filter(id=user.id).exists():
            comment.dislikes.remove(user)
        else:
            comment.dislikes.add(user)
        return JsonResponse({'success': True, 'dislikes': comment.dislikes.count(), 'likes': comment.likes.count()}, status=200)

class FollowUserView(View):
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'redirect': reverse_lazy("login")}, status=401)
        user = get_object_or_404(User, pk=request.POST.get('user_id'))
        action = request.POST.get('action')
        if action == 'follow' and not user.followers.filter(id=request.user.id).exists():
            user.followers.add(request.user)
        elif action == 'unfollow' and user.followers.filter(id=request.user.id).exists():
            user.followers.remove(request.user)
        else:
            return JsonResponse({'success': False}, status=400)
        return JsonResponse({'success': True, 'followers': user.followers.count()}, status=200)
        