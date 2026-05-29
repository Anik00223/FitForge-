from django.db import models


class FitForge(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "FitForge"
