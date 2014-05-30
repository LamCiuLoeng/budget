# -*- coding: utf-8 -*-
from datetime import datetime as dt
import traceback

from tg import redirect, validate, flash, expose, request, override_template
from repoze.what import predicates, authorize
from repoze.what.predicates import not_anonymous, in_group, has_permission
from tg.decorators import paginate

from budget.lib.base import BaseController
from budget.model import DBSession, metadata
from budget.util.common import *
import budget

__all__ = ["BasicMasterController"]

class BasicMasterController(BaseController):
    #Uncomment this line if your controller requires an authenticated user
    #allow_only = authorize.not_anonymous()

    url = "__MUST__BE__CHANGE__"

    dbObj = None

    searchWidget = None

    updateWidget = None

    formFields = []

    template = None

    search_config = None

    @expose('budget.templates.master.index')
    @paginate("result", items_per_page = 20)
    @tabFocus(tab_type = "master")
    def index(self, **kw):
        if self.template:     override_template(self.index, "mako:" + self.template)
        if not kw:
            result = []
        else:
            result = self.searchMaster(kw)
        return {
                "searchWidget" : self.searchWidget,
                "result" : result,
                "funcURL" :self.url,
                "values" : kw,
                }

    @expose('budget.templates.master.form')
    @tabFocus(tab_type = "master")
    def add(self, **kw):
        return {
                "widget" : self.updateWidget,
                "values" : {},
                "saveURL" : "/%s/saveNew" % self.url,
                "funcURL" :self.url
                }

    @expose()
    def saveNew(self, **kw):
        # params = {"issuedBy":request.identity["user"], "lastModifyBy":request.identity["user"], "lastModifyTime":dt.now()}
        params = {}
        for f in self.formFields:
            if f in kw : params[f] = kw[f] if kw[f] else None
        params = self.beforeSaveNew(kw, params)
        obj = self.dbObj(**params)
        obj = self.afterSaveNew(obj,kw)
        DBSession.add(obj)
        flash("Save the new master successfully!")
        redirect("/%s/index" % self.url)

    @expose('budget.templates.master.form')
    @tabFocus(tab_type = "master")
    def update(self, **kw):
        obj = getOr404(self.dbObj, kw["id"], "/%s/index" % self.url)
        values = {}
        #for f in self.formFields : values[f]=getattr(obj, f)
        for f in self.formFields : 
            v = getattr(obj, f)
            if isinstance(v, basestring):values[f] = str(getattr(obj, f))
            else: values[f] = v
        return {
                "widget" : self.updateWidget,
                "values" : values,
                "saveURL" : "/%s/saveUpdate?id=%d" % (self.url, obj.id),
                "funcURL" :self.url
                }

    @expose()
    def saveUpdate(self, **kw):
        obj = getOr404(self.dbObj, kw["id"], "/%s/index" % self.url)
        params = {"lastModifyBy":request.identity["user"], "lastModifyTime":dt.now()}
        for f in self.formFields:
            if f in kw : params[f] = kw[f] if kw[f] else None
        params = self.beforeSaveUpdate(kw, params)
        for k in params : setattr(obj, k, params[k])
        obj = self.afterSaveUpdate(obj,kw)
        flash("Update the master successfully!")
        redirect("/%s/index" % self.url)

    @expose()
    def enable(self, **kw):
        if kw.get('selected_ids', ''):
            for i in kw.get('selected_ids', '').split(','):
                obj = getOr404(self.dbObj, i, "/%s/index" % self.url)
                obj.lastModifyBy = request.identity["user"]
                obj.lastModifyTime = dt.now()
                obj.active = 0
        flash("Enable the master successfully!")
        redirect("/%s/index" % self.url)

    @expose()
    def disable(self, **kw):
        if kw.get('selected_ids', ''):
            for i in kw.get('selected_ids', '').split(','):
                obj = getOr404(self.dbObj, i, "/%s/index" % self.url)
                obj.lastModifyBy = request.identity["user"]
                obj.lastModifyTime = dt.now()
                obj.active = 1
        flash("Disable the master successfully!")
        redirect("/%s/index" % self.url)

    @expose()
    def delete(self, **kw):
        obj = getOr404(self.dbObj, kw["id"], "/%s/index" % self.url)
        obj.lastModifyBy = request.identity["user"]
        obj.lastModifyTime = dt.now()
        obj.active = 1
        flash("Delete the master successfully!")
        redirect("/%s/index" % self.url)


    def searchMaster(self, kw):
        try:
            if self.search_config :
                search_config = self.search_config
            else:
                search_config = {"itemCode": ["item_code", str],
                               "brandId": ["brand_id", int],
                               "itemClassId": ["category_id", int],
                               "attrName": ["attr_name", str],
                               "name": ["name", str],
                               "desc": ["desc", str],
                               "content": ["content", str],
                               "langId": ["lang_id", int],
                               "categoryId": ["cat_id", int],
                               "mainPart": ["main_part", str],
                               "extraPart": ["extra_part", str],
                               "code": ["code", str],
                               }

            obj = DBSession.query(self.dbObj)
            for field, value in kw.items():
                if value:
                    if search_config[field][1] == str:
                        obj = obj.filter(getattr(self.dbObj.__table__.c, search_config.get(field, "")[0]).op("ILIKE")("%%%s%%" % value))
                    elif search_config[field][1] == int:
                        obj = obj.filter(getattr(self.dbObj.__table__.c, search_config.get(field, "")[0]) == int(value))
                    else:
                        obj = obj.filter(getattr(self.dbObj.__table__.c, search_config.get(field, "")[0]) == value)
                else:
                    continue

#        q = DBSession.query(self.dbObj).filter(self.dbObj.__table__.c.name.op("ILIKE")("%%%s%%" %kw["name"]))
#        if not in_group("Admin"):
#            obj = obj.filter(self.dbObj.status==0)
            return obj.order_by(self.dbObj.id).all()
        except:
            file = open('log.txt', 'w')
            traceback.print_exc(None, file)
            file.close()

    def beforeSaveNew(self, kw, params):
        return params
    
    def afterSaveNew(self,obj,kw):
        return obj

    def beforeSaveUpdate(self, kw, params):
        return params
    
    def afterSaveUpdate(self,obj,kw):
        return obj
