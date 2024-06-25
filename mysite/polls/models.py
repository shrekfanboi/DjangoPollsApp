from django.db import models
from django.core import validators
from django.contrib.auth.models import AbstractUser
from markdownx.models import MarkdownxField
from markdownx.utils import markdownify
# Create your models here.

class User(AbstractUser):

    first_name = models.CharField(
        max_length=100, blank=True, 
        validators=[
            validators.RegexValidator(r'^[a-zA-Z]*$', 'Only Alphabets are allowed.')
        ]
    )
    last_name = models.CharField(
        max_length=100, blank=True,
        validators=[
            validators.RegexValidator(r'^[a-zA-Z]*$', 'Only Alphabets are allowed.')
        ]
    )
    email = models.EmailField(max_length=100, unique=True)
    username = models.CharField(
        max_length=50, unique=True,
        validators=[
            validators.MinLengthValidator(3,'Username must be at least 3 characters long.'),
            validators.RegexValidator(r'^[^\W_](\w)*$', 'Username should not start with a special character.'),
        ]
    )
    password = models.CharField(max_length=150)
    avatar = models.ImageField(upload_to='polls/', blank=True, default="polls/default-avatar.png")
    followers = models.ManyToManyField("self", symmetrical=False, related_name="following", blank=True)

    def __str__(self) -> str:
        return f"User {self.username}"
    
class Blog(models.Model):

    title = models.CharField(max_length=150)
    content = MarkdownxField(blank=True, help_text="Markdown is supported.")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="authored_blogs")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    comments = models.ManyToManyField(User, through="Comment", related_name="commented_blogs")
    views = models.ManyToManyField(User, related_name="viewed_blogs", blank=True)
    likes = models.ManyToManyField(User, related_name="liked_blogs", blank=True)
    dislikes = models.ManyToManyField(User, related_name="disliked_blogs", blank=True)
    groups = models.ManyToManyField("groups.Group", related_name="blogs", blank=True)

    @property
    def formatted_markdown(self):
        return markdownify(self.content)

    def __str__(self):
        return f"Blog {self.title} by {self.author}"

class Comment(models.Model):

    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="authored_comments")
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name="blog_comments") 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(User, related_name="liked_comments", blank=True)
    dislikes = models.ManyToManyField(User, related_name="disliked_comments", blank=True)

    def __str__(self) -> str:
        return f"Comment by {self.author} on {self.blog}"
 
