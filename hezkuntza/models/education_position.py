# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from eagle import _, api, models
from eagle.exceptions import ValidationError


class EducationPosition(models.Model):
    _inherit = 'education.position'

    @api.constrains('education_code')
    def _check_education_code(self):
        code_length = 3
        for record in self:
            if not len(record.education_code) == code_length:
                raise ValidationError(
                    _('Education Code must be {} digits long!').format(
                        code_length))