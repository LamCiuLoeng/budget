# -*- coding: utf-8 -*-
import logging
import json
from datetime import datetime as dt
import random, traceback, transaction
import os


from sqlalchemy.sql.expression import and_, desc, or_
from tg import expose, redirect, request, flash, config
from tg.decorators import paginate
# from tg.controllers.decoratedcontroller import not_anonymous
from tg.decorators import require
from repoze.what.predicates import has_permission, not_anonymous

from budget.lib.base import BaseController
from budget.util.common import tabFocus, sysUpload, advancedSendMail, serveFile
from budget.model import DBSession, FinFileObject, LogicTeam, User, UploadObject
from budget.util.file_util import  create_zip
from budget.util.fin_helper import getUserTeams






logger = logging.getLogger( __name__ )

__all__ = ['FinFileController']



class FinFileController( BaseController ):

    @require( not_anonymous() )
    @expose()
    def index( self ):
        if has_permission( 'FIN_VIEW_ALL' ):    # if FIN team
            return redirect( 'fin_index' )
        else:
            return redirect( 'none_fin_index' )


    @expose( 'budget.templates.finfile.fin_index' )
    @paginate( "result", items_per_page = 20 )
    @tabFocus( tab_type = "main" )
    def fin_index( self, **kw ):

        cds = [FinFileObject.active == 0,
               FinFileObject.logicteam_id == LogicTeam.id,
               FinFileObject.create_by_id == User.user_id]

        values = {
                  'team_id' : kw.get( 'team_id', '' ),
                  'create_time_from' : kw.get( 'create_time_from', '' ),
                  'create_time_to' : kw.get( 'create_time_to', '' )
                 }

        if values["create_time_from"] : cds.append( FinFileObject.create_time >= '%s 00:00:00' % kw["create_time_from"] )
        if values["create_time_to"] : cds.append( FinFileObject.create_time <= '%s 23:59:59' % kw["create_time_to"] )
        if values['team_id'] : cds.append( FinFileObject.logicteam_id == kw["team_id"] )

        result = DBSession.query( FinFileObject, LogicTeam, User ).filter( and_( *cds ) ).order_by( desc( FinFileObject.create_time ) )

        teams = DBSession.query( LogicTeam ).filter( and_( LogicTeam.active == 0 ) ).order_by( LogicTeam.name ).all()
        return {'result' : result, 'teams' : teams, 'values' : values}


    @expose()
    def download( self, **kw ):
        fids = kw.get( 'fids', None )
        if not fids:
            flash( "Not all parameters are provided!" )
            return redirect( 'index' )

        if type( fids ) != list : fids = [fids, ]

        fs = DBSession.query( UploadObject ).filter( or_( *[UploadObject.id == fid for fid in fids] ) )

        if fs.count() == 1 :
            obj = fs.one()
            return serveFile( obj.file_path, obj.file_name )
        else:    # zip the file
            zip_folder = os.path.join( config.download_dir, 'budget' )
            if not os.path.exists( zip_folder ): os.makedirs( zip_folder )
            zip_path = os.path.join( zip_folder, '%s_%s.zip' % ( unicode( request.identity["user"] ), dt.now().strftime( "%Y%m%d%H%M%S" ) ) )
            create_zip( zip_path, [ ( f.file_path, f.file_name ) for f in fs] )
            return serveFile( zip_path )




    @expose( 'budget.templates.finfile.none_fin_index' )
    @paginate( "result", items_per_page = 20 )
    @tabFocus( tab_type = "main" )
    def none_fin_index( self ):
        cds = [FinFileObject.active == 0,
               FinFileObject.logicteam_id == LogicTeam.id,
               FinFileObject.create_by_id == User.user_id,
               FinFileObject.create_by_id == request.identity["user"].user_id]

        result = DBSession.query( FinFileObject, LogicTeam, User ).filter( and_( *cds ) ).order_by( desc( FinFileObject.create_time ) )

        teams = getUserTeams()
        return {'result' : result, 'teams' : teams}



    @expose()
    def upload( self, **kw ):
        tid = kw.get( 'team_id', None )
        if not tid :
            flash( "Not all parameters are provided!" )
            return redirect( 'none_fin_index' )

        try:
            raw = sorted( filter( lambda ( k, v ): k.startswith( 'file' ), kw.iteritems() ), cmp = lambda x, y:cmp( x[0], y[0] ) )
            r = [v for k, v in raw]
            ( flag, fs ) = sysUpload( attachment_list = r, folder = 'budget', return_obj = True )
            succ = 0
            fileNames = []
            for f in fs:
                if not f : continue
                DBSession.add( FinFileObject( logicteam_id = tid, uploadObject = f ) )
                succ += 1
                fileNames.append( f.file_name )
            DBSession.flush()

            if succ > 0:
                send_from = 'r-track@r-pac.com.hk'
                sendto = config.get( "upload_email_to" ).split( ";" )
                cc_to = cc_to = config.get( "upload_email_cc" ).split( ";" )
                subject = "New File(s) Uploaded"
                content = [
                         'Dear user:',
                         '%s have uploaded file(s) to the Finance Budget System, listed below:' % unicode( request.identity["user"] ) ,
                         '',
                         ]
                content.extend( fileNames )
                content.extend( [
                                 '',
                                 '************************************************************************************',
                                 'This e-mail is sent by the r-pac Finance Budget System automatically.',
                                 'Please do not reply this e-mail directly!',
                                 '************************************************************************************',
                                ] )

                advancedSendMail( send_from, sendto, subject, '\n'.join( content ), None, cc_to )
        except:
            traceback.print_exc()
            flash( "Error when uploading the file(s),please try again or report to the system administrator." )
        else:
            flash( "Save the file(s) successfully!" )
        return redirect( 'none_fin_index' )
