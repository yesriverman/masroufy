from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser, Income, Expense, Group, Label

# 🔐 User Forms
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget = forms.PasswordInput(attrs={'class': 'form-control'})
        self.fields['password2'].widget = forms.PasswordInput(attrs={'class': 'form-control'})

class StyledAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'اسم المستخدم'})
        self.fields['password'].widget.attrs.update({'class': 'form-control', 'placeholder': 'كلمة المرور'})

# 💰 Income Form
class IncomeForm(forms.ModelForm):
    class Meta:
        model = Income
        fields = ['amount', 'date']
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date'].input_formats = ['%Y-%m-%d']

class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name']
        labels = {'name': '🏷️ اسم المجموعة'}
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'أدخل اسم المجموعة (مثلاً: السكن، الطعام)'
            })
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Disable editing name if protected
        if self.instance and self.instance.protected:
            self.fields['name'].disabled = True

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')

        if self.instance and self.instance.protected:
            cleaned_data['name'] = self.instance.name  # prevent tampering

        if self.user and name:
            qs = Group.objects.filter(user=self.user, name__iexact=name)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError("❌ هذه التسمية موجودة بالفعل.")
        return cleaned_data

# 🏷️ Label Form
class LabelForm(forms.ModelForm):
    class Meta:
        model = Label
        fields = ['group', 'name', 'expected_monthly']
        widgets = {
            'group': forms.Select(attrs={'class': 'form-control', 'placeholder': 'اسم المجموعة '}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'اسم المصروف '}),
            'expected_monthly': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'المبلغ المتوقع'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['group'].queryset = Group.objects.filter(user=self.user, is_deleted=False)

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        group = cleaned_data.get('group')
        if self.user and name and group:
            qs = Label.objects.filter(user=self.user, group=group, name__iexact=name, is_deleted=False)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError("❌ هذا الاسم موجود بالفعل ضمن هذه المجموعة.")
        return cleaned_data

# 💸 Expense Form
class ExpenseForm(forms.ModelForm):
    group = forms.ModelChoiceField(queryset=Group.objects.none(), required=True)

    class Meta:
        model = Expense
        fields = ['group', 'label', 'amount', 'date']
        labels = {
            'label': ' اسم المصروف',
            'amount': 'المبلغ',
            'date': 'التاريخ',
        }
        widgets = {
            'group': forms.Select(attrs={'class': 'form-control', 'placeholder': 'اسم المجموعة '}),
            'amount': forms.NumberInput(attrs=  {'class': 'form-control',
                'placeholder':'المبلغ'}),
                'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        
        
        self.fields['group'].widget.attrs.update({'class': 'form-control'})
        self.fields['label'].widget.attrs.update({'class': 'form-control'})
        
        self.fields['group'].queryset = Group.objects.filter(user=user, is_deleted=False)
        self.fields['label'].queryset = Label.objects.none()

        if 'group' in self.data:
            try:
                group_id = int(self.data.get('group'))
                self.fields['label'].queryset = Label.objects.filter(group_id=group_id, user=user, is_deleted=False)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['label'].queryset = Label.objects.filter(group=self.instance.label.group, user=user, is_deleted=False)
            self.fields['group'].initial = self.instance.label.group

# add_expense_view add multiple expenses to group
class LabelExpenseForm(forms.Form):
    label_id = forms.IntegerField(widget=forms.HiddenInput)
    label_name = forms.CharField(disabled=True, required=False)
    amount = forms.DecimalField(label='المبلغ', required=False, min_value=0)
from django.forms import formset_factory

LabelExpenseFormSet = formset_factory(LabelExpenseForm, extra=0)


class ProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'phone_number', 'profession', 'city', 'has_wife', 'kids']
        labels = {
            'username': '👤 اسم المستخدم',
            'email': '📧 البريد الإلكتروني',
            'phone_number': '📱 رقم الهاتف',
            'profession': '💼 المهنة',
            'city': '🏙️ المدينة',
            'has_wife': '💍 هل لديك زوجة؟',
            'kids': '👶 عدد الأطفال'
        }
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'profession': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'has_wife': forms.CheckboxInput(attrs={
    'class': 'form-check-input',
    'style': 'transform: scale(1.5); margin-right: 10px;'
}),

            # 'has_wife': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'kids': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        kwargs.pop('user', None)
        super().__init__(*args, **kwargs)




# expected_monthly_income_view
class ExpectedMonthlyIncomeForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['expected_monthly_income']
        widgets = {
            'expected_monthly_income': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'أدخل دخلك الشهري المتوقع',
                'min': '0'
            })
        }
        labels = {
            'expected_monthly_income': '📊 الدخل الشهري المتوقع'
        }

class ExpectedMonthlyForm(forms.ModelForm):
    class Meta:
        model = Label
        fields = ['expected_monthly']
        labels = {'expected_monthly': '💰 المبلغ المتوقع شهرياً'}
        widgets = {
            'expected_monthly': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'أدخل المبلغ'
            })
        }




# annual_expenses_view
class AnnualExpectedForm(forms.ModelForm):
    class Meta:
        model = Label
        fields = ['expected_monthly']
        labels = {'expected_monthly': '💰 المبلغ المتوقع شهرياً'}
        widgets = {
            'expected_monthly': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'أدخل المبلغ المتوقع'
            })
        }

# add_annual_label_view
class AnnualLabelAddForm(forms.ModelForm):
    class Meta:
        model = Label
        fields = ['name', 'expected_monthly']
        labels = {
            'name': '🏷️ اسم التسمية',
            'expected_monthly': '💰 المبلغ المتوقع شهرياً'
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'مثلاً: تأمين السيارة'}),
            'expected_monthly': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0'})
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_name(self):
        name = self.cleaned_data['name']
        if Label.objects.filter(user=self.user, name__iexact=name, group__code='annual_expenses', is_deleted=False).exists():
            raise forms.ValidationError("❌ هذه التسمية موجودة بالفعل ضمن النفقات السنوية.")
        return name






# monthly_fixed_expenses_view
class MonthlyFixedExpectedForm(forms.ModelForm):
    class Meta:
        model = Label
        fields = ['expected_monthly']
        labels = {'expected_monthly': '💰 المبلغ الشهري المتوقع'}
        widgets = {
            'expected_monthly': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'مثلاً: 1500'
            })
        }


# add_fixed_label_view
class FixedLabelAddForm(forms.ModelForm):
    class Meta:
        model = Label
        fields = ['name', 'expected_monthly']
        labels = {
            'name': '🏷️ اسم التسمية',
            'expected_monthly': '💰 المبلغ المتوقع شهرياً'
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'مثلاً: إيجار'}),
            'expected_monthly': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0'})
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_name(self):
        name = self.cleaned_data['name']
        if Label.objects.filter(user=self.user, name__iexact=name, group__code='monthly_fixed', is_deleted=False).exists():
            raise forms.ValidationError("❌ هذه التسمية موجودة بالفعل ضمن المصاريف الشهرية الثابتة.")
        return name





# monthly_variable_expenses_view
class ExpectedMonthlyForm(forms.ModelForm):
    class Meta:
        model = Label
        fields = ['expected_monthly']
        labels = {'expected_monthly': '💰 المبلغ المتوقع شهرياً'}
        widgets = {
            'expected_monthly': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'أدخل المبلغ'
            })
        }



# 📆 Specialized Label Forms
# annual_expenses_edit_view
class AnnualLabelForm(forms.ModelForm):
    expected_monthly = forms.DecimalField(label="المبلغ الشهري المتوقع", min_value=0, decimal_places=0)

    class Meta:
        model = Label
        fields = ['name', 'expected_monthly']
        labels = {'name': 'اسم التسمية'}
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'مثلاً: التأمين السنوي'}),
            'expected_monthly': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'مثلاً: 250'}),
        }


from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

class MonthlyVariableExpenseForm(forms.ModelForm):
    class Meta:
        model = Label
        fields = ['name', 'expected_monthly']
        labels = {
            'name': 'اسم التسمية',
            'expected_monthly': 'المعدل الشهري المتوقع'
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'مثلاً: الكهرباء'}),
            'expected_monthly': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'مثلاً: 400'}),
        }
