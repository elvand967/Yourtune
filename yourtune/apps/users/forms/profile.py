
# apps/users/forms/profile.py

from django import forms

from apps.users.models import Profile


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = (
            "avatar",
            "gender",
            "date_of_birth",
            "voice_preference",
            "bio",
            "location",
            "website",
            "language",
            "timezone",
            "is_public",
        )
        widgets = {
            "date_of_birth": forms.DateInput(attrs={"type": "date"}),
            "bio": forms.Textarea(attrs={"rows": 4}),
        }