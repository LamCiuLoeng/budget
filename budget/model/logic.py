'''
Created on 2013-2-6

@author: CL.Lam
'''
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, Float, Text, Numeric
from sqlalchemy.sql.expression import and_, or_
from sqlalchemy.orm import relation, backref


from budget.model import DeclarativeBase, DBSession
from budget.model.auth import SysMixin, Group


__all__ = [
           'STATUS_NEW', 'STATUS_SAVED', 'STATUS_CONFIRMED', 'STATUS_POSTED',
           'Currency', 'ExchangeRate', 'Company', 'LogicTeam', 'BusinessTeam',
           'FeeExpression', 'FeeGroup', 'FeeItem', 'FeeContent']


STATUS_NEW = 0
STATUS_SAVED = 10
STATUS_CONFIRMED = 20
STATUS_POSTED = 30



class DateMixin( object ):
    year = Column( Text )
    month = Column( Text )


class EffectMixin( object ):
    effect_from = Column( Text, default = None )
    effect_to = Column( Text, default = None )

    @classmethod
    def get_effect( clz, effect_date ):
        return DBSession.query( clz ).filter( and_( clz.active == 0,
                                              clz.effect_from <= effect_date,
                                              or_( clz.effect_to is None, clz.effect_to >= effect_date ),
                                              ) )


class Currency( DeclarativeBase, SysMixin ):
    __tablename__ = 'master_currency'

    id = Column( Integer, autoincrement = True, primary_key = True )
    name = Column( Text )
    label = Column( Text )
    default_rate = Column( Numeric( 15, 2 ), default = None )

    def __str__( self ):      return self.label
    def __unicode__( self ):      return self.label


class ExchangeRate( DeclarativeBase, SysMixin, DateMixin ):
    __tablename__ = 'master_exchange_rate'

    id = Column( Integer, autoincrement = True, primary_key = True )
    currency_id = Column( Integer, ForeignKey( 'master_currency.id' ) )
    currency = relation( Currency )
    value = Column( Numeric( 15, 2 ), default = None )

    @classmethod
    def get_one( cls, currency_id, year, month ):
        return DBSession.query( cls ).filter( and_( cls.currency_id == currency_id,
            cls.year == year, cls.month == month, cls.active == 0 ) ).order_by( cls.id ).first()



class Company( DeclarativeBase, SysMixin ):
    __tablename__ = 'master_company'

    id = Column( Integer, autoincrement = True, primary_key = True )
    name = Column( Text )
    label = Column( Text )

    currency_id = Column( Integer, ForeignKey( 'master_currency.id' ) )
    currency = relation( Currency )

    def __str__( self ):      return self.label
    def __unicode__( self ):      return self.label

    def get_exrate( self, year, month ):
        result = ExchangeRate.get_one( self.currency_id, year, month )
        return result.value if result else ''

    @classmethod
    def get_by_id( cls, id ):
        return DBSession.query( cls ).filter( and_( cls.id == id, cls.active == 0 ) ).order_by( cls.label ).first()



class Subline( DeclarativeBase, SysMixin ):
    __tablename__ = 'master_subline'

    id = Column( Integer, autoincrement = True, primary_key = True )
    name = Column( Text, default = None )
    label = Column( Text, default = None )

    def __str__( self ):      return self.label
    def __unicode__( self ):      return self.label


class SaleType( DeclarativeBase, SysMixin ):
    __tablename__ = 'master_sale_type'

    id = Column( Integer, autoincrement = True, primary_key = True )
    name = Column( Text, default = None )
    label = Column( Text, default = None )

    def __str__( self ):      return self.label
    def __unicode__( self ):      return self.label


class LogicTeam( DeclarativeBase, SysMixin, EffectMixin ):
    __tablename__ = 'master_logic_team'

    id = Column( Integer, autoincrement = True, primary_key = True )
    name = Column( Text )
    label = Column( Text )
    order = Column( Float, default = 0 )

    member_id = Column( Integer, ForeignKey( 'tg_group.group_id' ) )
    member = relation( Group, primaryjoin = member_id == Group.group_id )

    manager_id = Column( Integer, ForeignKey( 'tg_group.group_id' ) )
    manager = relation( Group, backref = "logicteams", primaryjoin = manager_id == Group.group_id )

    import_excel_column = Column( Text, default = None )

    for_sale = Column( Integer, default = 0 )    # 0 is for sale/cost module ,1 is not

    def __str__( self ):      return self.label
    def __unicode__( self ):      return self.label

    @classmethod
    def get_all( cls ):
        return DBSession.query( cls ).filter( cls.active == 0 ).order_by( cls.order ).all()

    @classmethod
    def get_by_id( cls, id ):
        return DBSession.query( cls ).filter( and_( cls.id == id, cls.active == 0 ) ).order_by( cls.order ).first()



class BusinessTeam( DeclarativeBase, SysMixin, DateMixin ):
    __tablename__ = 'master_business_team'

    id = Column( Integer, autoincrement = True, primary_key = True )

    logicteam_id = Column( Integer, ForeignKey( 'master_logic_team.id' ) )
    logicteam = relation( LogicTeam )

    company_id = Column( Integer, ForeignKey( 'master_company.id' ) )
    company = relation( Company )

    _members = Column( 'members', Text )

    def get_members( self ):
        return filter( lambda v:v, ( self._members or "" ).split( "|" ) )

    def set_members( self, content ):
        if not content :
            self._members = None
        elif type( content ) == list:
            self._members = "|".join( content )
        elif isinstance( content, basestring ):
            self._members = content
        else:
            raise Exception( 'No the proper value!' )

    members = property( fget = get_members, fset = set_members )





class FeeExpression( DeclarativeBase, SysMixin ):
    __tablename__ = 'master_fee_expression'

    id = Column( Integer, autoincrement = True, primary_key = True )
    exp = Column( Text )
#    args = Column(Text)



class FeeGroup( DeclarativeBase, SysMixin, EffectMixin ):
    __tablename__ = 'master_fee_group'

    id = Column( Integer, autoincrement = True, primary_key = True )
    name = Column( Text )
    label = Column( Text )
    order = Column( Float, default = 0 )

    def __str__( self ):      return self.label or self.name
    def __unicode__( self ):      return self.label or self.name


    @classmethod
    def get_groups( clz, effect_date ):
        return clz.get_effect().order_by( clz.order ).all()

    def get_items( self, effect_date ):
        return FeeItem.get_effect( self.id, effect_date ).filter( FeeItem.feegroup_id == self.id ).order_by( FeeItem.order ).all()




class FeeItem( DeclarativeBase, SysMixin, EffectMixin ):
    __tablename__ = 'master_fee_item'

    id = Column( Integer, autoincrement = True, primary_key = True )
    name = Column( Text, default = None )
    label = Column( Text, default = None )

    feegroup_id = Column( Integer, ForeignKey( 'master_fee_group.id' ) )
    feegroup = relation( FeeGroup, backref = backref( "items", order_by = 'FeeItem.order' ) )

    is_share = Column( Integer, default = 0 )    # 0 is not for share by the total fee, 1 is shared from the FIN input.
    order = Column( Float, default = 0 )
    type = Column( Integer, default = 0 )    # 0 is for the user to input ,1 is for the expression cal.
    expression_id = Column( Integer, ForeignKey( 'master_fee_expression.id' ) )
    expression = relation( FeeExpression )
    args = Column( Text )

    import_excel_row = Column( Text, default = None )

    def __str__( self ):      return self.label
    def __unicode__( self ):      return self.label






class FeeContent( DeclarativeBase, SysMixin, DateMixin ):
    __tablename__ = 'fee_content'

    id = Column( Integer, autoincrement = True, primary_key = True )

    company_id = Column( Integer, ForeignKey( 'master_company.id' ) )
    company = relation( Company )

    logicteam_id = Column( Integer, ForeignKey( 'master_logic_team.id' ) )
    logicteam = relation( LogicTeam )

    feeitem_id = Column( Integer, ForeignKey( 'master_fee_item.id' ) )
    feeitem = relation( FeeItem )

    actual_value = Column( Integer, default = None )
    actual_status = Column( Integer, default = 0 )
    budget_value = Column( Integer, default = None )
    budget_status = Column( Integer, default = 0 )
    forecast_value = Column( Integer, default = None )
    forecast_status = Column( Integer, default = 0 )

    status = Column( Integer, default = 0 )









class ERPFeeContent( DeclarativeBase, SysMixin, DateMixin ):
    __tablename__ = 'erp_fee_content'

    id = Column( Integer, autoincrement = True, primary_key = True )

    company_id = Column( Integer, ForeignKey( 'master_company.id' ) )
    company = relation( Company )

    logicteam_id = Column( Integer, ForeignKey( 'master_logic_team.id' ) )
    logicteam = relation( LogicTeam )

    customer = Column( Text, default = None )
    brand = Column( Text, default = None )


    subline_id = Column( Integer, ForeignKey( 'master_subline.id' ) )
    subline = relation( Subline )

    saletype_id = Column( Integer, ForeignKey( 'master_sale_type.id' ) )
    saletype = relation( SaleType )

    actual_sale_value = Column( Integer, default = None )
    actual_cost_value = Column( Integer, default = None )
#    actual_status = Column(Integer, default = 0)

    budget_sale_value = Column( Integer, default = None )
    budget_cost_value = Column( Integer, default = None )
#    budget_status = Column(Integer, default = 0)

    forecast_sale_value = Column( Integer, default = None )
    forecast_cost_value = Column( Integer, default = None )
#    forecast_status = Column(Integer, default = 0)

    status = Column( Integer, default = 0 )
