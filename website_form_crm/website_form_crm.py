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


def form_eval(model,**post):
    serial_fields = {}
    for key in post.keys():  # fields project.issue.description_1 .. nn
        if re.match(".*_(\d+)", key):
            field_name = key.split('_')[0].split('.')[-1]  # crm.lead.description_01  -> description
            if serial_fields.get(field_name):
                serial_fields[field_name].append(post.pop(key))
            else:
                serial_fields[field_name] = [post.pop(key)]
    form_data = dict((field_name, post.pop(form.model_id.model + '.' + field_name))  # fields project.issue.name -> { 'name': post.pop['value'] }
                     for field_name in request.env[form.model_id.model].fields_get().keys()
                     if post.get(form.model_id.model + '.' + field_name))
    for key in serial_fields.keys():
        if type(serial_fields[key]) is list:
            form_data[key] = ', '.join(serial_fields[key])  # description_01, description_nn -> { 'description': 'value01, value02, valueNN' }    
    return form_data

class website_form_crm(http.Controller):
    @http.route(['/form/<string:form>/lead/<model("crm.lead"):lead>', ], type='http', auth="user", website=True)
    def form_lead(self, form=False, lead=False, **post):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        form = request.env['form.form'].search([('name', '=', form)])
        if not form:
            return request.render('website.page_404', {})            
        if not lead:
            return request.render('website.page_404', {})

        if request.httprequest.method == 'POST':
            #~ serial_fields = {}
            #~ for key in post.keys():  # fields project.issue.description_1 .. nn
                #~ if re.match(".*_(\d+)", key):
                    #~ field_name = key.split('_')[0].split('.')[-1]
                    #~ _logger.warning("Lead_id split: fieldname: %s" % (field_name))
                    #~ if serial_fields.get(field_name):
                        #~ serial_fields[field_name].append(post.pop(key))
                    #~ else:
                        #~ serial_fields[field_name] = [post.pop(key)]
            #~ form_data = dict((field_name, post.pop(form.model_id.model + '.' + field_name))  # fields project.issue.name
                             #~ for field_name in request.env[form.model_id.model].fields_get().keys()
                             #~ if post.get(form.model_id.model + '.' + field_name))
            #~ for key in serial_fields.keys():
                #~ if type(serial_fields[key]) is list:
                    #~ form_data[key] = ', '.join(serial_fields[key])

            form_data = form_eval(form.model_id.model,post)
            _logger.debug("Form Data %s %s" % (form_data, post))
            
            partner = request.env['res.partner'].create({'is_company': True, 'name': form_data['partner_name'], 'email': form_data.get('email_from',''),  'phone': form_data.get('phone',''), 'mobile':form_data.get('mobile',''), 'ref': form_data.get('contact_name','') })
            form_data['partner_id'] = partner.id
            form_data['type'] = 'opportunity'
            form_data['stage_id'] = request.env.ref('crm.stage_lead1').id
            lead.write(form_data)
            
            return werkzeug.utils.redirect(form.thanks_url)

        return request.render('website_form_crm.lead_form', {'form': form, 'lead': lead})

