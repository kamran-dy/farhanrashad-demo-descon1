import xlwt
from odoo import models
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError


class EmployeeAgeReport(models.AbstractModel):
    _name = 'report.de_hr_employee_report.employee_information_xlsx'
    _inherit = 'report.report_xlsx.abstract'
    _description = 'Employee Information Report XLSX'
    
    def generate_xlsx_report(self, workbook, data, lines):
        #raise UserError(data['assets'])
        
        type_employee = self.env['employee.type'].search([('id', 'in', data['employee_type_ids'])])
        employee_type = []
        for rec in type_employee:
            employee_type.append(rec.name)
        
        em_type = ','.join(employee_type)
        grade_type = self.env['grade.type'].search([('id', 'in', data['grade_type_ids'])])
        g_type = []
        for rec in grade_type:
            g_type.append(rec.name)

        gr_type = ','.join(g_type)
        
        department = self.env['hr.department'].search([('id', 'in', data['department_ids'])])
        departments = []
        for rec in department:
            departments.append(rec.name)
        #raise UserError(departments)
        dep = ','.join(departments)
        
        
        employees = []
        if employee_type and grade_type and department:
            active_contract = self.env['hr.contract'].search([('state', '=', 'open'),
                                                              ('employee_id.emp_type', 'in', employee_type),
                                                              ('employee_id.grade_type', 'in', g_type),
                                                              ('employee_id.department_id', 'in',
                                                               departments)])
            
            
        elif employee_type and grade_type:
            active_contract = self.env['hr.contract'].search([('state', '=', 'open'),
                                                              ('employee_id.emp_type', '=', employee_type),
                                                              ('employee_id.grade_type', '=', grade_type)])
                     
        elif employee_type and department:
            active_contract = self.env['hr.contract'].search([('state', '=', 'open'),
                                                              ('employee_id.emp_type', '=', employee_type),
                                                              ('employee_id.department_id', '=',
                                                               department)])
        
        elif department and grade_type:
            active_contract = self.env['hr.contract'].search([('state', '=', 'open'),
                                                              ('employee_id.grade_type', '=', grade_type),
                                                              ('employee_id.department_id', '=',
                                                               department)
                                                              ])
        elif department:
            active_contract = self.env['hr.contract'].search([('state', '=', 'open'),
                                                              ('employee_id.department_id', '=',
                                                               department)
                                                              ])
        elif grade_type:
            active_contract = self.env['hr.contract'].search([('state', '=', 'open'),
                                                              ('employee_id.grade_type', '=', grade_type)
                                                              ])
        elif employee_type:
            active_contract = self.env['hr.contract'].search([('state', '=', 'open'),
                                                              ('employee_id.emp_type', '=', employee_type)
                                                              ])
        
        else:
            active_contract = self.env['hr.contract'].search([('state', '=', 'open')
                                                              ])
        
        format1 = workbook.add_format({'font_size': '14', 'align': 'vcenter', 'bold': True})
        sheet = workbook.add_worksheet('Employee Age Report')
        
        sheet.write(3, 3, 'Emp Type', format1)
        sheet.write(3, 4, em_type, format1)
        sheet.write(3, 6, 'Department', format1)
        sheet.write(3, 7, dep, format1)
        sheet.write(4, 3, 'Grade Type', format1)
        sheet.write(4, 4, gr_type, format1)
        
        
        sheet.write(6, 0, 'Employee Type', format1)
        sheet.write(6, 1, 'Grade Type', format1)
        sheet.write(6, 2, 'Department', format1)
        if data['email'] == True:
            sheet.write(6, 3, 'Email', format1)
        if data['mobile'] == True:
            sheet.write(6, 4, 'Mobile', format1)
        if data['address'] == True:
            sheet.write(6, 5, 'Address', format1)
        if data['religion'] == True:
            sheet.write(6, 6, 'Religion', format1)
        if data['cnic'] == True:
            sheet.write(6, 7, 'CNIC', format1)
        if data['blood_group'] == True:
            sheet.write(6, 8, 'Blood Group', format1)
        if data['bank_account_number'] == True:
            sheet.write(6, 9, 'Bank Account Number', format1)
        if data['card_no'] == True:
            sheet.write(6, 10, 'Card No.', format1)
        if data['emergency_contact'] == True:
            sheet.write(6, 11, 'Emergency Contact', format1)
        if data['assets'] == True:
        
            sheet.write(6, 12, 'Asset Name', format1)
            sheet.write(6, 13, 'Issue Date', format1)
            sheet.write(6, 14, 'Estimate Life Span', format1)
            sheet.write(6, 15, 'Recovery', format1)
            sheet.write(6, 16, 'Discovery', format1)
        if data['dependent'] == True:
        
            sheet.write(6, 17, 'Dependent Name', format1)
            sheet.write(6, 18, 'Relationship', format1)
            sheet.write(6, 19, 'Date of Birth', format1)
        if data['pfund'] == True:
            sheet.write(6, 20, 'Pfund', format1)
        if data['eobi_number'] == True:
            sheet.write(6, 21, 'EOBI Number', format1)
        if data['gratuity'] == True:
            sheet.write(6, 22, 'Gratuity', format1)
        if data['contract_details'] == True:
            sheet.write(6, 23, 'Contract', format1)
        
        format2 = workbook.add_format({'font_size': '12', 'align': 'vcenter'})
        row = 7
        sheet.set_column(row, 0, 50)
        sheet.set_column(row, 1, 25)
        sheet.set_column(row, 2, 20)
        sheet.set_column(row, 3, 20)
        sheet.set_column(row, 4, 20)
        sheet.set_column(row, 5, 20)
        sheet.set_column(row, 6, 20)
        sheet.set_column(row, 7, 20)
        sheet.set_column(row, 8, 20)
        sheet.set_column(row, 9, 20)
        sheet.set_column(row, 10, 20)
        sheet.set_column(row, 11, 25)
        sheet.set_column(row, 12, 20)
        sheet.set_column(row, 13, 20)
        sheet.set_column(row, 14, 20)
        sheet.set_column(row, 15, 20)
        sheet.set_column(row, 16, 20)
        sheet.set_column(row, 17, 20)
        sheet.set_column(row, 18, 20)
        sheet.set_column(row, 19, 20)
        sheet.set_column(row, 20, 20)
        sheet.set_column(row, 21, 20)
        sheet.set_column(row, 22, 20)        
        sheet.set_column(row, 23, 20)    
        
        for o in active_contract:
            if data['assets'] == True:
                if o.employee_id.asset_lines:
                    for al in o.employee_id.asset_lines:
                        if o.employee_id.emp_type:
                            emp_type = o.employee_id.emp_type
                        if o.employee_id.grade_type:
                            gtype = o.employee_id.grade_type.name
                        if o.employee_id.department_id:
                            dept = o.employee_id.department_id.name
                        if data['email'] == True:
                            email = o.employee_id.private_email
                        else:
                            email = None
                        if data['mobile'] == True:
                            mobile = o.employee_id.mobile_phone
                        else:
                            mobile = None
                        if data['address'] == True:
                            address = o.employee_id.address_home_id.name
                        else:
                             address = None
                        if data['religion'] == True:
                            religion = o.employee_id.religion
                        else:
                            religion = None
                        if data['cnic'] == True:
                            cnic = o.employee_id.cnic
                        else:
                            cnic = None
                        if data['blood_group'] == True:
                            blood_group = o.employee_id.blood_group
                        else:
                            blood_group = None
                        if data['bank_account_number'] == True:
                            bank_account_number = o.employee_id.bank_account_id
                        else:
                            bank_account_number = None
                        if data['card_no'] == True:
                            card_no = o.employee_id.identification_id
                        else:
                            card_no = None
                        if data['emergency_contact'] == True:
                            emergency_contact = o.employee_id.emergency_contact
                        else:
                            emergency_contact = None
                        if data['assets'] == True:
                            if o.employee_id.asset_lines:
                                if al.asset_id:
                                    asset_id = al.asset_id
                                if al.issue_date:
                                    issue_date = al.issue_date.strftime("%Y/%m/%d")
                                if al.estimated_life_span:
                                    estimated_life_span = al.estimated_life_span
                                if al.recovery_date:
                                    recovery_date = al.recovery_date.strftime("%Y/%m/%d")
                                if al.description:
                                    description = al.description
                            else:
                                asset_id = None
                                issue_date = None
                                estimated_life_span = None
                                recovery_date = None
                                description = None
                        else:
                            asset_id = None
                            issue_date = None
                            estimated_life_span = None
                            recovery_date = None
                            description = None
                                
                        if data['dependent'] == True:
                            if o.employee_id.employee_family_ids:
                                for f in o.employee_id.employee_family_ids:
                                    if f.name:
                                        f_name = f.name
                                    if f.relation_ship:
                                        f_relationship = f.relation_ship
                                    if f.date_of_birth:
                                        f_dob = f.date_of_birth.strftime("%Y/%m/%d")
                            else:
                                f_name = None
                                f_relationship = None
                                f_dob = None
                        else:
                            f_name = None
                            f_relationship = None
                            f_dob = None
                        
                        if data['pfund'] == True:
                            pfund = o.employee_id.identification_id
                        else:
                            pfund = None
                        if data['eobi_number'] == True:
                            eobi_number = o.employee_id.eobi_number
                        else:
                            eobi_number = None
                        if data['gratuity'] == True:
                            gratuity = o.employee_id.gratuity
                        else:
                            gratuity = None
                        if data['contract_details'] == True:
                            pass
                            #contract_details = o.employee_id.gratuity
                        
                        sheet.write(row, 0, emp_type, format2)
                        sheet.write(row, 1, gtype, format2)
                        sheet.write(row, 2, dept, format2)
                        sheet.write(row, 3, email, format2)
                        sheet.write(row, 4, mobile, format2)
                        sheet.write(row, 5, address, format2)
                        sheet.write(row, 6, religion, format2)
                        sheet.write(row, 7, cnic, format2)
                        sheet.write(row, 8, blood_group, format2)
                        sheet.write(row, 9, bank_account_number, format2)
                        sheet.write(row, 10, card_no, format2)
                        sheet.write(row, 11, emergency_contact, format2)
                        sheet.write(row, 12, asset_id, format2)
                        sheet.write(row, 13, issue_date, format2)
                        sheet.write(row, 14, estimated_life_span, format2)
                        sheet.write(row, 15, recovery_date, format2)
                        sheet.write(row, 16, description, format2)
                        sheet.write(row, 17, f_name, format2)
                        sheet.write(row, 18, f_relationship, format2)
                        sheet.write(row, 19, f_dob, format2)
                        sheet.write(row, 20, pfund, format2)
                        sheet.write(row, 21, eobi_number, format2)
                        sheet.write(row, 22, gratuity, format2)
                        #sheet.write(row, 23, employee['date'], format2)
                        

                        row = row + 1
                
                else:
                    if o.employee_id.emp_type:
                        emp_type = o.employee_id.emp_type
                    if o.employee_id.grade_type:
                        gtype = o.employee_id.grade_type.name
                    if o.employee_id.department_id:
                        dept = o.employee_id.department_id.name
                    if data['email'] == True:
                        email = o.employee_id.private_email
                    else:
                        email = None
                    if data['mobile'] == True:
                        mobile = o.employee_id.mobile_phone
                    else:
                        mobile = None
                    if data['address'] == True:
                        address = o.employee_id.address_home_id.name
                    else:
                         address = None
                    if data['religion'] == True:
                        religion = o.employee_id.religion
                    else:
                        religion = None
                    if data['cnic'] == True:
                        cnic = o.employee_id.cnic
                    else:
                        cnic = None
                    if data['blood_group'] == True:
                        blood_group = o.employee_id.blood_group
                    else:
                        blood_group = None
                    if data['bank_account_number'] == True:
                        bank_account_number = o.employee_id.bank_account_id
                    else:
                        bank_account_number = None
                    if data['card_no'] == True:
                        card_no = o.employee_id.identification_id
                    else:
                        card_no = None
                    if data['emergency_contact'] == True:
                        emergency_contact = o.employee_id.emergency_contact
                    else:
                        emergency_contact = None
                    if data['assets'] == True:
                        if o.employee_id.asset_lines:
                            if al.asset_id:
                                asset_id = al.asset_id
                            if al.issue_date:
                                issue_date = al.issue_date.strftime("%Y/%m/%d")
                            if al.estimated_life_span:
                                estimated_life_span = al.estimated_life_span
                            if al.recovery_date:
                                recovery_date = al.recovery_date.strftime("%Y/%m/%d")
                            if al.description:
                                description = al.description
                        else:
                            asset_id = None
                            issue_date = None
                            estimated_life_span = None
                            recovery_date = None
                            description = None
                    else:
                        asset_id = None
                        issue_date = None
                        estimated_life_span = None
                        recovery_date = None
                        description = None

                    if data['dependent'] == True:
                        if o.employee_id.employee_family_ids:
                            for f in o.employee_id.employee_family_ids:
                                if f.name:
                                    f_name = f.name
                                if f.relation_ship:
                                    f_relationship = f.relation_ship
                                if f.date_of_birth:
                                    f_dob = f.date_of_birth.strftime("%Y/%m/%d")
                        else:
                            f_name = None
                            f_relationship = None
                            f_dob = None
                    else:
                        f_name = None
                        f_relationship = None
                        f_dob = None

                    if data['pfund'] == True:
                        pfund = o.employee_id.identification_id
                    else:
                        pfund = None
                    if data['eobi_number'] == True:
                        eobi_number = o.employee_id.eobi_number
                    else:
                        eobi_number = None
                    if data['gratuity'] == True:
                        gratuity = o.employee_id.gratuity
                    else:
                        gratuity = None
                    if data['contract_details'] == True:
                        pass
                        #contract_details = o.employee_id.gratuity

                    sheet.write(row, 0, emp_type, format2)
                    sheet.write(row, 1, gtype, format2)
                    sheet.write(row, 2, dept, format2)
                    sheet.write(row, 3, email, format2)
                    sheet.write(row, 4, mobile, format2)
                    sheet.write(row, 5, address, format2)
                    sheet.write(row, 6, religion, format2)
                    sheet.write(row, 7, cnic, format2)
                    sheet.write(row, 8, blood_group, format2)
                    sheet.write(row, 9, bank_account_number, format2)
                    sheet.write(row, 10, card_no, format2)
                    sheet.write(row, 11, emergency_contact, format2)
                    sheet.write(row, 12, asset_id, format2)
                    sheet.write(row, 13, issue_date, format2)
                    sheet.write(row, 14, estimated_life_span, format2)
                    sheet.write(row, 15, recovery_date, format2)
                    sheet.write(row, 16, description, format2)
                    sheet.write(row, 17, f_name, format2)
                    sheet.write(row, 18, f_relationship, format2)
                    sheet.write(row, 19, f_dob, format2)
                    sheet.write(row, 20, pfund, format2)
                    sheet.write(row, 21, eobi_number, format2)
                    sheet.write(row, 22, gratuity, format2)
                    #sheet.write(row, 23, employee['date'], format2)


                    row = row + 1
                        
                                    
                            
            elif data['dependent'] == True:
                if o.employee_id.employee_family_ids:
                    for f in o.employee_id.employee_family_ids:
                        if o.employee_id.emp_type:
                            emp_type = o.employee_id.emp_type
                        if o.employee_id.grade_type:
                            gtype = o.employee_id.grade_type.name
                        if o.employee_id.department_id:
                            dept = o.employee_id.department_id.name
                        if data['email'] == True:
                            email = o.employee_id.private_email
                        else:
                            email = None
                        if data['mobile'] == True:
                            mobile = o.employee_id.mobile_phone
                        else:
                            mobile = None
                        if data['address'] == True:
                            address = o.employee_id.address_home_id.name
                        else:
                             address = None
                        if data['religion'] == True:
                            religion = o.employee_id.religion
                        else:
                            religion = None
                        if data['cnic'] == True:
                            cnic = o.employee_id.cnic
                        else:
                            cnic = None
                        if data['blood_group'] == True:
                            blood_group = o.employee_id.blood_group
                        else:
                            blood_group = None
                        if data['bank_account_number'] == True:
                            bank_account_number = o.employee_id.bank_account_id
                        else:
                            bank_account_number = None
                        if data['card_no'] == True:
                            card_no = o.employee_id.identification_id
                        else:
                            card_no = None
                        if data['emergency_contact'] == True:
                            emergency_contact = o.employee_id.emergency_contact
                        else:
                            emergency_contact = None
                        if data['assets'] == True:
                            if o.employee_id.asset_lines:
                                if al.asset_id:
                                    asset_id = al.asset_id
                                if al.issue_date:
                                    issue_date = al.issue_date.strftime("%Y/%m/%d")
                                if al.estimated_life_span:
                                    estimated_life_span = al.estimated_life_span
                                if al.recovery_date:
                                    recovery_date = al.recovery_date.strftime("%Y/%m/%d")
                                if al.description:
                                    description = al.description
                            else:
                                asset_id = None
                                issue_date = None
                                estimated_life_span = None
                                recovery_date = None
                                description = None
                        else:
                            asset_id = None
                            issue_date = None
                            estimated_life_span = None
                            recovery_date = None
                            description = None
                                
                        if data['dependent'] == True:
                            if f.name:
                                f_name = f.name
                            if f.relation_ship:
                                f_relationship = f.relation_ship
                            if f.date_of_birth:
                                f_dob = f.date_of_birth.strftime("%Y/%m/%d")
                        else:
                            f_name = None
                            f_relationship = None
                            f_dob = None
                        
                        if data['pfund'] == True:
                            pfund = o.employee_id.identification_id
                        else:
                            pfund = None
                        if data['eobi_number'] == True:
                            eobi_number = o.employee_id.eobi_number
                        else:
                            eobi_number = None
                        if data['gratuity'] == True:
                            gratuity = o.employee_id.gratuity
                        else:
                            gratuity = None
                        if data['contract_details'] == True:
                            pass
                        
                        sheet.write(row, 0, emp_type, format2)
                        sheet.write(row, 1, gtype, format2)
                        sheet.write(row, 2, dept, format2)
                        sheet.write(row, 3, email, format2)
                        sheet.write(row, 4, mobile, format2)
                        sheet.write(row, 5, address, format2)
                        sheet.write(row, 6, religion, format2)
                        sheet.write(row, 7, cnic, format2)
                        sheet.write(row, 8, blood_group, format2)
                        sheet.write(row, 9, bank_account_number, format2)
                        sheet.write(row, 10, card_no, format2)
                        sheet.write(row, 11, emergency_contact, format2)
                        sheet.write(row, 12, asset_id, format2)
                        sheet.write(row, 13, issue_date, format2)
                        sheet.write(row, 14, estimated_life_span, format2)
                        sheet.write(row, 15, recovery_date, format2)
                        sheet.write(row, 16, description, format2)
                        sheet.write(row, 17, f_name, format2)
                        sheet.write(row, 18, f_relationship, format2)
                        sheet.write(row, 19, f_dob, format2)
                        sheet.write(row, 20, pfund, format2)
                        sheet.write(row, 21, eobi_number, format2)
                        sheet.write(row, 22, gratuity, format2)
                        #sheet.write(row, 23, employee['date'], format2)
                        

                        row = row + 1
                else:
                    if o.employee_id.emp_type:
                        emp_type = o.employee_id.emp_type
                    if o.employee_id.grade_type:
                        gtype = o.employee_id.grade_type.name
                    if o.employee_id.department_id:
                        dept = o.employee_id.department_id.name
                    if data['email'] == True:
                        email = o.employee_id.private_email
                    else:
                        email = None
                    if data['mobile'] == True:
                        mobile = o.employee_id.mobile_phone
                    else:
                        mobile = None
                    if data['address'] == True:
                        address = o.employee_id.address_home_id.name
                    else:
                         address = None
                    if data['religion'] == True:
                        religion = o.employee_id.religion
                    else:
                        religion = None
                    if data['cnic'] == True:
                        cnic = o.employee_id.cnic
                    else:
                        cnic = None
                    if data['blood_group'] == True:
                        blood_group = o.employee_id.blood_group
                    else:
                        blood_group = None
                    if data['bank_account_number'] == True:
                        bank_account_number = o.employee_id.bank_account_id
                    else:
                        bank_account_number = None
                    if data['card_no'] == True:
                        card_no = o.employee_id.identification_id
                    else:
                        card_no = None
                    if data['emergency_contact'] == True:
                        emergency_contact = o.employee_id.emergency_contact
                    else:
                        emergency_contact = None
                    if data['assets'] == True:
                        if o.employee_id.asset_lines:
                            if al.asset_id:
                                asset_id = al.asset_id
                            if al.issue_date:
                                issue_date = al.issue_date.strftime("%Y/%m/%d")
                            if al.estimated_life_span:
                                estimated_life_span = al.estimated_life_span
                            if al.recovery_date:
                                recovery_date = al.recovery_date.strftime("%Y/%m/%d")
                            if al.description:
                                description = al.description
                        else:
                            asset_id = None
                            issue_date = None
                            estimated_life_span = None
                            recovery_date = None
                            description = None
                    else:
                        asset_id = None
                        issue_date = None
                        estimated_life_span = None
                        recovery_date = None
                        description = None

                    if data['dependent'] == True:
                        if o.employee_id.employee_family_ids:
                            for f in o.employee_id.employee_family_ids:
                                if f.name:
                                    f_name = f.name
                                if f.relation_ship:
                                    f_relationship = f.relation_ship
                                if f.date_of_birth:
                                    f_dob = f.date_of_birth.strftime("%Y/%m/%d")
                        else:
                            f_name = None
                            f_relationship = None
                            f_dob = None
                    else:
                        f_name = None
                        f_relationship = None
                        f_dob = None

                    if data['pfund'] == True:
                        pfund = o.employee_id.identification_id
                    else:
                        pfund = None
                    if data['eobi_number'] == True:
                        eobi_number = o.employee_id.eobi_number
                    else:
                        eobi_number = None
                    if data['gratuity'] == True:
                        gratuity = o.employee_id.gratuity
                    else:
                        gratuity = None
                    if data['contract_details'] == True:
                        pass
                        #contract_details = o.employee_id.gratuity

                    sheet.write(row, 0, emp_type, format2)
                    sheet.write(row, 1, gtype, format2)
                    sheet.write(row, 2, dept, format2)
                    sheet.write(row, 3, email, format2)
                    sheet.write(row, 4, mobile, format2)
                    sheet.write(row, 5, address, format2)
                    sheet.write(row, 6, religion, format2)
                    sheet.write(row, 7, cnic, format2)
                    sheet.write(row, 8, blood_group, format2)
                    sheet.write(row, 9, bank_account_number, format2)
                    sheet.write(row, 10, card_no, format2)
                    sheet.write(row, 11, emergency_contact, format2)
                    sheet.write(row, 12, asset_id, format2)
                    sheet.write(row, 13, issue_date, format2)
                    sheet.write(row, 14, estimated_life_span, format2)
                    sheet.write(row, 15, recovery_date, format2)
                    sheet.write(row, 16, description, format2)
                    sheet.write(row, 17, f_name, format2)
                    sheet.write(row, 18, f_relationship, format2)
                    sheet.write(row, 19, f_dob, format2)
                    sheet.write(row, 20, pfund, format2)
                    sheet.write(row, 21, eobi_number, format2)
                    sheet.write(row, 22, gratuity, format2)
                    #sheet.write(row, 23, employee['date'], format2)


                    row = row + 1
            else:
                if o.employee_id.emp_type:
                    emp_type = o.employee_id.emp_type
                if o.employee_id.grade_type:
                    gtype = o.employee_id.grade_type.name
                if o.employee_id.department_id:
                    dept = o.employee_id.department_id.name
                if data['email'] == True:
                    email = o.employee_id.private_email
                else:
                    email = None
                if data['mobile'] == True:
                    mobile = o.employee_id.mobile_phone
                else:
                    mobile = None
                if data['address'] == True:
                    address = o.employee_id.address_home_id.name
                else:
                     address = None
                if data['religion'] == True:
                    religion = o.employee_id.religion
                else:
                    religion = None
                if data['cnic'] == True:
                    cnic = o.employee_id.cnic
                else:
                    cnic = None
                if data['blood_group'] == True:
                    blood_group = o.employee_id.blood_group
                else:
                    blood_group = None
                if data['bank_account_number'] == True:
                    bank_account_number = o.employee_id.bank_account_id
                else:
                    bank_account_number = None
                if data['card_no'] == True:
                    card_no = o.employee_id.identification_id
                else:
                    card_no = None
                if data['emergency_contact'] == True:
                    emergency_contact = o.employee_id.emergency_contact
                else:
                    emergency_contact = None
                if data['assets'] == True:
                    if o.employee_id.asset_lines:
                        if al.asset_id:
                            asset_id = al.asset_id
                        if al.issue_date:
                            issue_date = al.issue_date.strftime("%Y/%m/%d")
                        if al.estimated_life_span:
                            estimated_life_span = al.estimated_life_span
                        if al.recovery_date:
                            recovery_date = al.recovery_date.strftime("%Y/%m/%d")
                        if al.description:
                            description = al.description
                    else:
                        asset_id = None
                        issue_date = None
                        estimated_life_span = None
                        recovery_date = None
                        description = None
                else:
                    asset_id = None
                    issue_date = None
                    estimated_life_span = None
                    recovery_date = None
                    description = None

                if data['dependent'] == True:
                    if o.employee_id.employee_family_ids:
                        for f in o.employee_id.employee_family_ids:
                            if f.name:
                                f_name = f.name
                            if f.relation_ship:
                                f_relationship = f.relation_ship
                            if f.date_of_birth:
                                f_dob = f.date_of_birth.strftime("%Y/%m/%d")
                    else:
                        f_name = None
                        f_relationship = None
                        f_dob = None
                else:
                    f_name = None
                    f_relationship = None
                    f_dob = None

                if data['pfund'] == True:
                    pfund = o.employee_id.identification_id
                else:
                    pfund = None
                if data['eobi_number'] == True:
                    eobi_number = o.employee_id.eobi_number
                else:
                    eobi_number = None
                if data['gratuity'] == True:
                    gratuity = o.employee_id.gratuity
                else:
                    gratuity = None
                if data['contract_details'] == True:
                    pass
                    #contract_details = o.employee_id.gratuity

                sheet.write(row, 0, emp_type, format2)
                sheet.write(row, 1, gtype, format2)
                sheet.write(row, 2, dept, format2)
                sheet.write(row, 3, email, format2)
                sheet.write(row, 4, mobile, format2)
                sheet.write(row, 5, address, format2)
                sheet.write(row, 6, religion, format2)
                sheet.write(row, 7, cnic, format2)
                sheet.write(row, 8, blood_group, format2)
                sheet.write(row, 9, bank_account_number, format2)
                sheet.write(row, 10, card_no, format2)
                sheet.write(row, 11, emergency_contact, format2)
                sheet.write(row, 12, asset_id, format2)
                sheet.write(row, 13, issue_date, format2)
                sheet.write(row, 14, estimated_life_span, format2)
                sheet.write(row, 15, recovery_date, format2)
                sheet.write(row, 16, description, format2)
                sheet.write(row, 17, f_name, format2)
                sheet.write(row, 18, f_relationship, format2)
                sheet.write(row, 19, f_dob, format2)
                sheet.write(row, 20, pfund, format2)
                sheet.write(row, 21, eobi_number, format2)
                sheet.write(row, 22, gratuity, format2)
                #sheet.write(row, 23, employee['date'], format2)


                row = row + 1