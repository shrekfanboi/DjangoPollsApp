from django.db.models import Count
from groups.models import Group
from polls.models import Blog
from groups.forms import CreateGroupForm

def get_index_context(context):
    return {
        'groups': Group.objects.annotate(
            num_members=Count('members'), num_posts=Count('blogs')
        ).order_by('-num_members', '-num_posts'),
        'blogs': context.get(
            'blogs', Blog.objects.all().order_by('-created_at')
        ),
        'create_group_form': context.get(
            'create_group_form', CreateGroupForm()
        ),
    }