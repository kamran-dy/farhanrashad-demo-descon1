from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError


class EmployeeInformationWizard(models.TransientModel):
    _name = 'employee.information'
    _description = 'Employee Information Wizard'

    department_ids = fields.Many2many('hr.department', string='Department')
    employee_type_ids = fields.Many2many('employee.type', string='Employee`s Type')
    grade_type_ids = fields.Many2many('grade.type', string='Grade Type')
    email = fields.Boolean('Email', default=True, store=True, readonly=False)
    mobile = fields.Boolean('Mobile', default=True, store=True, readonly=False)
    address = fields.Boolean('Address', default=True, store=True, readonly=False)
    religion = fields.Boolean('Religion', default=True, store=True, readonly=False)
    cnic = fields.Boolean('CNIC', default=True, store=True, readonly=False)
    blood_group = fields.Boolean('Blood Group', default=True, store=True, readonly=False)
    bank_account_number = fields.Boolean('Bank Account Number', default=True, store=True, readonly=False)
    card_no = fields.Boolean('Card No', default=True, store=True, readonly=False)
    emergency_contact = fields.Boolean('Emergency Contact', default=True, store=True, readonly=False)
    assets = fields.Boolean('Assets', default=True, store=True, readonly=False)
    dependent = fields.Boolean('Dependent', default=True, store=True, readonly=False)
    pfund = fields.Boolean('PFund', default=True, store=True, readonly=False)
    eobi_number = fields.Boolean('EOBI Number', default=True, store=True, readonly=False)
    gratuity = fields.Boolean('Gratuity', default=True, store=True, readonly=False)
    contract_details = fields.Boolean('Contract Details', default=True, store=True, readonly=False)
    
            
    def action_generate_pdf(self):
        data = {
            'employee_type_ids': self.employee_type_ids.ids,
            'grade_type_ids': self.grade_type_ids.ids,
            'department_ids': self.department_ids.ids,
            'email':self.email,
            'mobile':self.mobile,
            'address':self.address,
            'cnic':self.cnic,
            'religion':self.religion,
            'blood_group':self.blood_group,
            'bank_account_number':self.bank_account_number,
            'card_no':self.card_no,
            'emergency_contact':self.emergency_contact,
            'assets':self.assets,
            'dependent':self.dependent,
            'pfund':self.pfund,
            'eobi_number':self.eobi_number,
            'gratuity':self.gratuity,
            'contract_details':self.contract_details,
            }
        return self.env.ref('de_hr_employee_report.employee_information_pdf').report_action(self, data=data)

    def action_gnerate_excel(self):
        data = {
            'employee_type_ids': self.employee_type_ids.ids,
            'grade_type_ids': self.grade_type_ids.ids,
            'department_ids': self.department_ids.ids,
            'email':self.email,
            'mobile':self.mobile,
            'address':self.address,
            'cnic':self.cnic,
            'religion':self.religion,
            'blood_group':self.blood_group,
            'bank_account_number':self.bank_account_number,
            'card_no':self.card_no,
            'emergency_contact':self.emergency_contact,
            'assets':self.assets,
            'dependent':self.dependent,
            'pfund':self.pfund,
            'eobi_number':self.eobi_number,
            'gratuity':self.gratuity,
            'contract_details':self.contract_details,
            }
        return self.env.ref('de_hr_employee_report.employee_information_xlsx').report_action(self, data=data)
