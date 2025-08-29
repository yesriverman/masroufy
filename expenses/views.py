from collections import defaultdict
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum, Max, Prefetch
from django.urls import reverse
from .models import CustomUser, Expense, Group, Income, Label
from .forms import (
    AnnualLabelAddForm, AnnualLabelForm, CustomUserCreationForm, ExpectedMonthlyForm, ExpectedMonthlyIncomeForm,  ExpenseForm, FixedLabelAddForm,
    GroupForm, IncomeForm, LabelExpenseFormSet, LabelForm, ProfileForm,
     MonthlyVariableExpenseForm, StyledAuthenticationForm,MonthlyFixedExpectedForm,AnnualExpectedForm
)
from .utils import create_default_categories
from datetime import date, timedelta
from django.utils import timezone

# 🔐 Auth Views
def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            create_default_categories(user)
            login(request, user)
            return redirect('expected_monthly_income_view')
    else:
        form = CustomUserCreationForm()
    return render(request, 'auths/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = StyledAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('home')
    else:
        form = StyledAuthenticationForm()
    return render(request, 'auths/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

def custom_404_view(request, exception=None):
    return redirect('home' if request.user.is_authenticated else 'login')



@login_required
def income_list(request):
    incomes = Income.objects.filter(user=request.user).order_by('-date')
    return render(request, 'income/income_list.html', {'incomes': incomes})

@login_required
def income_add(request):
    next_url = request.GET.get('next') or request.POST.get('next') or reverse('income_list')

    if request.method == 'POST':
        form = IncomeForm(request.POST)
        if form.is_valid():
            income = form.save(commit=False)
            income.user = request.user
            income.save()
            return redirect(next_url)
    else:
        form = IncomeForm(initial={'date': date.today()})

    return render(request, 'income/income_form.html', {
        'form': form,
        'title': '➕ إضافة دخل جديد',
        'next': next_url
    })

@login_required
def income_edit(request, income_id):
    next_url = request.GET.get('next') or request.POST.get('next') or reverse('income_list')
    income = get_object_or_404(Income, id=income_id, user=request.user)

    if request.method == 'POST':
        form = IncomeForm(request.POST, instance=income)
        if form.is_valid():
            form.save()
            return redirect(next_url)
    else:
        form = IncomeForm(instance=income)

    return render(request, 'income/income_form.html', {
        'form': form,
        'title': '✏️ تعديل الدخل',
        'next': next_url,
        'income': income
    })

@login_required
def income_delete(request, income_id):
    next_url = request.GET.get('next') or request.POST.get('next') or reverse('income_list')
    income = get_object_or_404(Income, id=income_id, user=request.user)

    if request.method == 'POST':
        income.delete()
        return redirect(next_url)

    return render(request, 'income/income_confirm_delete.html', {
        'income': income,
        'title': '🗑️ تأكيد الحذف',
        'next': next_url
    })



@login_required
def group_list(request):
    groups = Group.objects.filter(user=request.user, is_deleted=False)
    return render(request, 'group/group_list.html', {'groups': groups})

@login_required
def group_add(request):
    next_url = request.GET.get('next') or reverse('group_list')
    form = GroupForm(request.POST or None, user=request.user)

    if request.method == 'POST' and form.is_valid():
        group = form.save(commit=False)
        group.user = request.user
        group.order = (Group.objects.filter(user=request.user, is_deleted=False)
                       .aggregate(Max('order'))['order__max'] or 0) + 1
        group.save()
        
        return redirect(next_url)

    deleted_groups = Group.objects.filter(user=request.user, is_deleted=True)
    return render(request, 'group/group_form.html', {
        'form': form,
        'deleted_groups': deleted_groups,
        'next_url': next_url
    })

@login_required
def group_edit(request, group_id):
    next_url = request.GET.get('next') or reverse('group_list')
    group = get_object_or_404(Group, id=group_id, user=request.user)

    if group.is_deleted:
        return redirect(next_url)

    form = GroupForm(request.POST or None, instance=group, user=request.user)

    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect(next_url)

    return render(request, 'group/group_form.html', {
        'form': form,
        'group': group,
        'next_url': next_url
    })


@login_required
def group_delete(request, group_id):
    next_url = request.GET.get('next') or reverse('group_list')
    group = get_object_or_404(Group, id=group_id, user=request.user, is_deleted=False)

    if group.protected:
        messages.warning(request, "⚠️ لا يمكن حذف هذه المجموعة لأنها محمية.")
        return redirect(next_url)

    if request.method == 'POST':
        group.is_deleted = True
        group.save()

        # Reorder remaining groups
        for i, g in enumerate(Group.objects.filter(user=request.user, is_deleted=False).order_by('order'), start=1):
            g.order = i
            g.save()

        messages.success(request, f"✅ تم حذف المجموعة: {group.name}")
        return redirect(next_url)

    return render(request, 'group/group_confirm_delete.html', {
        'group': group,
        'next_url': next_url
    })

@login_required
def group_restore_view(request, group_id):
    next_url = request.GET.get('next') or reverse('group_list')
    group = get_object_or_404(Group, id=group_id, user=request.user)
    form = GroupForm(request.POST or None, instance=group, user=request.user)

    if request.method == 'POST' and form.is_valid():
        group = form.save(commit=False)
        group.order = (Group.objects.filter(user=request.user, is_deleted=False)
                       .aggregate(Max('order'))['order__max'] or 0) + 1
        group.is_deleted = False
        group.save()
        return redirect(next_url)

    return render(request, 'group/group_form.html', {
        'form': form,
        'group': group,
        'next_url': next_url
    })

@login_required
def move_group_up(request, pk):
    next_url = request.GET.get('next') or reverse('group_list')
    group = get_object_or_404(Group, pk=pk, user=request.user)
    above = Group.objects.filter(user=request.user, order__lt=group.order).order_by('-order').first()
    if above:
        group.order, above.order = above.order, group.order
        group.save()
        above.save()
    return redirect(next_url)

@login_required
def move_group_down(request, pk):
    next_url = request.GET.get('next') or reverse('group_list')
    group = get_object_or_404(Group, pk=pk, user=request.user)
    below = Group.objects.filter(user=request.user, order__gt=group.order).order_by('order').first()
    if below:
        group.order, below.order = below.order, group.order
        group.save()
        below.save()
    return redirect(next_url)



# 🏷️ Label Views
@login_required
def label_list(request):
    groups = Group.objects.filter(user=request.user, is_deleted=False).prefetch_related(
        Prefetch('labels', queryset=Label.objects.filter(is_deleted=False).order_by('order'))
    )
    return render(request, 'label/label_list.html', {'groups': groups})

@login_required
def label_add(request):
    user = request.user
    next_url = request.GET.get('next') or request.POST.get('next') or 'label_list'

    form = LabelForm(request.POST or None, user=user)

    if request.method == 'POST' and form.is_valid():
        label = form.save(commit=False)
        
        group = label.group
        max_order = Label.objects.filter(user=user, group=group, is_deleted=False).aggregate(Max('order'))['order__max'] or 0
        label.order = max_order + 1
        
        label.user = user
        label.save()
        return redirect(next_url)

    deleted_labels = Label.objects.filter(user=user, is_deleted=True)
    return render(request, 'label/label_form.html', {
        'form': form,
        'title': '➕ إضافة تسمية فرعية',
        'next': next_url,
        'deleted_labels': deleted_labels
    })

@login_required
def label_edit(request, pk):
    next_url = request.GET.get('next') or request.POST.get('next') or reverse('label_list')
    label = get_object_or_404(Label, pk=pk, user=request.user, is_deleted=False)
    form = LabelForm(request.POST or None, instance=label, user=request.user)

    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect(next_url)

    return render(request, 'label/label_form.html', {
        'form': form,
        'title': '✏️ تعديل التسمية الفرعية',
        'next': next_url,
        'label': label
    })

@login_required
def label_delete(request, pk):
    label = get_object_or_404(Label, pk=pk, user=request.user, is_deleted=False)
    next_url = request.POST.get('next') or request.GET.get('next') or reverse('label_list')

    if request.method == 'POST':
        label.is_deleted = True
        label.save()

        # Reorder remaining labels in the same group
        for i, lbl in enumerate(Label.objects.filter(user=request.user, group=label.group, is_deleted=False).order_by('order'), start=1):
            lbl.order = i
            lbl.save()

        messages.success(request, f"✅ تم حذف التصنيف: {label.name}")
        return redirect(next_url)

    return render(request, 'label/label_confirm_delete.html', {
        'label': label,
        'next_url': next_url
    })

@login_required
def label_restore_view(request, label_id):
    next_url = request.GET.get('next') or request.POST.get('next') or reverse('label_list')
    label = get_object_or_404(Label, id=label_id, user=request.user)
    form = LabelForm(request.POST or None, instance=label, user=request.user)

    if request.method == 'POST' and form.is_valid():
        label = form.save(commit=False)
        max_order = Label.objects.filter(user=request.user, is_deleted=False).aggregate(Max('order'))['order__max'] or 0
        label.order = max_order + 1
        label.is_deleted = False
        label.save()
        return redirect(next_url)

    return render(request, 'label/label_form.html', {
        'form': form,
        'label': label,
        'next': next_url
    })

@login_required
def move_label_up(request, pk):
    next_url = request.GET.get('next') or reverse('label_list')
    label = get_object_or_404(Label, pk=pk, user=request.user, is_deleted=False)
    above = Label.objects.filter(
        user=request.user,
        group=label.group,
        is_deleted=False,
        order__lt=label.order
    ).order_by('-order').first()

    if above:
        label.order, above.order = above.order, label.order
        label.save()
        above.save()

    return redirect(next_url)

@login_required
def move_label_down(request, pk):
    next_url = request.GET.get('next') or reverse('label_list')
    label = get_object_or_404(Label, pk=pk, user=request.user, is_deleted=False)
    below = Label.objects.filter(
        user=request.user,
        group=label.group,
        is_deleted=False,
        order__gt=label.order
    ).order_by('order').first()

    if below:
        label.order, below.order = below.order, label.order
        label.save()
        below.save()

    return redirect(next_url)



from django.shortcuts import render
from .models import Group

def get_labels(request, group_id):
    group = Group.objects.get(pk=group_id)
    labels = group.labels.all()
    return render(request, 'partials/labels_list.html', {'labels': labels})






# 💸 Expense Views
@login_required
def expense_list(request):
    expenses = Expense.objects.filter(user=request.user).select_related('label', 'label__group').order_by('-date')
    return render(request, 'expense/expense_list.html', {'expenses': expenses})

@login_required
def expense_add(request):
    next_url = request.GET.get('next') or request.POST.get('next') or reverse('expense_list')
    form = ExpenseForm(request.POST or None, user=request.user)

    if request.method == 'POST' and form.is_valid():
        expense = form.save(commit=False)
        expense.user = request.user
        expense.save()
        return redirect(next_url)

    return render(request, 'expense/expense_form.html', {
        'form': form,
        'title': '➕ إضافة مصروف',
        'next': next_url
    })

@login_required
def add_expense_view(request):
    next_url = request.GET.get("next") or request.POST.get("next") or reverse("expense_list")
    selected_group_id = request.GET.get("group")

    labels = Label.objects.filter(group_id=selected_group_id, user=request.user, is_deleted=False) if selected_group_id else []

    initial_data = [
        {"label_id": label.id, "label_name": label.name}
        for label in labels
    ]

    formset = LabelExpenseFormSet(initial=initial_data)

    if request.method == "POST":
        formset = LabelExpenseFormSet(request.POST)
        if formset.is_valid():
            for form in formset:
                label_id = form.cleaned_data.get("label_id")
                amount = form.cleaned_data.get("amount")
                if amount:
                    Expense.objects.create(
                        label_id=label_id,
                        amount=amount,
                        date=timezone.now(),
                        user=request.user
                    )
            return redirect(next_url)

    return render(request, "expense/add_expense_form.html", {
        "formset": formset,
        "groups": Group.objects.for_user(request.user),
        "selected_group_id": selected_group_id,
        "next": next_url
    })

@login_required
def expense_edit(request, pk):
    next_url = request.GET.get('next') or request.POST.get('next') or reverse('expense_list')
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    form = ExpenseForm(request.POST or None, instance=expense, user=request.user)

    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect(next_url)

    return render(request, 'expense/expense_form.html', {
        'form': form,
        'title': '✏️ تعديل المصروف',
        'expense': expense,
        'next': next_url
    })

@login_required
def expense_delete(request, pk):
    next_url = request.GET.get('next') or request.POST.get('next') or reverse('expense_list')
    expense = get_object_or_404(Expense, pk=pk, user=request.user)

    if request.method == 'POST':
        expense.delete()
        return redirect(next_url)

    return render(request, 'expense/expense_confirm_delete.html', {
        'expense': expense,
        'title': '🗑️ تأكيد الحذف',
        'next': next_url
    })




@login_required
def home(request):
    user = request.user
    today = date.today()

    # Parse filters
    start_str = request.GET.get('start_date')
    end_str = request.GET.get('end_date')
    group_id = request.GET.get('group')
    label_id = request.GET.get('label')

    try:
        start_date = date.fromisoformat(start_str) if start_str else today.replace(day=1)
    except ValueError:
        start_date = today.replace(day=1)

    try:
        end_date = date.fromisoformat(end_str) if end_str else today
    except ValueError:
        end_date = today

    expenses = Expense.objects.filter(user=user, date__range=(start_date, end_date)).select_related('label', 'label__group')
    incomes = Income.objects.filter(user=user, date__range=(start_date, end_date))

    if label_id and label_id.isdigit():
        expenses = expenses.filter(label_id=int(label_id))
    elif group_id and group_id.isdigit():
        expenses = expenses.filter(label__group_id=int(group_id))

    total_expense = expenses.aggregate(total=Sum('amount'))['total'] or 0
    total_income = incomes.aggregate(total=Sum('amount'))['total'] or 0
    balance = total_income - total_expense

    grouped_expenses = defaultdict(lambda: {'items': [], 'total': 0})
    for expense in expenses:
        label = expense.label
        label_key = label if label else "(بدون تسمية)"
        grouped_expenses[label_key]['items'].append(expense)
        grouped_expenses[label_key]['total'] += expense.amount





    # grouped_expenses = defaultdict(lambda: {'items': [], 'total': 0})
    # for expense in expenses:
    #     label_name = expense.label.name if expense.label else "(بدون تسمية)"
    #     grouped_expenses[label_name]['items'].append(expense)
    #     grouped_expenses[label_name]['total'] += expense.amount

    context = {
        'start_date': start_date.isoformat(),
        'end_date': end_date.isoformat(),
        'total_expense': total_expense,
        'total_income': total_income,
        'balance': balance,
        'grouped_expenses': dict(grouped_expenses),
        'groups': Group.objects.filter(user=user, is_deleted=False),
        'labels': Label.objects.filter(user=user, is_deleted=False),
        'selected_group': int(group_id) if group_id and group_id.isdigit() else '',
        'selected_label': int(label_id) if label_id and label_id.isdigit() else '',
    }

    return render(request, 'home.html', context)



# 👤 Profile Views
@login_required
def profile_view(request):
    return render(request, 'auths/profile.html', {'user': request.user})

@login_required
def edit_profile_view(request):
    user = request.user
    form = ProfileForm(request.POST or None, instance=user, user=user)

    if request.method == 'POST' and form.is_valid():
        print('Cleaned has_wife:', form.cleaned_data['has_wife'])  # 👈 Add this
        form.save()
        return redirect('profile')

    return render(request, 'auths/edit_profile.html', {'form': form})




@login_required
def planning_view(request):
    user = request.user
    monthly_income = user.expected_monthly_income

    # Identify the annual group (by name or flag)
    annual_group = Group.objects.for_user(user).filter(name__icontains='سنوي').first()

    # All groups except annual
    groups = Group.objects.for_user(user).filter(is_deleted=False).exclude(id=annual_group.id if annual_group else None).prefetch_related(
        Prefetch('labels', queryset=Label.objects.filter(is_deleted=False).order_by('order'))
    )

    # Annual labels
    annual_labels = Label.objects.for_user(user).filter(group=annual_group, is_deleted=False) if annual_group else []
    annual_total = sum(label.expected_monthly for label in annual_labels)
    annual_monthly_equiv = annual_total / 12

    # Monthly expenses from non-annual groups
    monthly_expense_total = sum(
        label.expected_monthly for group in groups for label in group.labels.all()
    ) + annual_monthly_equiv

    net_balance = monthly_income - monthly_expense_total

    # Add group-level totals
    for group in groups:
        group.total_expected = sum(label.expected_monthly for label in group.labels.all())

    return render(request, 'planning_page.html', {
        'monthly_income': monthly_income,
        'monthly_expense_total': monthly_expense_total,
        'net_balance': net_balance,
        'groups': groups,
        'annual_labels': annual_labels,
        'annual_total': annual_total,
        'annual_monthly_equiv': annual_monthly_equiv,
    })

@login_required
def expected_monthly_income_view(request):
    user = request.user
    next_url = request.GET.get('next') or request.POST.get('next') or 'annual_expenses_view'

    form = ExpectedMonthlyIncomeForm(request.POST or None, instance=user)

    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect(next_url)

    return render(request, 'welcome/expected_monthly_income_view.html', {
        'form': form,
        'next': next_url
    })

@login_required
def annual_expenses_view(request):

    
    group = get_object_or_404(Group, user=request.user, code='annual_expenses')

    labels = Label.objects.filter(group=group, user=request.user, is_deleted=False)

    label_forms = [
        (label, AnnualExpectedForm(request.POST or None, instance=label, prefix=str(label.id)))
        for label in labels
    ]

    if request.method == 'POST':
        all_valid = True
        any_changed = True

        for label, form in label_forms:
            if form.has_changed():
                if form.is_valid():
                    form.save()
                    any_changed = True
                else:
                    all_valid = False

        if all_valid and any_changed:
            return redirect(monthly_fixed_expenses_view)

    return render(request, 'welcome/annual_expenses_view.html', {
        'group': group,
        'label_forms': label_forms
    })

@login_required
def add_annual_label_view(request):
    group = get_object_or_404(Group, user=request.user, code='annual_expenses')

    form = AnnualLabelAddForm(request.POST or None, user=request.user)

    if request.method == 'POST' and form.is_valid():
        label = form.save(commit=False)
        label.user = request.user
        label.group = group
        label.order = Label.objects.filter(user=request.user, group=group, is_deleted=False).count() + 1
        label.save()
        return redirect('annual_expenses_view')

    return render(request, 'welcome/add_annual_label.html', {
        'form': form,
        'group': group,
        'title': '➕ إضافة تسمية للنفقات السنوية'
    })

@login_required
def monthly_fixed_expenses_view(request):

    group = get_object_or_404(Group, user=request.user, code='monthly_fixed')

    labels = Label.objects.filter(group=group, user=request.user, is_deleted=False)

    label_forms = [
        (label, MonthlyFixedExpectedForm(request.POST or None, instance=label, prefix=str(label.id)))
        for label in labels
    ]

    if request.method == 'POST':
        all_valid = True
        any_changed = True

        for label, form in label_forms:
            if form.has_changed():
                if form.is_valid():
                    form.save()
                    any_changed = True
                else:
                    all_valid = False

        if all_valid and any_changed:
            return redirect(edit_remaining_groups_view)

    return render(request, 'welcome/monthly_fixed_expenses_view.html', {
        'group': group,
        'label_forms': label_forms
    })

@login_required
def add_fixed_label_view(request):
    group = get_object_or_404(Group, user=request.user, code='monthly_fixed')

    form = FixedLabelAddForm(request.POST or None, user=request.user)

    if request.method == 'POST' and form.is_valid():
        label = form.save(commit=False)
        label.user = request.user
        label.group = group
        label.order = Label.objects.filter(user=request.user, group=group, is_deleted=False).count() + 1
        label.save()
        return redirect('monthly_fixed_expenses_view')

    return render(request, 'welcome/add_fixed_label.html', {
        'form': form,
        'group': group,
        'title': '➕ إضافة تسمية للمصاريف الشهرية الثابتة'
    })

@login_required
def edit_remaining_groups_view(request):
    group_codes = ['monthly_variable', 'groceries', 'emergency']
    groups = Group.objects.filter(user=request.user, code__in=group_codes)

    label_forms = []

    for group in groups:
        labels = Label.objects.filter(group=group, user=request.user, is_deleted=False)
        for label in labels:
            prefix = f"{group.code}_{label.id}"
            form = ExpectedMonthlyForm(
                data=request.POST if request.method == 'POST' else None,
                instance=label,
                prefix=prefix
            )
            label_forms.append((group, label, form))

    if request.method == 'POST':
        all_valid = True
        any_changed = True

        for group, label, form in label_forms:
            if form.is_valid():
                if form.has_changed():
                    form.save()
                    any_changed = True
            else:
                all_valid = False

        if all_valid and any_changed:
            return redirect(planning_view)

    return render(request, 'welcome/edit_remaining_groups.html', {
        'groups': groups,
        'label_forms': label_forms
    })



import json


@login_required
def yearly_dashboard_view(request):
    user = request.user
    year = int(request.GET.get('year', date.today().year))

    # Get all expenses and incomes for the year
    start_date = date(year, 1, 1)
    end_date = date(year, 12, 31)

    expenses = Expense.objects.filter(user=user, date__range=(start_date, end_date)).select_related('label', 'label__group')
    incomes = Income.objects.filter(user=user, date__range=(start_date, end_date))

    # Monthly breakdown
    monthly_data = []
    for month in range(1, 13):
        month_start = date(year, month, 1)
        month_end = (month_start.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)

        month_expenses = expenses.filter(date__range=(month_start, month_end))
        month_incomes = incomes.filter(date__range=(month_start, month_end))

        fixed = month_expenses.filter(label__group__name="المصاريف الشهرية الثابتة").aggregate(total=Sum('amount'))['total'] or 0
        variable = month_expenses.filter(label__group__name="المصاريف الشهرية المتغيرة").aggregate(total=Sum('amount'))['total'] or 0
        installment = month_expenses.filter(label__name="القسط الشهري للنفقات السنوية").aggregate(total=Sum('amount'))['total'] or 0
        income = month_incomes.aggregate(total=Sum('amount'))['total'] or 0
        balance = income - (fixed + variable + installment)

        monthly_data.append({
            'name': month_start.strftime('%B'),
            'income': income,
            'fixed': fixed,
            'variable': variable,
            'installment': installment,
            'balance': balance
        })

    # Totals
    total_income = incomes.aggregate(total=Sum('amount'))['total'] or 0
    total_expense = expenses.aggregate(total=Sum('amount'))['total'] or 0
    balance = total_income - total_expense

    # Category totals
    category_totals = {}
    for label in Label.objects.filter(user=user, is_deleted=False):
        label_expenses = expenses.filter(label=label).aggregate(total=Sum('amount'))['total'] or 0
        category_totals[label.name] = {
            'actual': label_expenses,
            'expected': label.expected_monthly * 12,
            'diff': label_expenses - (label.expected_monthly * 12)
        }
    # Pie/Donut chart data
    pie_data = [
        {'label': label, 'value': data['actual']}
        for label, data in category_totals.items()
        if data['actual'] > 0
    ]
    # Line chart: monthly income vs. expenses
    line_data = [
        {'month': m['name'], 'income': m['income'], 'expense': m['fixed'] + m['variable'] + m['installment']}
        for m in monthly_data
    ]
    # Bar chart: category-wise actual vs expected
    bar_data = [
        {'label': label, 'actual': data['actual'], 'expected': data['expected']}
        for label, data in category_totals.items()
    ]
    # Heatmap: spending intensity by month
    heatmap_data = [
        {'month': m['name'], 'intensity': m['fixed'] + m['variable'] + m['installment']}
        for m in monthly_data
    ]

    donut_labels = [label for label, data in category_totals.items() if data['actual'] > 0]
    donut_values = [data['actual'] for label, data in category_totals.items() if data['actual'] > 0]
    
    group_totals = {}
    for group in Group.objects.filter(user=user, is_deleted=False):
        group_expenses = expenses.filter(label__group=group).aggregate(total=Sum('amount'))['total'] or 0
        if group_expenses > 0:
            group_totals[group.name] = group_expenses

    group_labels = list(group_totals.keys())
    group_values = list(group_totals.values())
    
    savings_label = Label.objects.filter(user=user, name__icontains="ادخار", is_deleted=False).first()
    savings_progress = []
    for month in range(1, 13):
        month_start = date(year, month, 1)
        month_end = (month_start.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)

        if savings_label:
            monthly_savings = expenses.filter(
                label=savings_label,
                date__range=(month_start, month_end)
            ).aggregate(total=Sum('amount'))['total'] or 0
        else:
            monthly_savings = 0

        savings_progress.append({
            'month': month_start.strftime('%B'),
            'saved': monthly_savings
        })

    context = {
        'year': year,
        'year_range': range(2020, 2031),  # 2031 is exclusive
        'monthly_data': monthly_data,
        'total_income': total_income,
        'total_expense': total_expense,
        'balance': balance,
        'category_totals': category_totals,


        'pie_labels': json.dumps([item['label'] for item in pie_data]),
        'pie_values': json.dumps([item['value'] for item in pie_data]),

        'line_months': json.dumps([item['month'] for item in line_data]),
        'line_income': json.dumps([item['income'] for item in line_data]),
        'line_expense': json.dumps([item['expense'] for item in line_data]),

        'bar_labels': json.dumps([item['label'] for item in bar_data]),
        'bar_actual': json.dumps([item['actual'] for item in bar_data]),
        'bar_expected': json.dumps([item['expected'] for item in bar_data]),

        'heatmap_months': json.dumps([item['month'] for item in heatmap_data]),
        'heatmap_intensity': json.dumps([item['intensity'] for item in heatmap_data]),
        
        'donut_labels': json.dumps(donut_labels),
        'donut_values': json.dumps(donut_values),
        
        'group_labels': json.dumps(group_labels),
        'group_values': json.dumps(group_values),
        
        'savings_labels': json.dumps([item['month'] for item in savings_progress]),
        'savings_values': json.dumps([item['saved'] for item in savings_progress]),
    }

    
    

    return render(request, 'yearly_dashboard.html', context)



@login_required
def budget_simulator_view(request):
    user = request.user
    labels = Label.objects.filter(user=user, is_deleted=False)

    simulated_values = {}
    if request.method == 'POST':
        for label in labels:
            key = f'label_{label.id}'
            value = int(request.POST.get(key, 0))
            simulated_values[label.name] = value

        total_simulated = sum(simulated_values.values())
        simulated_balance = (Income.objects.filter(user=user).aggregate(total=Sum('amount'))['total'] or 0) - total_simulated
    else:
        simulated_balance = None

    context = {
        'labels': labels,
        'simulated_values': simulated_values,
        'simulated_balance': simulated_balance
    }
    return render(request, 'dashboard/budget_simulator.html', context)













# 📊 Dashboard Views
def get_month_bounds():
    today = date.today()
    start_date = today.replace(day=1)
    next_month = start_date.replace(day=28) + timedelta(days=4)
    end_date = next_month.replace(day=1) - timedelta(days=1)
    return start_date, end_date

@login_required
def dashboard(request):
    user = request.user
    start_date, end_date = get_month_bounds()
    group_id = request.GET.get('group')

    selected_group = None
    sublabel_data = []
    total_expected = 0
    total_actual = 0

    groups = Group.objects.filter(user=user, is_deleted=False)

    if group_id:
        selected_group = get_object_or_404(groups, pk=group_id)
        labels = Label.objects.filter(group=selected_group, user=user, is_deleted=False).prefetch_related('expenses')

        total_expected = labels.aggregate(total=Sum('expected_monthly'))['total'] or 0

        for label in labels:
            filtered_expenses = label.expenses.filter(date__range=(start_date, end_date))
            actual_total = filtered_expenses.aggregate(Sum('amount'))['amount__sum'] or 0
            total_actual += actual_total

            sublabel_data.append({
                'label': label,
                'expected': label.expected_monthly or 0,
                'actual': actual_total,
                'expenses': filtered_expenses
            })

    context = {
        'groups': groups,
        'selected_group': selected_group,
        'selected_id': int(group_id) if group_id else '',
        'sublabel_data': sublabel_data,
        'total_expected': total_expected,
        'total_actual': total_actual,
        'start_date': start_date.isoformat(),
        'end_date': end_date.isoformat(),
    }

    return render(request, 'dashboard.html', context)


# @login_required
# def monthly_variable_expenses_view(request):
#     redirect_url = reverse('planning_view') 

#     group_codes = ['monthly_variable', 'groceries', 'emergency']
#     groups = Group.objects.filter(user=request.user, code__in=group_codes)

#     label_forms = []

#     for group in groups:
#         labels = Label.objects.filter(group=group, user=request.user, is_deleted=False)
#         for label in labels:
#             form = ExpectedMonthlyForm(request.POST or None, instance=label, prefix=f"{group.code}_{label.id}")
#             label_forms.append((group, label, form))

#     if request.method == 'POST':
#         all_valid = True
#         any_changed = False

#         for group, label, form in label_forms:
#             if form.has_changed():
#                 if form.is_valid():
#                     form.save()
#                     any_changed = True
#                 else:
#                     all_valid = False

#         if all_valid and any_changed:
#             return redirect(redirect_url)

#     return render(request, 'welcome/edit_remaining_groups.html', {
#         'label_forms': label_forms,
#         'groups': groups
#     })












# @login_required
# def annual_expenses_edit_view(request):
#     group = get_object_or_404(Group, user=request.user, code='annual_expenses')

#     labels = Label.objects.filter(group=group, user=request.user, is_deleted=False).order_by('order')

#     add_form = AnnualLabelForm(request.POST or None, prefix='new')
#     label_forms = [
#         (label, AnnualLabelForm(request.POST or None, instance=label, prefix=str(label.id)))
#         for label in labels
#     ]

#     redirect_url = reverse('monthly_fixed_expenses_view')

#     if request.method == 'POST':
#         if 'add_label' in request.POST and add_form.is_valid():
#             new_label = add_form.save(commit=False)
#             new_label.group = group
#             new_label.user = request.user
#             new_label.order = labels.count() + 1
#             new_label.save()
#             return redirect(request.path)

#         elif 'delete_label' in request.POST:
#             label_id = request.POST.get('delete_label')
#             Label.objects.filter(id=label_id, group=group, user=request.user).delete()
#             return redirect(request.path)

#         else:
#             all_valid = True
#             for label, form in label_forms:
#                 if form.is_valid():
#                     form.save()
#                 else:
#                     all_valid = False
#             if all_valid:
#                 return redirect(redirect_url)

#     return render(request, 'welcome/annual_expenses_edit.html', {
#         'group': group,
#         'label_forms': label_forms,
#         'add_form': add_form
#     })



# @login_required
# def monthly_variable_expenses_view(request):
#     user = request.user
#     next_url = request.GET.get('next') or request.POST.get('next') or 'home'

#     group, _ = Group.objects.get_or_create(user=user, name="المصاريف الشهرية المتغيرة", defaults={'order': 3})
#     labels = Label.objects.filter(group=group, user=user, is_deleted=False)

#     add_form = MonthlyVariableExpenseForm(request.POST or None, prefix='new')
#     label_forms = [(label, MonthlyVariableExpenseForm(request.POST or None, instance=label, prefix=str(label.id))) for label in labels]

#     if request.method == 'POST':
#         if 'add_label' in request.POST and add_form.is_valid():
#             new_label = add_form.save(commit=False)
#             new_label.group = group
#             new_label.user = user
#             new_label.order = labels.count() + 1
#             new_label.save()
#             return redirect(next_url)

#         elif 'delete_label' in request.POST:
#             label_id = request.POST.get('delete_label')
#             Label.objects.filter(id=label_id, group=group, user=user).delete()
#             return redirect(next_url)

#         else:
#             all_valid = True
#             for label, form in label_forms:
#                 if form.is_valid():
#                     form.save()
#                 else:
#                     all_valid = False
#             if all_valid:
#                 return redirect(next_url)

#     return render(request, 'welcome/monthly_variable_expenses_view.html', {
#         'group': group,
#         'label_forms': label_forms,
#         'add_form': add_form,
#         'next': next_url
#     })


from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .models import Group, Label
from .forms import ExpectedMonthlyForm




# @login_required
# def edit_remaining_groups_view(request):
#     redirect_url = reverse('dashboard')  # or wherever you want to go

#     group_codes = ['monthly_variable', 'groceries', 'emergency']
#     groups = Group.objects.filter(user=request.user, code__in=group_codes)

#     label_forms = []

#     for group in groups:
#         labels = Label.objects.filter(group=group, user=request.user, is_deleted=False)
#         for label in labels:
#             prefix = f"{group.code}_{label.id}"
#             form = ExpectedMonthlyForm(
#                 data=request.POST if request.method == 'POST' else None,
#                 instance=label,
#                 prefix=prefix
#             )
#             label_forms.append((group, label, form))

#     if request.method == 'POST':
#         all_valid = True
#         any_changed = False

#         for group, label, form in label_forms:
#             if form.is_valid():
#                 if form.has_changed():
#                     form.save()
#                     any_changed = True
#             else:
#                 all_valid = False

#         if all_valid and any_changed:
#             return redirect(redirect_url)

#     return render(request, 'welcome/edit_remaining_groups.html', {
#         'groups': groups,
#         'label_forms': label_forms
#     })

# @login_required
# def edit_remaining_groups_view(request):
#     redirect_url = reverse('dashboard')  # or any other target view

#     group_codes = ['monthly_variable', 'groceries', 'emergency']
#     groups = Group.objects.filter(user=request.user, code__in=group_codes)

#     label_forms = []

#     for group in groups:
#         labels = Label.objects.filter(group=group, user=request.user, is_deleted=False)
#         for label in labels:
#             form = ExpectedMonthlyForm(
#                 request.POST if request.method == 'POST' else None,
#                 instance=label,
#                 prefix=f"{group.code}_{label.id}"
#             )
#             label_forms.append((group, label, form))

#     if request.method == 'POST':
#         all_valid = True
#         any_changed = False

#         for group, label, form in label_forms:
#             if form.has_changed():
#                 if form.is_valid():
#                     form.save()
#                     any_changed = True
#                 else:
#                     all_valid = False

#         if all_valid and any_changed:
#             return redirect(redirect_url)

#     return render(request, 'welcome/edit_remaining_groups.html', {
#         'groups': groups,
#         'label_forms': label_forms
#     })




