from django.db import models
from django.contrib.auth.models import User

class Prediction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    input_data = models.TextField()
    prediction_result = models.CharField(max_length=50)
    predicted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.prediction_result} - {self.predicted_at.strftime('%Y-%m-%d %H:%M')}"
