# -*- coding: utf-8 -*-
from datetime import datetime as dt
import traceback, os, sys, random

# turbogears imports
from tg import expose, redirect, validate, flash, request, response
from tg.controllers import CUSTOM_CONTENT_TYPE

# third party imports
from paste.fileapp import FileApp
from pylons.controllers.util import forward
from repoze.what import predicates,authorize
from repoze.what.predicates import not_anonymous,in_group,has_permission

# project specific imports
from budget.lib.base import BaseController
from budget.model import *
from budget.util.common import *
from budget.util.excel_helper import *
from budget.widgets.order import *

__all__ = ['ReportController']

class ReportController(BaseController):
    #Uncomment this line if your controller requires an authenticated user
    allow_only = authorize.not_anonymous()
    
    @expose('budget.templates.report.index')
    @tabFocus(tab_type="report")
    def index(self):
        try:
            report_form = order_report
        
            return dict(report_form = report_form, values = {})
        except:
            traceback.print_exc()

    @expose()
    def export(self, **kw):
        result_data = []
        additionInfo = []
        current = dt.now()
        dateStr = current.today().strftime("%Y%m%d")
        fileDir = os.path.join(os.path.abspath(os.path.curdir),"report_download","%s" % dateStr)
        
        if not os.path.exists(fileDir): os.makedirs(fileDir)
        
        timeStr = current.time().strftime("%H%M%S")
        rn = random.randint(0,10000)
        username = 'budget_sportsware'#request.identity['repoze.who.userid']
        filename = os.path.join(fileDir, "%s_%s_%d.xls" % (username, timeStr, rn))
        templatePath = os.path.join(os.path.abspath(os.path.curdir),"report_download/TEMPLATE/TRB_TEMPLATE.xls")
        pe = JCPExcel(templatePath = templatePath, destinationPath = filename)
        
        query_fields = {"orderDate": "Order Date",
                        "customerPO": "Customer PO#",
                        "tel": "Tel",
                        "billCompany": "Bill Company",
                        "billAddress": "Bill Address",
                        "billAttn": "Bill Attn",
                        "billTel": "Bill Tel",
                        "billFax": "Bill Fax",
                        "shipCompany": "Ship Company",
                        "shipAddress": "Ship Address",
                        "shipAttn": "Ship Attn",
                        "shipTel": "Ship Tel",
                        "shipFax": "Ship Fax",
                        "requestShipDate": "Request Ship Date",}
        
        if kw:
            for k, v in kw.iteritems():
                if kw[k]:
                    additionItem = query_fields[k] + ": " + kw[k]
                    additionInfo.append(additionItem)

        try:
            results = self._query_result(**kw)
            
            if results:
                for result in results:
                        result_data.extend(self._format_value(result)) 
            
            pe.inputData(additionInfo = additionInfo, data = result_data)
            pe.outputData()
            
            return serveFile(unicode(filename))
        except:
            traceback.print_exc()
            if pe: pe.clearData()
            flash("Error occur in the Excel Exporting !")
            raise redirect("report")
    
    def _format_value(self, trb_form):
        results = []
        
        for detail_item in trb_form.formDetails:
            result = []
            quantity = detail_item.quantity
                
            result = trb_form.populate()
            result.append(str(quantity))
            results.append(result)
        
        return results
    
    def _query_result(self, **kw):
        try:
            conditions = []
            
            if kw.get("orderDate",False):
                date = dt.strptime(kw.get("orderDate",'2009-12-1200:00:00') + "00:00:00", "%Y-%m-%d%H:%M:%S")
                conditions.append(TRBOrderFormHeader.orderDate >= date)
            if kw.get("customerPO", False):
                conditions.append(TRBOrderFormHeader.customerPO.like("%%%s%%" % kw.get("customerPO", "")))
            if kw.get("tel", False):
                conditions.append(TRBOrderFormHeader.tel.like("%%%s%%" % kw.get("tel", "")))
            if kw.get("requestShipDate",False):
                date = dt.strptime(kw.get("requestShipDate",'2009-12-1200:00:00') + "23:59:59", "%Y-%m-%d%H:%M:%S")
                conditions.append(TRBOrderFormHeader.requestShipDate >= date)
            if kw.get("shipMethod", False):
                conditions.append(TRBOrderFormHeader.shipMethod.like("%%%s%%" % kw.get("shipMethod", "")))
            if kw.get("billCompany", False):
                conditions.append(TRBOrderFormHeader.billId == TRBBillTo.id)
                conditions.append(TRBBillTo.billCompany.like("%%%s%%" % kw.get("billCompany", "")))
            if kw.get("billAddress", False):
                conditions.append(TRBOrderFormHeader.billId == TRBBillTo.id)
                conditions.append(TRBBillTo.billAddress.like("%%%s%%" % kw.get("billAddress", "")))
            if kw.get("billAttn", False):
                conditions.append(TRBOrderFormHeader.billId == TRBBillTo.id)
                conditions.append(TRBBillTo.billAttn.like("%%%s%%" % kw.get("billAttn", "")))
            if kw.get("billTel", False):
                conditions.append(TRBOrderFormHeader.billId == TRBBillTo.id)
                conditions.append(TRBBillTo.billTel.like("%%%s%%" % kw.get("billTel", "")))
            if kw.get("billFax", False):
                conditions.append(TRBOrderFormHeader.billId == TRBBillTo.id)
                conditions.append(TRBBillTo.billFax.like("%%%s%%" % kw.get("billFax", "")))
            if kw.get("shipCompany", False):
                conditions.append(TRBOrderFormHeader.shipId == TRBShipTo.id)
                conditions.append(TRBShipTo.shipCompany.like("%%%s%%" % kw.get("shipCompany", "")))
            if kw.get("shipAddress", False):
                conditions.append(TRBOrderFormHeader.shipId == TRBShipTo.id)
                conditions.append(TRBShipTo.shipAddress.like("%%%s%%" % kw.get("shipAddress", "")))
            if kw.get("shipAttn", False):
                conditions.append(TRBOrderFormHeader.shipId == TRBShipTo.id)
                conditions.append(TRBShipTo.shipAttn.like("%%%s%%" % kw.get("shipAttn", "")))
            if kw.get("shipTel", False):
                conditions.append(TRBOrderFormHeader.shipId == TRBShipTo.id)
                conditions.append(TRBShipTo.shipTel.like("%%%s%%" % kw.get("shipTel", "")))
            if kw.get("shipFax", False):
                conditions.append(TRBOrderFormHeader.shipId == TRBShipTo.id)
                conditions.append(TRBShipTo.shipFax.like("%%%s%%" % kw.get("shipFax", "")))

            if len(conditions):
                obj = DBSession.query(TRBOrderFormHeader)

                for condition in conditions: obj = obj.filter(condition)
            
                result = obj.filter(TRBOrderFormHeader.active == 0)
            else:
                result = DBSession.query(TRBOrderFormHeader).filter(TRBOrderFormHeader.active == 0)

            return result
        except:
            traceback.print_exc()