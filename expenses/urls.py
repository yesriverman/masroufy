from django.urls import path
from . import views

urlpatterns = [
    # 🔐 Auth
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # 👤 Profile
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile_view, name='edit_profile'),

    # 💰 Income
    path('incomes/', views.income_list, name='income_list'),
    path('income/add/', views.income_add, name='income_add'),
    path('incomes/<int:income_id>/edit/', views.income_edit, name='income_edit'),
    path('incomes/<int:income_id>/delete/', views.income_delete, name='income_delete'),

    # 🗂️ Groups
    path('groups/', views.group_list, name='group_list'),
    path('groups/add/', views.group_add, name='group_add'),
    path('groups/<int:group_id>/edit/', views.group_edit, name='group_edit'),
    path('groups/<int:group_id>/delete/', views.group_delete, name='group_delete'),
    path('groups/restore/<int:group_id>/', views.group_restore_view, name='group_restore_view'),
    path('groups/<int:pk>/up/', views.move_group_up, name='move_group_up'),
    path('groups/<int:pk>/down/', views.move_group_down, name='move_group_down'),

    # 🏷️ Labels
    path('labels/', views.label_list, name='label_list'),
    path('labels/add/', views.label_add, name='label_add'),
    path('labels/<int:pk>/edit/', views.label_edit, name='label_edit'),
    path('labels/<int:pk>/delete/', views.label_delete, name='label_delete'),
    path('labels/restore/<int:label_id>/', views.label_restore_view, name='label_restore_view'),
    path('labels/<int:pk>/up/', views.move_label_up, name='move_label_up'),
    path('labels/<int:pk>/down/', views.move_label_down, name='move_label_down'),

    # 💸 Expenses
    path('expenses/', views.expense_list, name='expense_list'),
    path('expenses/add/', views.expense_add, name='expense_add'),
    path('expenses/<int:pk>/edit/', views.expense_edit, name='expense_edit'),
    path('expenses/<int:pk>/delete/', views.expense_delete, name='expense_delete'),
    path('add_expense_view/', views.add_expense_view, name='add_expense_view'),


    # 📊 Dashboard
    path('dashboard/', views.yearly_dashboard_view, name='dashboard'),
    path('', views.home, name='home'),
    path('planning_view/', views.planning_view, name='planning_view'),



    # 🚀 welcome
    path('welcome/income/', views.expected_monthly_income_view, name='expected_monthly_income_view'),
    
    path('welcome/annual/', views.annual_expenses_view, name='annual_expenses_view'),
    path('welcome/annual/add/', views.add_annual_label_view, name='add_annual_label_view'),
    
    path('welcome/fixed/', views.monthly_fixed_expenses_view, name='monthly_fixed_expenses_view'),
    path('welcome/fixed/add/', views.add_fixed_label_view, name='add_fixed_label_view'),

    path('welcome/variable/', views.edit_remaining_groups_view, name='edit_remaining_groups_view'),



    # 🚨 Optional: Custom 404 handler
    # path('404/', views.custom_404_view, name='custom_404'),
]
