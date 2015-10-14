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
from lxml import etree, html
import werkzeug
import pytz
import re

import logging
_logger = logging.getLogger(__name__)

    
class website_form(http.Controller):

    @http.route(['/form/<string:form_name>/add', ], type='http', auth="user", website=True)
    def form_add(self, form_name=False,model_id=False,add_menu=0, thanks_template='website_form.thanks',**post):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        form = request.env['form.form'].create({
                'name': form_name,
                'model_id': model_id,
                'template': request.env['website'].new_page(form_name), 
                'thanks_template': thanks_template
            })
        
        _logger.warning("This is form postnr %s" % (form))



        if add_menu:
            model, id  = request.registry["ir.model.data"].get_object_reference(request.cr, request.uid, 'website', 'main_menu')
            request.registry['website.menu'].create(request.cr, request.uid, {
                    'name': form.name,
                    'url': "/form/" + form.name,
                    'parent_id': id,
                }, context=request.context)

        return werkzeug.utils.redirect("/form/"+form.name)

    @http.route(['/form/<string:form>', ], type='http', auth="public", website=True)
    def form_view(self, form=False,**post):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        form = request.env['form.form'].search([('name','=', form)])
        if request.httprequest.method == 'POST':            
            form.form_save(form.model_id.model,post)
            return werkzeug.utils.redirect(form.thanks_url)
            

        return request.render(form.template, {'form': form})

 

    @http.route(['/form/<string:form>/edit', ], type='http', auth="user", website=True)
    def form_edit(self, form=False,**post):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        form = request.env['form.form'].search([('name','=', form)])
        if request.httprequest.method == 'POST':

            form_data = dict((field_name, post.pop('form.' + field_name))
                for field_name in form.fields_get().keys() if post.get('form.'+field_name))

            post_keys = list(key for key in post.keys())
            _logger.warning("This is form post %s" % (post_keys))
            form.write(form_data)
        return request.render('website_form.edit', {'form': form})



class form_form(models.Model):
    _name = 'form.form'
    _description = 'Simple Form'
    _order = 'name'

    name = fields.Char('Name',required=True)
    model_id = fields.Many2one(comodel_name='ir.model',string='Model')
    thanks_url = fields.Char('Thanks Url', default="/page/website_form.thank_you")
    auth_type = fields.Selection([('public','public'),('user','user'),('admin','admin')])
    template = fields.Char('Template', required = True)

    def form_eval(self,model,post):
        serial_fields = {}
        for key in post.keys():  # fields project.issue.description_1 .. nn
            if re.match(".*_(\d+)", key):
                field_name = key.split('_')[0].split('.')[-1]  # crm.lead.description_01  -> description
                if serial_fields.get(field_name):
                    serial_fields[field_name].append(post.pop(key))
                else:
                    serial_fields[field_name] = [post.pop(key)]
        form_data = dict((field_name, post.pop(model + '.' + field_name))  # fields project.issue.name -> { 'name': post.pop['value'] }
                         for field_name in self.env[model].fields_get().keys()
                         if post.get(model + '.' + field_name))
        for key in serial_fields.keys():
            if type(serial_fields[key]) is list:
                form_data[key] = ', '.join(serial_fields[key])  # description_01, description_nn -> { 'description': 'value01, value02, valueNN' }    
        return form_data
        
    def form_save(self,**post):
        form_data = self.form_eval(self.model_id.model,post)
        if form_data['id']:
            object = self.search([('id','=',form_data.pop('id'))])
            object.write(form_data)
        else:
            self.create(form_data)


