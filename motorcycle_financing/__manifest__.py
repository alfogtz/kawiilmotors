{
    'name': 'Motorcycle Financing',
    'summary': 'Streamlines the loan application process for dealerships.',
    'description': 'This module helps K\'awiil Motors track and manage motorcycle loan applications efficiently.',
    'license': 'OPL-1',
    'category': 'Kawiil/Custom Modules',
    'author': 'alfogtz',
    'website': 'https://github.com/alfogtz/kawiilmotors',
    'version': '18.0.0.0.1',
    'depends': ['sale', 'mail'],
    'data': ['security/motorcycle_financing_groups.xml',
             'security/ir.model.access.csv',
             'security/document_security.xml',
             'security/rules.xml',
             'views/loan_application_action.xml',
             'views/loan_application_document_views.xml',
             'views/loan_application_document_type_views.xml',
             'views/loan_application_tag_views.xml',
             'views/loan_application_views.xml',
             'views/motorcycle_financing_menu.xml',
             'views/sale_order_views.xml',],
    'demo': ['data/loan_demo.xml',],
    'application': True,
    'images': ['static/description/icon.png'],
}
