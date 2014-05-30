# -*- coding: utf-8 -*-

# turbogears imports
from tg import expose, redirect, validate, flash, session, request
from tg.decorators import *

# third party imports
from repoze.what import predicates, authorize
from repoze.what.predicates import not_anonymous, in_group, has_permission

# project specific imports
from budget.lib.base import BaseController
from budget.model import *


from budget.util.common import *
from budget.widgets.access import *


class AccessController(BaseController):
    #Uncomment this line if your controller requires an authenticated user
    allow_only = authorize.in_group('Admin')


    @expose('budget.templates.access.index')
    @tabFocus(tab_type = "access")
    def index(self):
        return dict(page = 'index')

    @expose('budget.templates.access.user')
    @paginate("result", items_per_page = 20)
    @tabFocus(tab_type = "access")
    def user(self, **kw):
        if not kw:
            result = []
        else:
            result = DBSession.query(User).filter(User.__table__.c.user_name.op("ilike")("%%%s%%" % kw["user_name"])).order_by(User.user_name).all()
        return {"widget" : user_search_form, "result" : result, "values" : kw}



    @expose('budget.templates.access.group')
    @paginate("result", items_per_page = 20)
    @tabFocus(tab_type = "access")
    def group(self, **kw):
        if not kw:
            result = []
        else:
            result = DBSession.query(Group).filter(Group.__table__.c.group_name.op("ilike")("%%%s%%" % kw["group_name"])).order_by(Group.group_name).all()
        return {"widget" : group_search_form, "result" : result, "values" : kw}


    @expose('budget.templates.access.permission')
    @paginate("result", items_per_page = 20)
    @tabFocus(tab_type = "access")
    def permission(self, **kw):
        if not kw:
            result = []
        else:
            result = DBSession.query(Permission).filter(Permission.__table__.c.permission_name.op("ilike")("%%%s%%" % kw["permission_name"])).order_by(Permission.permission_name).all()
        return {"widget" : permission_search_form, "result" : result, "values" : kw}




    @expose('budget.templates.access.add')
    @tabFocus(tab_type = "access")
    def add(self, **kw):
        if not kw.get("type", None) :
            flash("No such operation!")
            redirect("/access/index")
        return {"type" : kw["type"]}


    @expose()
    def save_new(self, **kw):
        if kw["type"] == "user" :
            password = kw["password"] if kw["password"] else "123321"
            u = User(user_name = kw["user_name"], display_name = kw["display_name"], email_address = kw["email_address"], password = password)
            DBSession.add(u)
            DBSession.flush()
            redirect("/access/user_manage?id=%d" % u.user_id)
        elif kw["type"] == "group" :
            g = Group(group_name = kw["group_name"])
            DBSession.add(g)
            DBSession.flush()
            redirect("/access/group_manage?id=%d" % g.group_id)
        elif kw["type"] == "permission" :
            p = Permission(permission_name = kw["permission_name"], description = kw["description"])
            ag = DBSession.query(Group).filter_by(group_name = "Admin").one()
            ag.permissions.append(p)
            DBSession.add(p)
            DBSession.flush()
            redirect("/access/permission_manage?id=%d" % p.permission_id)
        elif kw["type"] == "sample_profile" :
            s = SampleGroupProfile(name = kw["name"], description = kw["description"])
            DBSession.add(s)
            DBSession.flush()
            redirect("/access/sample_profile_manage?id=%d" % s.id)
        elif kw["type"] == "dba_profile" :
            s = DBAProfile(name = kw["name"], description = kw["description"])
            DBSession.add(s)
            DBSession.flush()
            redirect("/access/dba_profile_manage?id=%d" % s.id)
        else:
            flash("No such type operation!")
            redirect("/access/index")


    @expose("budget.templates.access.user_manage")
    @tabFocus(tab_type = "access")
    def user_manage(self, **kw):
        u = getOr404(User, kw["id"])
        included = u.groups
        excluded = DBSession.query(Group).filter(~Group.users.any(User.user_id == u.user_id)).order_by(Group.group_name)
        return {
                "widget" : user_update_form,
                "values" : {"id" : u.user_id, "user_name" : u.user_name, "email_address" : u.email_address, "display_name" : u.display_name},
                "included" : included,
                "excluded" : excluded,
                }

    @expose()
    def save_user(self, **kw):
        u = getOr404(User, kw["id"])
        if kw.get("user_name", None) : u.user_name = kw["user_name"]
        if kw.get("password", None) : u.password = kw["password"]
        if kw.get("display_name", None) : u.display_name = kw["display_name"]
        if kw.get("email_address", None) : u.email_address = kw["email_address"]

        if not kw["igs"] : u.groups = []
        else : u.groups = DBSession.query(Group).filter(Group.group_id.in_(kw["igs"].split("|"))).all()
        flash("Save the update successfully!")
        redirect("/access/user")



    @expose("budget.templates.access.permission_manage")
    @tabFocus(tab_type = "access")
    def permission_manage(self, **kw):
        p = getOr404(Permission, kw["id"])

        included = p.groups
        excluded = DBSession.query(Group).filter(~Group.permissions.any(Permission.permission_id == p.permission_id)).order_by(Group.group_name)

        return {"widget" : permission_update_form,
                "values" : {"id" : p.permission_id, "permission_name" : p.permission_name},
                "included" : included,
                "excluded" : excluded
                }

    @expose()
    def save_permission(self, **kw):
        p = getOr404(Permission, kw["id"])
        p.permission_name = kw["permission_name"]
        if not kw["igs"] : p.groups = []
        else : p.groups = DBSession.query(Group).filter(Group.group_id.in_(kw["igs"].split("|"))).all()
        flash("Save the update successfully!")
        redirect("/access/permission")



    @expose('budget.templates.access.group_manage')
    @tabFocus(tab_type = "access")
    def group_manage(self, **kw):
        g = getOr404(Group, kw["id"])
        included = g.users
        excluded = DBSession.query(User).filter(~User.groups.any(Group.group_id == g.group_id)).order_by(User.user_name)

        got = g.permissions

        #myLog(got)

        lost = DBSession.query(Permission).filter(~Permission.groups.any(Group.group_id == g.group_id)).order_by(Permission.permission_name)
        return {"widget" : group_update_form , "values" : { "id" : g.group_id, "group_name" : g.group_name },
                "included" : included , "excluded" : excluded,
                "got" : got, "lost" : lost }


    @expose()
    def save_group(self, **kw):
        g = getOr404(Group, kw["id"])

        g.group_name = kw["group_name"]

        uigs = kw["uigs"]
        pigs = kw["pigs"]

        if not uigs : g.users = []
        else : g.users = DBSession.query(User).filter(User.user_id.in_(uigs.split("|"))).all()

        if not pigs : g.permissions = []
        else : g.permissions = DBSession.query(Permission).filter(Permission.permission_id.in_(pigs.split("|"))).all()

        flash("Save the update successfully!")
        redirect("/access/group")



    @expose('budget.templates.access.sample_profile')
    @paginate("result", items_per_page = 20)
    @tabFocus(tab_type = "access")
    def sample_profile(self, **kw):
        if not kw:
            result = []
        else:
            result = DBSession.query(SampleGroupProfile).filter(SampleGroupProfile.__table__.c.name.op("ilike")("%%%s%%" % kw["name"])).order_by(SampleGroupProfile.name).all()
        return {"widget" : sample_profile_search_form, "result" : result, "values" : kw}



    @expose('budget.templates.access.sample_profile_manage')
    @paginate("result", items_per_page = 20)
    @tabFocus(tab_type = "access")
    def sample_profile_manage(self, **kw):
        s = getOr404(SampleGroupProfile, kw["id"])
        return {
                "widget" : sample_profile_update_form ,
                "values" : { "id" : s.id, "name" : s.name , "description" : s.description,
                            "team_id" : s.team_id , "region_id" : s.region_id, "group_id" : s.group_id,
                            "manager_group_id" : s.manager_group_id
                            }
                }


    @expose()
    def save_sample_profile(self, **kw):
        s = getOr404(SampleGroupProfile, kw["id"])
        s.name = kw.get("name", None)
        s.description = kw.get("description", None)
        s.group_id = kw.get("group_id", None) or None
        s.team_id = kw.get("team_id", None) or None
        s.region_id = kw.get("region_id", None) or None
        s.manager_group_id = kw.get("manager_group_id", None) or None
        
        flash("Save the update successfully!")
        redirect("/access/sample_profile")



    @expose('budget.templates.access.dba_profile')
    @paginate("result", items_per_page = 20)
    @tabFocus(tab_type = "access")
    def dba_profile(self, **kw):
        if not kw:
            result = []
        else:
            result = DBSession.query(DBAProfile).filter(DBAProfile.__table__.c.name.op("ilike")("%%%s%%" % kw["name"])).order_by(DBAProfile.name).all()
        return {"widget" : dba_profile_search_form, "result" : result, "values" : kw}



    @expose('budget.templates.access.dba_profile_manage')
    @paginate("result", items_per_page = 20)
    @tabFocus(tab_type = "access")
    def dba_profile_manage(self, **kw):
        s = getOr404(DBAProfile, kw["id"])
        return {
                "widget" : dba_profile_update_form ,
                "values" : { "id" : s.id, "name" : s.name , "description" : s.description,
                            "group_id" : s.group_id, "customer_id" : s.customer_id}
                }


    @expose()
    def save_dba_profile(self, **kw):
        s = getOr404(DBAProfile, kw["id"])
        s.name = kw.get("name", None)
        s.description = kw.get("description") or None
        s.group_id = kw.get("group_id", None) or None
        s.customer_id = kw.get("customer_id") or None

        flash("Save the update successfully!")
        redirect("/access/dba_profile")
