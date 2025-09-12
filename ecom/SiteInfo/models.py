from django.db import models

# Create your models here.

class Contact(models.Model):
    fn = models.CharField(default="", max_length=50, verbose_name="First Name")
    ln = models.CharField(default="", max_length=50, verbose_name="Last Name")
    email = models.CharField(default="", max_length=50)
    phone = models.IntegerField(default=0000000000)
    msg = models.TextField(default="", verbose_name="Message")
    ss = models.ImageField(upload_to="ContactSS", default="", verbose_name="Screenshot")

    def __str__(self):
        return f"{self.fn} {self.ln}"

    class Meta:
        verbose_name_plural = "User Queries"
