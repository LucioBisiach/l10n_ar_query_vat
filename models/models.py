# -*- coding: utf-8 -*-

from odoo import models, fields ,api, _
from odoo.exceptions import ValidationError
from odoo.tools import config

import requests
import urllib
import json

import logging
_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit = 'res.partner'

    vat = fields.Char(copy=False)
    compute_api_data_tango = fields.Boolean(string="Compute API data Tango", default=False, store=True, compute="_compute_api_data_tango")

    @api.depends('vat')
    def _compute_api_data_tango(self):
        for rec in self:
            if not rec.vat:
                rec.compute_api_data_tango = False
            if rec.compute_api_data_tango == False and rec.vat and len(rec.vat) == 11:
                API_URL = 'https://afip.tangofactura.com/Index/GetContribuyenteWithImpuestos/?cuit='
                res = requests.get(API_URL + rec.vat)
                if res.status_code == 200:
                    jsonObject = res.json()

                    if 'error' in jsonObject:
                        raise ValidationError("Invalid VAT/CUIT/CUIL")

                    if jsonObject['Contribuyente']['EsRI'] == True:
                        responsibility_type_id = self.env['l10n_ar.afip.responsibility.type'].search([('code','=','1')])
                    if jsonObject['Contribuyente']['EsExento'] == True:
                        responsibility_type_id = self.env['l10n_ar.afip.responsibility.type'].search([('code','=','4')])
                    if jsonObject['Contribuyente']['EsMonotributo'] == True:
                        responsibility_type_id = self.env['l10n_ar.afip.responsibility.type'].search([('code','=','6')])
                    if jsonObject['Contribuyente']['EsConsumidorFinal'] == True:
                        responsibility_type_id = self.env['l10n_ar.afip.responsibility.type'].search([('code','=','5')])

                    if responsibility_type_id:
                        country = self.env['res.country'].search([('code','=','AR')])

                    identification_type = self.env['l10n_latam.identification.type'].search([('name','=',jsonObject['Contribuyente']['tipoClave'])])
                    name_state = jsonObject['Contribuyente']['domicilioFiscal']['nombreProvincia'].title()
                    state_id = self.env['res.country.state'].search([('name','in',[name_state])])
                    
                    rec.write({
                        'name': jsonObject['Contribuyente']['nombre'],
                        'street': jsonObject['Contribuyente']['domicilioFiscal']['direccion'],
                        'city': jsonObject['Contribuyente']['domicilioFiscal']['localidad'],
                        'zip': jsonObject['Contribuyente']['domicilioFiscal']['codPostal'],
                        'l10n_ar_afip_responsibility_type_id': responsibility_type_id or False,
                        'country_id': country.id or False,
                        'l10n_latam_identification_type_id': identification_type or False,
                        'state_id': state_id or False
                    })


    @api.constrains("vat")
    def _check_vat_unique(self):
        for record in self:
            if 'skip_required_vat' not in record.env.context:
                if record.parent_id or not record.vat:
                    continue
                test_condition = config["test_enable"] and not self.env.context.get("test_vat")
                if test_condition:
                    continue
                if record.vat:
                    if record.vat.find('-') > 0:
                        raise ValidationError(_('El número de CUIT no puede contener guiones'))
                if record.same_vat_partner_id:
                    raise ValidationError(_("Ya existe un contacto registrado con el N° de identificación %s.") % record.vat
                    )
                    
