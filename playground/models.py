from django.db import models
from django.utils import timezone


class Message(models.Model):
	text = models.TextField()
	sender = models.CharField(max_length=100)
	timestamp = models.DateTimeField(default=timezone.now)

	class Meta:
		ordering = ['-timestamp']

	def __str__(self):
		return f"{self.sender}: {self.text[:50]}"
