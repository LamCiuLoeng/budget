# -*- coding: utf-8 -*-
import os
from sqlalchemy import *
from sqlalchemy.orm import mapper, relation, synonym
from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Integer, Unicode
# from sqlalchemy.orm import relation, backref
from tg import config

from budget.model import DeclarativeBase
from auth import SysMixin




class UploadObject( DeclarativeBase, SysMixin ):
    __tablename__ = 'sysutil_upload'

    id = Column( Integer, autoincrement = True, primary_key = True )
    file_name = Column( Text )
    _file_path = Column( "file_path", Text, nullable = False )



    def _get_file_path( self ):
        return os.path.join( config.get( "download_dir" ), self._file_path )

    def _set_file_path( self, value ):
        self._file_path = value

    file_path = synonym( '_file_path', descriptor = property( _get_file_path, _set_file_path ) )
