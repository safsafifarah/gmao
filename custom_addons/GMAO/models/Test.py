from odoo import api, fields, models

class Test (models.Model):
    _name="gmao.test"
    _description ="Test Model"
    name= fields. Char(string='Name', required=True)
    age =fields. Integer (string="Age")
    is_urgent = fields. Boolean (string="Is Urgent ?")
    notes = fields.Text(string="Notes")
