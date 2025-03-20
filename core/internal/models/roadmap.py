from django.db import models


class RoadmapItem(models.Model):
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=100)
    description = models.TextField()
    date = models.DateField()

    class Meta:
        verbose_name = "INT_RoadmapItem"
        verbose_name_plural = "INT_RoadmapItems"
        ordering = ["-date"]

    def __str__(self):
        return "roadmapItem: {};".format(self.title)
