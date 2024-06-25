def redirect_authenticated_user(user):
    return not user.is_authenticated