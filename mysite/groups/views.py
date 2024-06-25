from typing import Any
from django.db.models.base import Model as Model
from django.db.models.query import QuerySet
from django.forms import BaseModelForm
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden
from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, View
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.edit import FormMixin
from django.urls import reverse_lazy
from django.utils.text import slugify
from .models import Group
from .forms import CreateGroupForm
from polls.utils import get_index_context

# Create your views here.

class GroupListView(ListView):
    model = Group
    template_name = 'groups/group_list.html'
    context_object_name = 'groups'

class GroupDetailView(DetailView):
    model = Group
    template_name = 'groups/group_detail.html'
    context_object_name = 'group'

    def get_context_data(self, **kwargs: Any):
        context = super().get_context_data(**kwargs)
        group = self.get_object()
        context['create_group_form'] = CreateGroupForm(instance=group)
        return context

class JoinGroupView(DetailView):
    model = Group
    template_name = 'groups/group_detail.html'
    context_object_name = 'group'

    def get(self, request, *args, **kwargs):
        group = self.get_object()
        group.members.add(request.user)
        return redirect('groups:group_detail', group.slug)

class LeaveGroupView(DetailView):
    model = Group
    template_name = 'groups/group_detail.html'
    context_object_name = 'group'

    def get(self, request, *args, **kwargs):
        group = self.get_object()
        group.members.remove(request.user)
        return redirect('groups:group_detail', group.slug)

class CreateGroupView(CreateView):

    model = Group
    form_class = CreateGroupForm
    template_name = 'polls/index.html'

    def get_success_url(self):
        return reverse_lazy('groups:group_detail', kwargs={'slug': self.object.slug})
    
    def form_invalid(self, form: BaseModelForm):
        context = self.get_context_data(form=form)
        context['create_group_form'] = form
        context.update(get_index_context(context))
        return self.render_to_response(context)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class EditGroupView(UpdateView):
    model = Group
    form_class = CreateGroupForm
    template_name = 'groups/group_detail.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def get_object(self, queryset: QuerySet[Any] | None = ...) -> Model:
        return Group.objects.get(slug=self.kwargs['slug'])
    
    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        self.object = form.save(commit=False)
        self.object.slug = slugify(self.object.name)
        self.object.save()
        return super().form_valid(form)
    
    def form_invalid(self, form: BaseModelForm) -> HttpResponse:
        context = self.get_context_data(form=form)
        context.update({'create_group_form': form})
        return self.render_to_response(context)
    
    def get_success_url(self):
        return reverse_lazy('groups:group_detail', kwargs={'slug': self.object.slug})

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        self.object = self.get_object()
        if not self.object.is_member(user=self.request.user):
            return HttpResponseForbidden("You are not allowed to edit this group")
        return super().dispatch(request, *args, **kwargs)


class DeleteGroupView(DeleteView):
    model = Group
    success_url = reverse_lazy('polls:index')
    
    def get_object(self, queryset: QuerySet[Any] | None = ...) -> Model:
        return Group.objects.get(slug=self.kwargs['slug'])
    

class GroupView(View):
    def get(self, request, *args, **kwargs):
        view = GroupDetailView.as_view()
        return view(request, *args, **kwargs)
    def post(self, request, *args, **kwargs):
        view = EditGroupView.as_view()
        return view(request, *args, **kwargs)