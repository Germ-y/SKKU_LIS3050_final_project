from django.db import models

class Paper(models.Model):
    title = models.CharField(max_length=500)
    authors = models.CharField(max_length=500, blank=True)
    category = models.CharField(max_length=200, blank=True)
    detail_url = models.URLField(blank=True, null=True)
    pdf_url = models.URLField(blank=True, null=True)


    def __str__(self):
        return self.title
