from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

from expenses.managers import UserScopedManager

# 🧑‍💼 Custom user model
class CustomUser(AbstractUser):
    email = models.EmailField(blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    profession = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    has_wife = models.BooleanField(default=False)
    kids = models.PositiveIntegerField(default=0)
    expected_monthly_income = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return self.username

# 💰 Income model
class Income(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='incomes')
    amount = models.PositiveIntegerField(default=0)
    date = models.DateField(default=timezone.now)

    objects = UserScopedManager()


    def save(self, *args, **kwargs):
        if not self.user:
            self.user = getattr(self, '_current_user', self.user)

        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"{self.user.username} - {self.date}: {self.amount}"

    class Meta:
        ordering = ['-date']

# 🗂️ Group model (category container)
class Group(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    order = models.PositiveIntegerField()
    is_deleted = models.BooleanField(default=False)

    # Internal logic fields
    code = models.CharField(max_length=50, blank=True, null=True)
    protected = models.BooleanField(default=False)

    objects = UserScopedManager()

    def save(self, *args, **kwargs):
        if not self.user:
            self.user = getattr(self, '_current_user', self.user)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['order']
        unique_together = ('user', 'code')  # ensures code is unique per user

    def __str__(self):
        return self.name

# 🏷️ Label model (subcategory with budget)
class Label(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='labels')
    name = models.CharField(max_length=100)
    expected_monthly = models.PositiveIntegerField(default=0)
    order = models.PositiveIntegerField()
    is_deleted = models.BooleanField(default=False)


    objects = UserScopedManager()


    def save(self, *args, **kwargs):
        if not self.user:
            self.user = getattr(self, '_current_user', self.user)
        super().save(*args, **kwargs)
        
    class Meta:
        ordering = ['order']
        unique_together = ('user', 'group', 'name')

    def __str__(self):
        return self.name

# 💸 Expense model
class Expense(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    label = models.ForeignKey(Label, on_delete=models.CASCADE, related_name='expenses')
    date = models.DateField(default=timezone.now)
    amount = models.PositiveIntegerField()

    objects = UserScopedManager()


    def save(self, *args, **kwargs):
        if not self.user:
            self.user = getattr(self, '_current_user', self.user)
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"{self.label.name} → {self.amount} on {self.date}"

    class Meta:
        ordering = ['-date']
