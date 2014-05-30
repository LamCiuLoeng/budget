# -*- coding: utf-8 -*-
from tg import request
from sqlalchemy.sql.expression import and_

from budget.model import DBSession
from budget.model import FeeContent, FeeItem, LogicTeam, Permission
from budget.util.oracle_helper import searchOracle



__all__ = ['round2int', 'ERPInfo']


round2int = lambda v : int( round( v ) )




class ERPInfo( object ):
    _customer_list = None
    _brand_mapping = {}

    @classmethod
    def get_customer( clz ):
        if clz._customer_list is None:
            sql = "SELECT tp.PROGRAM_CODE FROM t_program tp ORDER BY tp.PROGRAM_CODE"
            customer_list = searchOracle( sql, {} )
            clz._customer_list = [c[0] for c in  customer_list]
        return clz._customer_list

    @classmethod
    def search_customer( clz, val ):
        if not val : return []
        return filter( lambda v : v.find( val.upper() ) > -1, clz.get_customer() )

    @classmethod
    def get_brand( clz, customer ):
        customer = customer.upper()
        if customer in clz._brand_mapping : return clz._brand_mapping[customer]
        customer_list = clz.get_customer()
        if customer not in customer_list : return []
        sql = "SELECT tb.BRAND_CODE FROM t_program tp, t_brand tb WHERE tp.PROGRAM_CODE=tb.PROGRAM_CODE AND tp.PROGRAM_CODE = '%s'" % customer
        brand_list = searchOracle( sql, {} )
        clz._brand_mapping[customer] = [b[0] for b in brand_list]
        return clz._brand_mapping[customer]


    @classmethod
    def search_brand( clz, customer, val ):
        if not val : return []
        return filter( lambda v : v.find( val.upper() ) > -1, clz.get_brand( customer ) )




def getUserTeams():
    teams = []
    mp = DBSession.query( Permission ).filter( Permission.permission_name == 'MANAGER_VIEW' ).one()
    for g in request.identity["user"].groups:
        if mp in g.permissions and g.logicteams:
            teams.extend( g.logicteams )
    return teams
