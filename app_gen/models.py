from django.db import models
from django.contrib.auth.models import User

class ContentGenerationLog(models.Model):
    title = models.CharField(max_length=200)
    objective = models.TextField()
    data = models.TextField()
    return_format = models.CharField(max_length=200)
    response = models.TextField()
    model_used = models.CharField(max_length=100)
    temperature = models.FloatField()
    prompt_tokens = models.IntegerField()
    completion_tokens = models.IntegerField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']