# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution, third party addon
#    Copyright (C) 2004-2015 Vertel AB (<http://vertel.se>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning
from openerp import http
from openerp.http import request
from openerp import SUPERUSER_ID
from datetime import datetime
import werkzeug
import pytz
import re

import logging
_logger = logging.getLogger(__name__)

class website_form_crm(http.Controller):


    @http.route(['/form/<string:form>/lead', ], type='http', auth="public", website=True)
    def form_lead(self, form=False,**post):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        form = request.env['form.form'].search([('name','=', form)])
        if request.httprequest.method == 'POST':
            form_data = {}
            for key in post.keys():  # fields project.issue.description_1 .. nn
                if re.match(".*_(\d+)",key):
                    (field_name,nr) = re.split('_',key,1)
                    if form_data.get(field_name):
                        form_data[field_name].append(post.get(key))
                    else:
                        form_data[field_name] = [post.get(key)]
            for key in form_data.keys():
                if type(form_data[key]) is list:
                    form_data[key] = ', '.join(form_data[key])

            form_data = dict((field_name, post.pop(form.model_id.model + '.' + field_name))  # fields project.issue.name
                for field_name in request.env[form.model_id.model].fields_get().keys()
                             if post.get(form.model_id.model + '.' + field_name))

            form_so = {'sale.order': form_data}
            _logger.warning("Form Data %s %s" % (form_data, post))
            object = request.env[form.model_id.model].create(form_data)
            _logger.warning("Form created object %s" % (object))
            return werkzeug.utils.redirect(form.thanks_url)

        _logger.warning("This is form post %s %s" % (form, post))
        return request.render('website_form.form', {'form': form})





#~ class form_form(models.Model):
    #~ _name = 'form.form'
    #~ _description = 'Simple Form'
    #~ _order = 'name'
#~ 
    #~ name = fields.Char('Name',required=True)
    #~ model_id = fields.Many2one(comodel_name='ir.model',string='Model')
    #~ body = fields.Html('Body',sanitize=False)
    #~ thanks_url = fields.Char('Thanks Url', default="/page/website_form.thank_you")
    #~ auth_type = fields.Selection([('public','public'),('user','user'),('admin','admin')])



