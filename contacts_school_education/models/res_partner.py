# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from eagle import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    next_course_ids = fields.One2many(
        comodel_name='education.course.change', inverse_name='school_id',
        string='Next Courses')
    prev_course_ids = fields.One2many(
        comodel_name='education.course.change', inverse_name='next_school_id',
        string='Previous Courses')
    alumni_center_id = fields.Many2one(
        comodel_name='res.partner', string='Last Education Center',
        domain=[('educational_category', '=', 'school')])
    alumni_academic_year_id = fields.Many2one(
        comodel_name='education.academic_year', string='Last Academic Year')
    alumni_member = fields.Boolean(string='Alumni Association Member')
    student_group_ids = fields.Many2many(
        comodel_name='education.group', relation='edu_group_student',
        column1='student_id', column2='group_id', string='Education Groups',
        readonly=True, domain="[('group_type_id.type', '=', 'official')]")
    current_group_id = fields.Many2one(
        comodel_name='education.group', string='Current Group',
        compute='_compute_current_group_id')
    current_center_id = fields.Many2one(
        comodel_name='res.partner', string='Current Education Center',
        compute='_compute_current_group_id',
        search='_search_current_center_id',
        domain="[('educational_category', '=', 'school')]")
    current_course_id = fields.Many2one(
        comodel_name='education.course', string='Current Course',
        compute='_compute_current_group_id',
        search='_search_current_course_id')
    childs_current_center_ids = fields.Many2many(
        comodel_name='res.partner',
        string='Children\'s Current Education Centers',
        compute='_compute_child_current_group_ids',
        search='_search_parent_current_center_id')
    childs_current_course_ids = fields.Many2many(
        comodel_name='education.course',
        string='Children\'s Current Courses',
        compute='_compute_child_current_group_ids',
        search='_search_parent_current_course_id')

    @api.depends('student_group_ids')
    def _compute_current_group_id(self):
        today = fields.Date.context_today(self)
        current_year = self.env['education.academic_year'].search([
            ('date_start', '<=', today), ('date_end', '>=', today)], limit=1)
        for partner in self.filtered(
                lambda p: p.educational_category == 'student'):
            groups = partner.student_group_ids.filtered(
                lambda g: g.group_type_id.type == 'official' and
                g.academic_year_id == current_year)
            partner.current_group_id = groups[:1]
            partner.current_center_id = partner.current_group_id.center_id
            partner.current_course_id = partner.current_group_id.course_id

    @api.multi
    def _search_current_center_id(self, operator, value):
        if operator == '=':
            centers = self.browse(value)
        else:
            centers = self.search([
                (self._rec_name, operator, value),
                ('educational_category', '=', 'school'),
            ])
        groups = self._search_current_groups().filtered(
            lambda g: g.center_id in centers)
        return [('id', 'in', groups.mapped('student_ids').ids)]

    @api.multi
    def _search_current_course_id(self, operator, value):
        course_obj = self.env['education.course']
        if operator == '=':
            courses = course_obj.browse(value)
        else:
            courses = course_obj.search([
                (course_obj._rec_name, operator, value),
            ])
        groups = self._search_current_groups().filtered(
            lambda g: g.course_id in courses)
        return [('id', 'in', groups.mapped('student_ids').ids)]

    @api.depends('child_ids', 'child_ids.current_group_id')
    def _compute_child_current_group_ids(self):
        for partner in self.filtered(
                lambda p: p.educational_category == 'family'):
            childs_groups = partner.mapped(
                'child_ids.current_group_id')
            partner.childs_current_center_ids = [
                (6, 0, childs_groups.mapped('center_id').ids)]
            partner.childs_current_course_ids = [
                (6, 0, childs_groups.mapped('course_id').ids)]

    @api.multi
    def _search_parent_current_center_id(self, operator, value):
        if operator == '=':
            centers = self.browse(value)
        else:
            centers = self.search([
                (self._rec_name, operator, value),
                ('educational_category', '=', 'school'),
            ])
        groups = self._search_current_groups().filtered(
            lambda g: g.center_id in centers)
        return [('id', 'in', groups.mapped('student_ids.parent_id').ids)]

    @api.multi
    def _search_parent_current_course_id(self, operator, value):
        course_obj = self.env['education.course']
        if operator == '=':
            courses = course_obj.browse(value)
        else:
            courses = course_obj.search([
                (course_obj._rec_name, operator, value),
            ])
        groups = self._search_current_groups().filtered(
            lambda g: g.course_id in courses)
        return [('id', 'in', groups.mapped('student_ids.parent_id').ids)]

    @api.multi
    def _search_current_groups(self):
        today = fields.Date.context_today(self)
        current_year = self.env['education.academic_year'].search([
            ('date_start', '<=', today), ('date_end', '>=', today)], limit=1)
        official_type = self.env['education.group_type'].search([
            ('type', '=', 'official')])
        return self.env['education.group'].search([
            ('academic_year_id', '=', current_year.id),
            ('group_type_id', 'in', official_type.ids)
        ])
