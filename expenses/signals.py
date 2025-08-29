# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from .models import Label, Group, CustomUser

# @receiver(post_save, sender=Label)
# def update_annual_expense_totals(sender, instance, **kwargs):
#     group = instance.group
#     user = instance.user

#     if group.name == 'النفقات السنوية':
#         labels = Label.objects.filter(group=group, user=user, is_deleted=False)
#         total = sum(label.expected_monthly for label in labels)

#         user.expected_annual_expenses = total
#         user.expected_annual_divided_monthly = round(total / 12)
#         user.save()
