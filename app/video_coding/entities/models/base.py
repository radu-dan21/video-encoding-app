from django.db import models


class BaseModel(models.Model):
    MAX_CHAR_FIELD_LEN = 1999

    class Meta:
        abstract = True
        ordering = ["-id"]

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.name} <{self.id}>"
