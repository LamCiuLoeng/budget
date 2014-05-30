# -*- coding: utf-8 -*-
'''
Created on 2013-9-30
@author: CL.lam
'''
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer
from sqlalchemy.orm import relation

from budget.model import DeclarativeBase, SysMixin, LogicTeam, UploadObject

__all__ = ['FinFileObject', ]


class FinFileObject( DeclarativeBase, SysMixin ):
    __tablename__ = 'fileutil_fin_file'

    id = Column( Integer, autoincrement = True, primary_key = True )

    logicteam_id = Column( Integer, ForeignKey( 'master_logic_team.id' ) )
    logicteam = relation( LogicTeam )

    uploadObject_id = Column( Integer, ForeignKey( 'sysutil_upload.id' ) )
    uploadObject = relation( UploadObject )
