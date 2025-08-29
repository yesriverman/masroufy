
from .models import Group, Label

def create_default_categories(user):
    defaults = {
        'annual_expenses': {
            'name': 'النفقات السنوية',
            'protected': True,
            'labels': [
                ('عطلة', 0),
                ('تأمين السيارة', 0)
            ]
        },
        'monthly_fixed': {
            'name': 'المصاريف الشهرية الثابتة',
            'protected': True,
            'labels': [
                ('إيجار', 0),
                ('مصروف الجيب', 0),
                ('قرض', 0),
                ('رسوم دراسية', 0),
                ('ادخار', 0),
                ('بر الوالدين', 0),
                ('اشتراك الهاتف', 0),
                ('الكهرباء', 0),
                ('الماء', 0)
            ]
        },
        'monthly_variable': {
            'name': 'المصاريف الشهرية المتغيرة',
            'protected': True,
            'labels': [
                ('بنزين', 0),
                ('خضراوات', 0),
                ('فواكه', 0),
                ('لحوم', 0),
                ('صدقة', 0),
                ('عشاء في الخارج', 0),
                ('ملابس', 0)
            ]
        },
        'groceries': {
            'name': 'المواد الغذائية',
            'protected': False,
            'labels': [
                ('دقيق', 0),
                ('أرز', 0)
            ]
        },
        'emergency': {
            'name': 'الطوارئ',
            'protected': False,
            'labels': [
                ('صندوق الطوارئ', 0),
                ('إصلاحات غير متوقعة', 0)
            ]
        },
    }

    for group_order, (code, data) in enumerate(defaults.items(), start=1):
        group = Group.objects.create(
            user=user,
            name=data['name'],
            code=code,
            protected=data['protected'],
            order=group_order
        )

        for label_order, (label_name, expected) in enumerate(data['labels'], start=1):
            Label.objects.create(
                user=user,
                group=group,
                name=label_name.strip(),
                expected_monthly=expected,
                order=label_order
            )



# def create_default_categories(user):
#     defaults = {
#         'النفقات السنوية': [
#             ('عطلة', 0), ('تأمين السيارة', 0)
#         ],
#         'المصاريف الشهرية الثابتة': [
#             ('إيجار', 0), ('مصروف الجيب', 0), ('قرض', 0), ('رسوم دراسية', 0), ('ادخار', 0), ('بر الوالدين', 0), ('اشتراك الهاتف', 0), ('الكهرباء', 0), ('الماء', 0)
#         ],
#         'المصاريف الشهرية المتغيرة': [
#             ('بنزين', 0), ('خضراوات', 0), ('فواكه', 0), ('لحوم', 0), ('صدقة', 0), ('عشاء في الخارج', 0), ('ملابس', 0),
#         ],
#         'المواد الغذائية': [
#             ('دقيق', 0), ('أرز', 0)
#         ],
#         'الطوارئ': [
#             ('صندوق الطوارئ', 0), ('إصلاحات غير متوقعة', 0)
#         ],
#     }

#     for group_order, (group_name, labels) in enumerate(defaults.items(), start=1):
#         group = Group.objects.create(
#             name=group_name,
#             user=user,
#             order=group_order
#         )
#         for label_order, (label_name, expected) in enumerate(labels, start=1):
#             Label.objects.create(
#                 name=label_name.strip(),  # removes accidental leading/trailing spaces
#                 expected_monthly=expected,
#                 group=group,
#                 user=user,
#                 order=label_order
#             )

# def create_default_categories(user):
#     # Define your default structure

#     defaults = {
#     'النفقات السنوية': [('شراء هاتف', 0),  ('عطلة', 0), ('تأمين السيارة', 0)],
    
#     'المصاريف الشهرية الثابتة': [('إيجار', 0), ('مصروف الجيب', 0), (' قرض', 0), ('رسوم دراسية', 0), ('ملابس', 0), ('ادخار', 0), ('بر الوالدين', 0), ('اشتراك الهاتف', 0), ('الكهرباء', 0), ('الماء', 0)
#      , ('القسط الشهري للنفقات السنوية', 0)],
   
#     'المصاريف الشهرية المتغيرة': [ ('بنزين', 0), ('خضراوات', 0), ('فواكه', 0), ('لحوم', 0), ('سمك', 0), ('صدقة', 0), ('عشاء في الخارج', 0)],
    
#     'المواد الغذائية': [('دقيق', 0), ('أرز', 0)],
    
#     'الطوارئ': [('صندوق الطوارئ', 0), ('إصلاحات غير متوقعة', 0)],
# }


#     for group_order, (group_name, labels) in enumerate(defaults.items(), start=1):
#         group = Group.objects.create(
#             name=group_name,
#             user=user,
#             order=group_order
#         )
#         for label_order, (label_name, expected) in enumerate(labels, start=1):
#             Label.objects.create(
#                 name=label_name,
#                 expected_monthly=expected,
#                 group=group,
#                 user=user,
#                 order=label_order
#             )

# # #     defaults =     {
# # # 'Annual Expenses': [('Buying a Phone', 2000), ('Buying a Laptop', 6000), ('Vacation', 5000), ('Home Renovation', 7000), ('Car Insurance', 4000),  ('Medical Expenses', 4000),],
# # # 'Monthly Expenses': [('Rent', 3000), ('Pocket Money', 1000), ('Loan', 1500), ('School Fees', 2000), ('Clothes', 1500), ('Savings', 2000), ("Children's Savings", 1000), ('Honoring Parents', 500), ('Telephone', 300), ('Electricity', 200), ('Water', 100), ('Internet', 300)],
# # # 'librairie':[('Books', 300),  ('Notebooks', 150), ('Pens', 50)],
# # # 'Daily Expenses':[('Transportation', 200) , ('Bread', 150),  ('Gasoline', 500),('Vegetables', 500), ('Fruits', 300), ('Meat', 600), ('Fish', 500), ('Chicken', 700),  ('Charity', 200), ('Dinner Out', 300), ('Lunch Out', 200)],
# # # 'Groceries': [('Flour', 500), ('Rice', 400), ('Pasta', 300), ('Sugar', 200), ('Salt', 100), ('Oil', 300), ('Spices', 200)],
# # # 'Emergency': [('Emergency Fund', 5000), ('Unexpected Repairs', 2000), ('Medical Emergencies', 3000), ('Car Repairs', 1500), ('Home Repairs', 2500)],}

