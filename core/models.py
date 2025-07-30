from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import User
from django.http import HttpRequest


class LogSystem(models.Model):
    """
    Stores internal server errors (500-level) triggered during request handling.

    This model is fed by a custom logging handler and holds critical error info
    including traceback and the logger/module that triggered the event.
    """
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # Request metadata
    request_path = models.CharField(max_length=500)
    request_method = models.CharField(max_length=10)
    request_data = models.JSONField(blank=True, null=True)
    # Logger context
    logger_name = models.CharField(max_length=255)        # e.g., __name__
    module = models.CharField(max_length=255, blank=True) # optional: record calling module
    function_name = models.CharField(max_length=255, blank=True)  # optional: calling func

    # Traceback of the actual error
    traceback = models.TextField()

    def __str__(self):
        return f"{self.logger_name} | {self.request_path} | {self.timestamp:%Y-%m-%d %H:%M}"
