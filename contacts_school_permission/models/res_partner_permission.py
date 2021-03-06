# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from eagle import api, fields, models


class ResPartnerPermission(models.Model):
    _name = 'res.partner.permission'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = 'Contact Permission'
    _rec_name = 'partner_id'

    partner_id = fields.Many2one(
        comodel_name='res.partner', string='Student', required=True,
        domain=[('educational_category', 'in', ('student', 'other'))])
    allowed_signer_ids = fields.Many2many(
        comodel_name='res.partner', string='Allowed Signers',
        compute='_compute_allowed_signer_ids', store=True)
    signer_id = fields.Many2one(
        comodel_name='res.partner', string='Signed by',
        domain="[('id', 'in', allowed_signer_ids)]")
    type_id = fields.Many2one(
        comodel_name='res.partner.permission.type', string='Type',
        required=True)
    type_description = fields.Text(
        string='Type Description', related='type_id.description', store=True)
    description = fields.Text(string='Description')
    state = fields.Selection(
        selection=[('yes', 'Yes'),
                   ('no', 'No'),
                   ('pending', 'Pending')], string='State', default='pending',
        required=True)
    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')
    attachment_doc = fields.Binary(string='Attached Document')

    @api.depends('partner_id', 'partner_id.child2_ids',
                 'partner_id.child2_ids.relation',
                 'partner_id.child2_ids.responsible_id')
    def _compute_allowed_signer_ids(self):
        for record in self:
            record.allowed_signer_ids = (
                record.partner_id.child2_ids.filtered(
                    lambda l: l.relation in ('progenitor', 'guardian')
                ).mapped('responsible_id'))

    def button_sign(self):
        self.ensure_one()
        self.write({
            'state': 'yes',
            'signer_id': self.env.user.partner_id.id,
        })

    def button_deny(self):
        self.ensure_one()
        self.write({
            'state': 'no',
            'signer_id': self.env.user.partner_id.id,
        })


class ResPartnerPermissionType(models.Model):
    _name = 'res.partner.permission.type'
    _description = 'Permission Type'

    name = fields.Char(string='Name')
    description = fields.Text(string='Description')
    admission_default = fields.Boolean(string='Default in Admission')


class ResPartner(models.Model):
    _inherit = 'res.partner'

    permission_ids = fields.One2many(
        comodel_name='res.partner.permission', inverse_name='partner_id',
        string='Permissions')
