from django import forms

from apps.tracker.models import BMILog, WorkoutLog


class BMILogForm(forms.ModelForm):
    class Meta:
        model = BMILog
        fields = ["weight_kg", "height_cm"]


class WorkoutLogForm(forms.ModelForm):
    class Meta:
        model = WorkoutLog
        fields = ["exercise", "sets", "reps", "weight_kg", "notes"]
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 2}),
        }
