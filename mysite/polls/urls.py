from django.urls import path, re_path
from django.conf.urls import include
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from . import views, forms

app_name = "polls"

urlpatterns = [
    path('', views.PollsView.as_view(), name="index"),
    path('about/', TemplateView.as_view(template_name="polls/about.html"), name="about"),
    path('profile/<str:username>/', views.UserProfileView.as_view(), name="user_profile"),
    path('profile/<str:username>/follow/', views.FollowUserView.as_view(), name="follow_user"),
    path('profile/<str:username>/unfollow/', views.FollowUserView.as_view(), name="unfollow_user"),
    path('post/<int:pk>/', views.BlogDetailView.as_view(), name="blog_detail"),
    path('post/<int:pk>/edit/', login_required(views.UpdateBlogView.as_view()), name="edit_blog"),
    path('post/<int:pk>/post-comment/', views.CreateCommentView.as_view(), name="post_comment"),
    path('post/<int:pk>/like/', views.LikeBlogView.as_view(), name="like_blog"),
    path('post/<int:pk>/dislike/', views.DislikeBlogView.as_view(), name="dislike_blog"),
    path('post/<int:blog_id>/comment/<int:comment_id>/like/', views.LikeCommentView.as_view(), name="like_comment"),
    path('post/<int:blog_id>/comment/<int:comment_id>/dislike/', views.DislikeCommentView.as_view(), name="dislike_comment"),
    path('post/<int:pk>/delete/', views.DeleteBlogView.as_view(), name="delete_blog"),
    path('create-blog/', login_required(views.CreateBlogView.as_view()), name="create_blog"),
    path('edit-profile/', login_required(views.EditProfileView.as_view()), name="edit_profile"),
    path('help/', TemplateView.as_view(template_name="polls/help.html"), name="help"),
    path('register/', views.RegisterUserView.as_view(), name="register"),
    path('login/', views.LoginUserView.as_view(), name="login"),
    path('logout/', login_required(auth_views.LogoutView.as_view()), name="logout"),
    path('reset-password/', views.MyPasswordResetView.as_view(), name="password_reset"),
    path('reset-password-sent/', auth_views.PasswordResetDoneView.as_view(template_name="polls/reset_password_sent.html"), name="password_reset_done"),
    path('reset-password-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name="polls/reset_password_confirm.html", form_class=forms.CustomSetPasswordForm), name="password_reset_confirm"),
    path('reset-password-complete/', auth_views.PasswordResetCompleteView.as_view(template_name="polls/reset_password_complete.html"), name='password_reset_complete'),
    path('change-password/', login_required(auth_views.PasswordChangeView.as_view(template_name="polls/change_password.html", form_class=forms.CustomPasswordChangeForm)), name="change_password"),
    path('change-password-done/', auth_views.PasswordChangeDoneView.as_view(template_name="polls/change_password_done.html"), name="password_change_done"),
    path('delete-user/', login_required(views.UserDeleteView.as_view()), name="delete_user"),
]
