# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2016 ITS-1 (<http://www.its1.lv/>)
#                       E-mail: <info@its1.lv>
#                       Address: <Vienibas gatve 109 LV-1058 Riga Latvia>
#                       Phone: +371 66116534
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

import time
from openerp.report import report_sxw
from openerp.osv import osv

class report_stock_inventory(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(report_stock_inventory, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'cr':cr,
            'uid': uid,
            'get_numbers': self.get_numbers,
            'get_cost': self.get_cost,
            'get_totals': self.get_totals
        })
        self.context = context

    def get_numbers(self, lines):
        data = {}
        n = 0
        for l in lines:
            n += 1
            data.update({l.id: n})
        return data

    def get_cost(self, line):
        if line.product_qty > line.theoretical_qty:
            cost = line.product_id.standard_price
        else:
            inv_line_obj = self.pool.get('stock.inventory.line')
            quant_ids = inv_line_obj._get_quants(self.cr, self.uid, line, context=self.context)
            quant_obj = self.pool.get('stock.quant')
            total_cost = 0.0
            total_qty = 0.0
            for quant in quant_obj.browse(self.cr, self.uid, quant_ids, context=self.context):
                total_cost += (quant.cost * quant.qty)
                total_qty += quant.qty
            cost = total_qty != 0.0 and total_cost / total_qty or 0.0
        return cost

    def get_totals(self, lines):
        qty = 0.0
        value = 0.0
        for l in lines:
            qty += l.theoretical_qty
            cost = self.get_cost(l)
            value += (cost * l.theoretical_qty)
        return {'quantity': qty, 'value': value}

class report_inventory(osv.AbstractModel):
    _name = 'report.stock.report_inventory'
    _inherit = 'report.abstract_report'
    _template = 'stock.report_inventory'
    _wrapped_report_class = report_stock_inventory

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: