
from django.db import models

class SensorData(models.Model):
    image = models.ImageField(upload_to='images/', null=True, blank=True)
    lidar_data = models.TextField()  # JSON olarak saklanabilir
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"SensorData {self.id} - {self.timestamp}"
