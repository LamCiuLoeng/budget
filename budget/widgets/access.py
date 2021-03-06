# -*- coding: utf-8 -*-


from tw.api import WidgetsList
from tw.forms import TableForm
from tw.forms.fields import HiddenField

from budget.model import DBSession
from budget.model import *

from budget.widgets.components import *

#class SearchForm(RPACForm):
#    
#    group_options = DBSession.query(Group.group_id,Group.group_name).order_by(Group.group_name)
#    
#    permission_options = DBSession.query(Permission.permission_id,Permission.permission_name).order_by(Permission.permission_name)
#    
#    fields = [
#        RPACText("user_name",label_text="User Name"),
#        RPACSelect("group_id",label_text="Group Name",options=group_options),
#        RPACSelect("permission_id",label_text="Permission Name",options=permission_options)
#        ]
#        
#access_search_form = SearchForm("search")

group_options=lambda :[(None, '')]+[(g.group_id, g.group_name) for g in DBSession.query(Group.group_id, Group.group_name).order_by(Group.group_name)]
team_options=lambda :[(None, '')]+[(t.id, t.name) for t in DBSession.query(Team.id, Team.name).order_by(Team.name)]
region_options=lambda:[(None, '')]+[(r.id, r.name) for r in DBSession.query(Region.id, Region.name).order_by(Region.name)]
dba_customer_options=lambda:[(None, '')]+[(r.id, r.name) for r in DBSession.query(DBACustomer.id, DBACustomer.name).order_by(DBACustomer.name)]







class UserSearchForm(RPACForm):
    fields=[RPACText("user_name", label_text="User Name"), ]

user_search_form=UserSearchForm()

class GroupSearchForm(RPACForm):
    fields=[RPACText("group_name", label_text="Group Name"), ]

group_search_form=GroupSearchForm()


class PermissionSearchForm(RPACForm):
    fields=[RPACText("permission_name", label_text="Permission Name"), ]

permission_search_form=PermissionSearchForm()




class UserForm(RPACForm):
    fields=[
              HiddenField("id"),
              RPACText("user_name", label_text="User Name"),
              RPACText("password", label_text="Password"),
              RPACText("email_address", label_text="E-mail Address"),
              RPACText("display_name", label_text="Display Name"),
              ]

user_update_form=UserForm()


class GroupForm(RPACForm):
    fields=[
        HiddenField("id"),
        RPACText("group_name", label_text="Group Name"),
        ]

group_update_form=GroupForm()


class PermissionForm(RPACForm):
    fields=[
        HiddenField("id"),
        RPACText("permission_name", label_text="Permission Name"),
        ]

permission_update_form=PermissionForm()
