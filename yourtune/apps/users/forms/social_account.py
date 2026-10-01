
# apps/users/forms/social_account.py

from django import forms

from apps.users.models import SocialAccount


class SocialAccountForm(forms.ModelForm):
    class Meta:
        model = SocialAccount
        fields = ("user", "provider", "provider_uid", "email", "extra_data", "is_primary")
        widgets = {
            "extra_data": forms.Textarea(attrs={"rows": 6}),
        }