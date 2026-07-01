from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.models import User

from apps.accounts.models import UserProfile


class SignupForm(forms.Form):
    name = forms.CharField(max_length=150)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput, min_length=8)
    confirm_password = forms.CharField(widget=forms.PasswordInput, min_length=8)

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email=email).exists() or User.objects.filter(username=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("password") != cleaned.get("confirm_password"):
            self.add_error("confirm_password", "Passwords do not match.")
        return cleaned

    def save(self):
        email = self.cleaned_data["email"]
        name_parts = self.cleaned_data["name"].strip().split(" ", 1)
        user = User.objects.create_user(
            username=email,
            email=email,
            password=self.cleaned_data["password"],
            first_name=name_parts[0],
            last_name=name_parts[1] if len(name_parts) > 1 else "",
        )
        return user


class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned = super().clean()
        email = cleaned.get("email", "").lower()
        password = cleaned.get("password")
        if email and password:
            user = authenticate(self.request, username=email, password=password)
            if user is None:
                raise forms.ValidationError("Invalid credentials.")
            cleaned["user"] = user
        return cleaned


class ProfileSetupForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            "age",
            "sex",
            "weight_kg",
            "height_cm",
            "activity_level",
            "fitness_goal",
            "dietary_preference",
            "allergies",
        ]
        widgets = {
            "allergies": forms.Textarea(attrs={"rows": 3}),
        }
