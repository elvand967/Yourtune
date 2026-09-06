
# apps/users/adapters.py

from allauth.account.models import EmailAddress
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.models import SocialLogin


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin: SocialLogin):
        if sociallogin.is_existing:
            return

        email = sociallogin.user.email
        if not email:
            return

        try:
            email_address = EmailAddress.objects.get(email__iexact=email, verified=True)
        except EmailAddress.DoesNotExist:
            return

        sociallogin.connect(request, email_address.user)