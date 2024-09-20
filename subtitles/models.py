from django.db import models

class Video(models.Model):
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='videos/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Subtitle(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    language = models.CharField(max_length=20, default="English")
    start_time = models.CharField(max_length=12)
    end_time = models.CharField(max_length=12)
    phrase = models.TextField(db_index=True)
    file = models.FileField(upload_to='subtitles/', blank=True, null=True)

    def __str__(self):
        return f"{self.language} - {self.video.title}"
