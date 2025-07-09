from django.db import models
from django.db.models import Sum, Count, F, Q
from datetime import datetime
from dateutil.relativedelta import relativedelta


class Account(models.Model):
    name = models.CharField(max_length=100)
    balance = models.FloatField(default=0)
    income = models.FloatField(default=0)
    expense = models.FloatField(default=0)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    saving_goal = models.FloatField(default=0)
    liability_list = models.ManyToManyField('Liability', blank=True)
    salary = models.FloatField(default=0)

    def __str__(self):
        return f"{self.name} ({self.user.username})"


class Liability(models.Model):
    name = models.CharField(max_length=100)
    amount = models.FloatField(default=0)
    date = models.DateField(null=False, default=datetime.now().date())
    long_term = models.BooleanField(default=False)
    interest_rate = models.FloatField(default=0, blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    monthly_expense = models.FloatField(default=0, blank=True, null=True)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} - {self.amount}"

    def save(self, *args, **kwargs):
        if self.long_term:
            self.monthly_expense = self.calculate_monthly_expense()
        else:
            self.monthly_expense = self.amount
        super(Liability, self).save(*args, **kwargs)

    def calculate_monthly_expense(self):
        if self.long_term:
            if not self.end_date:
                return None  # Avoid crashing

            duration_days = (self.end_date - self.date).days
            months = max(1, duration_days // 30)  # At least 1 month

            if self.interest_rate in [None, 0]:
                return round(self.amount / months, 2)
            else:
                monthly_rate = self.interest_rate / 12 / 100
                try:
                    monthly_expense = (self.amount * monthly_rate) / (1 - (1 + monthly_rate) ** -months)
                    return round(monthly_expense, 2)
                except ZeroDivisionError:
                    return round(self.amount / months, 2)
        else:
            return self.amount  # For short-term liabilities
