from django.db import models
from django.utils.text import slugify
from django.contrib.auth import get_user_model

User = get_user_model()
# Create your models here.

class Group(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, default='')
    slug = models.SlugField(allow_unicode=True, unique=True, blank=True)
    members = models.ManyToManyField(User, related_name='joined_groups', blank=True)
    profile = models.ImageField(upload_to='groups/', blank=True, default="groups/default-group.png")


    def get_absolute_url(self):
        return f"/polls/groups/{self.slug}/"

    def save(self, *args, **kwargs):
        self.slug = self.slug or slugify(self.name)
        super().save(*args, **kwargs)

    def is_member(self, user):
        return self.members.filter(pk=user.pk).exists()

    def __str__(self):
        return self.name
    