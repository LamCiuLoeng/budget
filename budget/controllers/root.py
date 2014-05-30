# -*- coding: utf-8 -*-
import logging
import json
import thread
from datetime import datetime as dt
import random, traceback, transaction


from tg import expose, flash, require, url, request, redirect
from repoze.what import predicates
from repoze.what.predicates import not_anonymous, in_group

from budget.lib.base import BaseController
from budget.model import DBSession, metadata
from budget import model
from budget.util.common import *
from budget.controllers import *

from budget.controllers.access import *
from budget.controllers.master import *
from budget.controllers.fee import FeeController
from budget.controllers.budgetreport import *
from budget.controllers.erpfee import ERPFeeController
from budget.controllers.finfile import FinFileController


logger = logging.getLogger( __name__ )

__all__ = ['RootController']



class RootController( BaseController ):

    access = AccessController()

    # management
    fee = FeeController()
    erpfee = ERPFeeController()
    file = FinFileController()

    # master
    currency = CurrencyController()
    company = CompanyController()
    feegroup = FeeGroupController()
    feeitem = FeeItemController()
    logicteam = LogicTeamController()
    exchangerate = ExchangeRateController()

    # report
    budgetreport = BudgetReportController()


    @require( not_anonymous() )
    @expose( 'budget.templates.index' )
    @tabFocus( tab_type = "main" )
    def index( self ):
        return dict( page = 'index' )


    @require( not_anonymous() )
    @expose( 'budget.templates.tracking' )
    @tabFocus( tab_type = "view" )
    def tracking( self ):
        return {}

    @require( not_anonymous() )
    @expose( 'budget.templates.report' )
    @tabFocus( tab_type = "report" )
    def report( self ):
        return {}

    @expose( 'budget.templates.login' )
    def login( self, came_from = url( '/' ) ):
        """Start the user login."""
        if request.identity: redirect( came_from )

        login_counter = request.environ['repoze.who.logins']
        if login_counter > 0:
            flash( 'Wrong credentials', 'warning' )
        return dict( page = 'login', login_counter = str( login_counter ), came_from = came_from )

    @expose()
    def post_login( self, came_from = url( '/' ) ):
        if not request.identity:
            login_counter = request.environ['repoze.who.logins'] + 1
            redirect( url( '/login', came_from = came_from, __logins = login_counter ) )
        userid = request.identity['repoze.who.userid']
#        flash('Welcome back, %s!' % userid)
        redirect( came_from )

    @expose()
    def post_logout( self, came_from = url( '/' ) ):
#        flash('We hope to see you soon!')
        redirect( url( "/" ) )

    @require( not_anonymous() )
    @expose( 'budget.templates.page_master' )
    @tabFocus( tab_type = "master" )
    def master( self ):
        """Handle the front-page."""
        return {}
