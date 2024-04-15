# Copyright 2022-2024 Tecnativa - Víctor Martínez
# Copyright 2024 Tecnativa - Carolina Fernandez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import fields
from odoo.tests import Form, common, new_test_user
from odoo.tests.common import users

from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT


class TestAccountMove(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, **DISABLED_MAIL_CONTEXT))
        new_test_user(
            cls.env, login="test-account-user", groups="account.group_account_invoice"
        )
        cls.categ = cls.env["product.category"].create({"name": "Test category"})
        cls.product_a = cls.env["product.product"].create(
            {"name": "Test product A", "maintenance_ok": True, "categ_id": cls.categ.id}
        )
        cls.product_b = cls.env["product.product"].create(
            {"name": "Test product B", "categ_id": cls.categ.id}
        )
        cls.account_payable = cls.env["account.account"].create(
            {
                "name": "Test Account",
                "code": "TEST",
                "account_type": "liability_payable",
                "reconcile": True,
            }
        )
        cls.account_expense = cls.env["account.account"].create(
            {
                "name": "Test Account",
                "code": "ACC",
                "account_type": "expense",
            }
        )
        cls.journal = cls.env["account.journal"].create(
            {
                "name": "Test purchase journal",
                "type": "purchase",
                "code": "TEST-PURCHASE",
            }
        )
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test partner",
            }
        )

    def _create_invoice(self, move_type="in_invoice"):
        move_form = Form(
            self.env["account.move"].with_context(default_move_type=move_type)
        )
        move_form.partner_id = self.partner
        move_form.ref = "SUPPLIE-REF"
        move_form.invoice_date = fields.Date.from_string("2000-01-01")
        with move_form.invoice_line_ids.new() as line_form:
            line_form.product_id = self.product_a
            line_form.name = "Product A\nTest description product A\nB"
            line_form.quantity = 2
        with move_form.invoice_line_ids.new() as line_form:
            line_form.product_id = self.product_b
            line_form.quantity = 2
        invoice = move_form.save()
        return invoice

    @users("test-account-user")
    def test_invoice_out_invoice_action_post_equipment_1(self):
        invoice = self._create_invoice("out_invoice")
        line_a = invoice.line_ids.filtered(lambda x: x.product_id == self.product_a)
        line_b = invoice.line_ids.filtered(lambda x: x.product_id == self.product_b)
        self.assertFalse(line_a.equipment_category_id)
        self.assertFalse(line_b.equipment_category_id)
        invoice.action_post()
        equipments = invoice.mapped("line_ids.equipment_ids")
        self.assertEqual(len(equipments), 0)

    @users("test-account-user")
    def test_invoice_action_post_equipment_1(self):
        invoice = self._create_invoice()
        line_a = invoice.line_ids.filtered(lambda x: x.product_id == self.product_a)
        line_b = invoice.line_ids.filtered(lambda x: x.product_id == self.product_b)
        self.assertFalse(line_a.equipment_category_id)
        self.assertFalse(line_b.equipment_category_id)
        invoice.action_post()
        equipments = invoice.mapped("line_ids.equipment_ids")
        self.assertEqual(len(equipments), 2)
        self.assertTrue(line_a.equipment_category_id)
        self.assertEqual(len(line_a.equipment_ids), 2)
        self.assertEqual(len(line_b.equipment_ids), 0)
        equipment = fields.first(equipments)
        self.assertEqual(equipment.name, "Product A")
        self.assertEqual(equipment.note, "<p>Test description product A<br>B</p>")
        self.assertEqual(equipment.category_id.product_category_id, self.categ)
        self.assertEqual(equipment.assign_date, invoice.date)
        self.assertEqual(equipment.effective_date, invoice.date)
        self.assertEqual(equipment.partner_id, self.partner)
        self.assertEqual(equipment.partner_ref, invoice.ref)

    @users("test-account-user")
    def test_invoice_action_post_equipment_1_multi_lines(self):
        self.product_b.maintenance_ok = True
        invoice = self._create_invoice()
        line_a = invoice.line_ids.filtered(lambda x: x.product_id == self.product_a)
        line_b = invoice.line_ids.filtered(lambda x: x.product_id == self.product_b)
        invoice.action_post()
        equipments = invoice.mapped("line_ids.equipment_ids")
        self.assertEqual(len(equipments.mapped("category_id")), 1)
        self.assertEqual(line_a.equipment_category_id, line_b.equipment_category_id)

    @users("test-account-user")
    def test_invoice_action_post_equipment_2(self):
        category = (
            self.env["maintenance.equipment.category"]
            .sudo()
            .create({"name": self.categ.name, "product_category_id": self.categ.id})
        )
        invoice = self._create_invoice()
        line_a = invoice.line_ids.filtered(lambda x: x.product_id == self.product_a)
        self.assertEqual(line_a.equipment_category_id, category)
        invoice.action_post()
        equipment = fields.first(line_a.equipment_ids)
        self.assertEqual(equipment.category_id, category)
