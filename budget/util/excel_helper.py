# -*- coding: utf-8 -*-
import os, traceback, logging, datetime
from itertools import chain
import win32com.client
import pythoncom

from win32com.client import DispatchEx
from sqlalchemy.sql.expression import and_

from common import *
from budget.model import DBSession
from budget.model.logic import FeeItem, LogicTeam

__all__ = ["ExcelBasicGenerator", 'FinBudgetExcel', 'parseExcel', 'FinSaleExcel']


XlBorderWeight = {
                  "xlHairline" : 1,
                  "xlThin" : 2,
                  "xlMedium" : 3,
                  "xlThick" : 4
                  }

XlBordersIndex = {
                  "xlDiagonalDown" : 5,
                  "xlDiagonalUp" : 6,
                  "xlEdgeBottom" : 9,
                  "xlEdgeLeft" : 7,
                  "xlEdgeRight" : 10,
                  "xlEdgeTop" : 8,
                  "xlInsideHorizontal" : 12,
                  "xlInsideVertical" : 11,
                  }



# http://msdn.microsoft.com/en-us/library/microsoft.office.interop.excel.xlhalign.aspx
XlHAlign = {
          "xlHAlignCenter" :-4108,  # Center
          "xlHAlignCenterAcrossSelection" : 7,  # Center across selection.
          "xlHAlignDistributed" :-4117,  # Distribute
          "xlHAlignFill" : 5,  # Fill
          "xlHAlignGeneral" : 1,  # Align according to data type.
          "xlHAlignJustify" :-4130,  # Justify
          "xlHAlignLeft" :-4130,  # Left
          "xlHAlignRight" :-4152,  # Right
          }


HorizontalAlignment = {
                       "xlCenter" :-4108,
                       "xlDistributed" :-4117,
                       "xlJustify" :-4130,
                       "xlLeft" :-4131,
                       "xlRight" :-4152,
                       }


XlUnderlineStyle = {
    "xlUnderlineStyleNone" :-4142,
    "xlUnderlineStyleSingle" : 2,
    "xlUnderlineStyleDouble" :-4119,
    "xlUnderlineStyleSingleAccounting" :4,
    "xlUnderlineStyleDoubleAccounting" : 5,
}


InteriorPattern = {
                   "xlSolid" : 1,
                   }


InteriorPatternColorIndex = {
                             "xlAutomatic" :-4105,
                             }

XlThemeColor = {
                "xlThemeColorAccent1" :    5,  # Accent1
                "xlThemeColorAccent2" :    6,  # Accent2
                "xlThemeColorAccent3" :    7,  # Accent3
                "xlThemeColorAccent4" :   8,  # Accent4
                "xlThemeColorAccent5" :   9,  # Accent5
                "xlThemeColorAccent6" :   10,  # Accent6
                "xlThemeColorDark1"   : 1,  # Dark1
                "xlThemeColorDark2"   : 3,  # Dark2
                "xlThemeColorFollowedHyperlink"  :  12,  # Followed hyperlink
                "xlThemeColorHyperlink" :    11,  # Hyperlink
                "xlThemeColorLight1"  :    2,  # Light1
                "xlThemeColorLight2"  : 4,  # Light2
                }

class ExcelBasicGenerator(object):
    def __init__(self, templatePath = None, destinationPath = None, overwritten = True):
        # solve the problem when create the excel at second time ,the exception is occur.
        pythoncom.CoInitialize()

        self.excelObj = DispatchEx('Excel.Application')
        self.excelObj.Visible = False
        self.excelObj.DisplayAlerts = False

        if templatePath and os.path.exists(templatePath):
            self.workBook = self.excelObj.Workbooks.open(templatePath)
        else:
            self.workBook = self.excelObj.Workbooks.Add()

        self.destinationPath = os.path.normpath(destinationPath) if destinationPath else None
        self.overwritten = overwritten

    def inputData(self): pass

    def outputData(self):
        try:
            if not self.destinationPath : pass
            elif os.path.exists(self.destinationPath):
                if self.overwritten:
                    os.remove(self.destinationPath)
                    self.excelObj.ActiveWorkbook.SaveAs(self.destinationPath)
            else:
                self.excelObj.ActiveWorkbook.SaveAs(self.destinationPath)
        except:
            traceback.print_exc()
        finally:
            try:
                self.workBook.Close(SaveChanges = 0)
            except:
                traceback.print_exc()

    def clearData(self):
        try:
            if hasattr(self, "workBook"): self.workBook.Close(SaveChanges = 0)
        except:
            traceback.print_exc()


class FinBudgetExcel(ExcelBasicGenerator):

    def __init__(self, templatePath = None, destinationPath = None, overwritten = True):
        # set formulas
        self.formulas = [
            '={0}12+{0}13',
            '={0}8-{0}9-{0}10+{0}11-{0}14',
            '=IF(OR({0}15=0,{0}8=0)=TRUE,0%,{0}15/{0}8)',
            '={0}19-{0}20-{0}21',
            '=IF(OR({0}22=0,{0}19=0)=TRUE,0%,{0}22/{0}19)',
            '=IF(OR({0}15+{0}22=0,{0}8+{0}19=0)=TRUE,0%,({0}15+{0}22)/({0}8+{0}19))',
            '={0}27-{0}28-{0}29',
            '=IF(OR({0}30=0,{0}27=0)=TRUE,0%,{0}30/{0}27)',
            '={0}8+{0}19+{0}27',
            '={0}9+{0}20+{0}28',
            '={0}10+{0}21+{0}29',
            '={0}11',
            '={0}14',
            '={0}34-{0}35-{0}36+{0}37-{0}38',
            '=IF(OR({0}$34+{0}$37=0,{0}39=0)=TRUE,0%,{0}39/({0}$34+{0}$37))',
            '={0}43+{0}44',
            '=IF(OR({0}$34+{0}$37=0,{0}45=0)=TRUE,0%,{0}45/({0}$34+{0}$37))',
            '={0}39-{0}45',
            '=IF(OR({0}$34+{0}$37=0,{0}49=0)=TRUE,0%,{0}49/({0}$34+{0}$37))',
            '=IF(OR({0}$34+{0}$37=0,{0}53=0)=TRUE,0%,{0}53/({0}$34+{0}$37))',
            '=+{0}53+{0}49',
            '=IF(OR({0}$34+{0}$37=0,{0}57=0)=TRUE,0%,{0}57/({0}$34+{0}$37))',
            '=SUM({0}81:{0}86)',
            '=SUM({0}88:{0}95)',
            '=SUM({0}61:{0}80,{0}87,{0}96,{0}97)',
            '=SUM({0}110:{0}115)',
            '=SUM({0}117:{0}124)',
            '=SUM({0}101:{0}109,{0}116,{0}125,{0}126)',
            '=SUM({0}158:{0}164)',
            '=SUM({0}166:{0}173)',
            '=SUM({0}130:{0}157,{0}165,{0}174,{0}175)',
            '=SUM({0}179:{0}183)',
            '={0}98+{0}127+{0}176+{0}184',
            '={0}57-{0}187',
            '=IF(OR({0}$34+{0}$37=0,{0}188=0)=TRUE,0%,{0}188/({0}$34+{0}$37))',
            '={0}188{1}'
        ]
        self.f_cols = ['B', 'C', 'E', 'F', 'G', 'I', 'J', 'K', 'M', 'N', 'O', 'Q', 'R', 'S',
                       'U', 'V', 'W', 'Y', 'Z', 'AA', 'AC', 'AD', 'AE', 'AG', 'AH', 'AI', 'AK',
                       'AL', 'AM', 'AO', 'AP', 'AQ', 'AS', 'AT', 'AU', 'AW']
        self.f_rows = [14, 15, 16, 22, 23, 24, 30, 31, 34, 35, 36, 37, 38, 39, 40, 45, 46,
                       49, 50, 54, 57, 58, 87, 96, 98, 116, 125, 127, 165, 174, 176, 184,
                       187, 188, 189, 190]
        self.b_rows = [7, 17, 18, 25, 26, 32, 33, 41, 42, 47, 48, 51, 52, 55, 56,
                       59, 60, 99, 100, 128, 129, 177, 178, 185, 186]
        super(FinBudgetExcel, self).__init__(templatePath, destinationPath, overwritten)

    def inputData(self, data = None):
        if data is None:
            data = {}
        teams = data.get('teams', [])
        company_name = data.get('company_name', [])
        team_names = data.get('team_names', [])
        rates = data.get('rates')

        font_name = 'Arial Unicode MS'
        font_size_8 = 8
        font_size_10 = 10
        color_blue = 5

        startRow = 4
        t_row = 0
        t_col = len(rates)

        bg_colors = {'Travel and Entertainment': 37, 'Employee Expenses': 37,
            'Distribution & Production costs': 36, 'Selling & Promotion expenses': 36,
            'Operating & Administrative expenses': 36, 'Taxation Related': 36,
            'TOTAL EXPENSES': 36}

        as_at = 'AS AT %s' % datetime.datetime.now().strftime("%m.%d.%y")

        for i, t in enumerate(teams):
            # if i == 0:
            #     excelSheet = self.workBook.Sheets[0]
            # else:
            excelSheet = self.workBook.Sheets.Add(self.workBook.Sheets[self.workBook.Sheets.Count - 1])
            excelSheet.Name = t['team_name']

            # company
            c1 = excelSheet.Cells(1, 1)
            c1.Font.Name = font_name
            c1.Font.Size = font_size_10
            c1.Font.Bold = True
            c1.Value = company_name

            # team
            c2 = excelSheet.Cells(2, 1)
            c2.Font.Name = font_name
            c2.Font.Size = font_size_10
            c2.Font.Bold = True
            c2.Value = excelSheet.Name

            # date
            c3 = excelSheet.Cells(3, 1)
            c3.Font.Name = font_name
            c3.Font.Size = font_size_10
            c3.Font.Bold = True
            c3.Value = as_at

            # currency
            c4 = excelSheet.Cells(4, 1)
            c4.Font.Name = font_name
            c4.Font.Size = font_size_10
            c4.Font.Bold = True
            c4.Font.Underline = XlUnderlineStyle.get('xlUnderlineStyleSingle')
            c4.Font.ColorIndex = color_blue
            c4.Interior.ColorIndex = 36
            # c4.Value = data.get('currency', '')

            tmp_data = t['data']
            row = len(tmp_data)
            if t_row == 0:
                t_row = row
            col = len(tmp_data[0])

            for co in range(4, col, 4):
                ca = number2alphabet(co)
                excelSheet.Range("%s%d:%s%d" % (ca, startRow, ca, startRow + row - 1)).Interior.ColorIndex = 34

            # months
            m = excelSheet.Range("B%d:%s%d" % (startRow, number2alphabet(col), startRow))
            m.Font.ColorIndex = color_blue
            m.Font.Bold = True
            m.Font.Underline = XlUnderlineStyle.get('xlUnderlineStyleSingle')
            m.HorizontalAlignment = HorizontalAlignment.get('xlCenter')

            # A,B,F
            abf = excelSheet.Range("B%d:%s%d" % (startRow + 1, number2alphabet(col), startRow + 1))
            abf.Font.ColorIndex = color_blue
            abf.Font.Bold = True
            abf.HorizontalAlignment = HorizontalAlignment.get('xlCenter')

            # Ex-Rate
            rate = excelSheet.Range("B%d:%s%d" % (startRow + 2, number2alphabet(col), startRow + 2))
            rate.Font.ColorIndex = color_blue
            rate.HorizontalAlignment = HorizontalAlignment.get('xlCenter')

            # set fee group style
            feegroups_loc = t.get('feegroups_loc')

            for index in feegroups_loc:
                cell = excelSheet.Cells(startRow + index, 1)
                cell.Font.Bold = True
                cell.Font.Underline = XlUnderlineStyle.get('xlUnderlineStyleSingle')

            obj = excelSheet.Range("A%d:%s%d" % (startRow, number2alphabet(col), startRow + row - 1))
            obj.Font.Name = font_name
            obj.Font.Size = font_size_8
            # obj.NumberFormatLocal = "#,##0.00;-#,##0.00"
            obj.NumberFormat = '_(* #,##0_);_(* (#,##0);_(* "-"??_);_(@_)'
            for line in ["xlInsideHorizontal", "xlInsideVertical", "xlEdgeBottom", "xlEdgeLeft", "xlEdgeRight", "xlEdgeTop"]:
                obj.Borders(XlBordersIndex[line]).Weight = XlBorderWeight["xlThin"]
                obj.Borders(XlBordersIndex[line]).LineStyle = 1

            obj.Value = tmp_data
            # set row background color
            for index, d in enumerate(tmp_data):
                if d[0] in bg_colors and index not in feegroups_loc:
                    excelSheet.Range("A%d:%s%d" % (startRow + index,
                        number2alphabet(col), startRow + index)).Interior.ColorIndex = bg_colors.get(d[0])
                if index > 3 and d[0] and index not in feegroups_loc:
                    for co in range(4, col, 4):
                        tmp_row = startRow + index
                        tmp_cell = excelSheet.Range("%s%d" % (number2alphabet(co), tmp_row))
                        ce1 = "%s%d" % (number2alphabet(co - 2), tmp_row)
                        ce2 = "%s%d" % (number2alphabet(co - 1), tmp_row)
                        tmp_cell.NumberFormat = '0%'
                        tmp_cell.Value = "=IF(OR(%s=0,%s=0)=TRUE,0%%,(%s-%s)/ABS(%s))" % (ce1, ce2, ce1, ce2, ce2)

            formulas_len = len(self.formulas)

            for i, co in enumerate(self.f_cols[:self.f_cols.index(number2alphabet(col)) + 1]):
                for j, f in enumerate(self.formulas):
                    if j == formulas_len - 1:
                        tmp = i / 3
                        if tmp > 0:
                            excelSheet.Range('%s%d' % (co, self.f_rows[j])).Value = f.format(co, '+%s190' % self.f_cols[(tmp - 1) * 3])
                        else:
                            excelSheet.Range('%s%d' % (co, self.f_rows[j])).Value = f.format(co, '')
                    else:
                        excelSheet.Range('%s%d' % (co, self.f_rows[j])).Value = f.format(co)

            obj.EntireColumn.AutoFit()

        # Total
        if len(team_names) > 1:
            excelSheet = self.workBook.Sheets('Total')
            excelSheet.Cells(1, 1).Value = company_name
            excelSheet.Cells(2, 1).Value = 'Total, %s' % data.get('year')
            excelSheet.Cells(3, 1).Value = as_at
            excelSheet.Range("A6:%s6" % number2alphabet(t_col)).Value = rates

            for i, co in enumerate(self.f_cols[:self.f_cols.index(number2alphabet(t_col)) + 1]):
                for r in range(8, 8 + t_row - 4):
                    if r not in self.f_rows and r not in self.b_rows:
                        tmp_range = '%s%d' % (co, r)
                        excelSheet.Range(tmp_range).Value = '=' + '+'.join(["'%s'!%s" % (n, tmp_range) for n in team_names])

        # delete TEMP sheet
        tmp_sheet = self.workBook.Sheets('TMP')
        # tmp_sheet = self.workBook.Sheets[self.workBook.Sheets.Count - 1]
        tmp_sheet.Delete()


def parseExcel(file_path):
    pythoncom.CoInitialize()
    excelObj = DispatchEx('Excel.Application')
    excelObj.Visible = False
    workBook = excelObj.Workbooks.open(file_path)
    excelSheet = workBook.Sheets(1)

    items = DBSession.query(FeeItem).filter(and_(FeeItem.active == 0, FeeItem.import_excel_row != None)).order_by(FeeItem.order)
    teams = DBSession.query(LogicTeam).filter(and_(LogicTeam.active == 0, LogicTeam.import_excel_column != None)).order_by(LogicTeam.order)

    data = []
    y_header = []
    def _f(v):
        try:
            return int(v)
        except:
            return None

    for item in items:
        y_header.append(item.label)
        data.append([(team.id, item.id, _f(excelSheet.Cells(item.import_excel_row , team.import_excel_column).Value))  for team in teams])

    result = {
              'x_header' : [team.label for team in teams],
              'y_header' : y_header,
              'data' : data
              }
    workBook.Close()

    return result



class FinSaleExcel(ExcelBasicGenerator):
    def _addColumn(self, c, *addtion):
        return number2alphabet(alphabet2number(c) + sum(addtion))

    def inputData(self, data = None):
        dataSheet = self.workBook.Sheets('DATA')
        dataSheet.Range("TITLE").Value = "Monthly Sales Report by Corporate Account - %s vs %s" % (data['PAST_YEAR'], data['CURRENT_YEAR'])
        dataSheet.Range("CURRENT_YEAR").Value = data['CURRENT_YEAR']
        dataSheet.Range("PAST_YEAR").Value = data['PAST_YEAR']
        dataSheet.Range("CURRENCY").Value = data['CURRENCY']
        dataSheet.Range("COMPANY").Value = 'Company : %s' % data['COMPANY']

        last_rate, this_rate = data['LAST_RATE'], data['THIS_RATE']
        start_row = current_row = 8
        start_col = "A"

        content, blank_row, title_row, formula_row, purple_rows, row_length = [], ['', ], [], [], [], alphabet2number("BD") - 4  # row_length should be update if the cols change
        content_start_col = self._addColumn(start_col, 4)
        total_direct_sale, total_direct_cost, total_inter_com_sale, \
        total_inter_com_cost, total_inter_dept_sale, total_inter_dept_cost = [], [], [], [], [], []
        special_customer_color_mapping = {}

        for val in data['teamdata'].values() :
            row_title = [val['team']]
            content.extend([row_title, blank_row])
            title_row.append(current_row)
            current_row += 2
            direct_sale_row, direct_cost_row, inter_com_sale_row, inter_com_cost_row, inter_dept_sale_row, inter_dept_cost_row = [], [], [], [], [], []

            special_customer = {}

            for t in val['data'].values():
                sale_row, cost_row, gp_row = current_row, current_row + 1, current_row + 2

                # fill the exchange rate formula
                usd_formula = "=%(col)s%(row)s/%(rate)s"
                sale_list = list(chain(*zip(t['last_sale'], [usd_formula] * len(t['last_sale']), t['this_sale'], [usd_formula] * len(t['this_sale']))))
                cost_list = list(chain(*zip(t['last_cost'], [usd_formula] * len(t['last_cost']), t['this_cost'], [usd_formula] * len(t['this_cost']))))

                for i in range(len(sale_list) / 4):
                    last_index, this_index = i * 4 + 1, i * 4 + 3
                    last_col, this_col = self._addColumn(content_start_col, last_index, -1), self._addColumn(content_start_col, this_index, -1)

                    sale_list[last_index] = sale_list[last_index] % {'col' : last_col, 'row' : sale_row, 'rate' : last_rate[i]}
                    cost_list[last_index] = cost_list[last_index] % {'col' : last_col, 'row' : cost_row, 'rate' : last_rate[i]}
                    sale_list[this_index] = sale_list[this_index] % {'col' : this_col, 'row' : sale_row, 'rate' : this_rate[i]}
                    cost_list[this_index] = cost_list[this_index] % {'col' : this_col, 'row' : cost_row, 'rate' : this_rate[i]}

                blank_header = [''] * len(t['header'])
                gp_formula = "=IF(%(col)s%(srow)s=0,0,(%(col)s%(crow)s/%(col)s%(srow)s-1)*-1)"

                # fill the sum formula
                last_sum_fomula = "=" + "+".join([self._addColumn(content_start_col, c * 4) + '%(row)s'  for c in range(len(sale_list) / 4)])
                last_sum_fomula_usd = "=" + "+".join([self._addColumn(content_start_col, c * 4, 1) + '%(row)s'  for c in range(len(sale_list) / 4)])
                this_sum_fomula = "=" + "+".join([self._addColumn(content_start_col, c * 4, 2) + '%(row)s'  for c in range(len(sale_list) / 4)])
                this_sum_fomula_usd = "=" + "+".join([self._addColumn(content_start_col, c * 4, 3) + '%(row)s'  for c in range(len(sale_list) / 4)])

                sum_cols = [last_sum_fomula, last_sum_fomula_usd, this_sum_fomula, this_sum_fomula_usd]

                # fill the row with content and formula
                row1 = t['header'] + ['Net Sales', ] + sale_list + map(lambda v : v % {'row' : sale_row}, sum_cols)
                row2 = blank_header + ['Cost', ] + cost_list + map(lambda v : v % {'row' : cost_row}, sum_cols)
                row3 = blank_header + ['GP Rate'] + [gp_formula % {'col' : self._addColumn(content_start_col, i), 'srow' : sale_row, 'crow' : cost_row} for i in range(len(sale_list) + len(sum_cols))]
                content.extend([row1, row2, row3, blank_row])
                formula_row.append(current_row + 2)
                current_row += 4

                if t['is_direct'] :  # if it's direct, mark down the sale and cost row
                    direct_sale_row.append(sale_row)
                    direct_cost_row.append(cost_row)
                elif t['is_inter_com'] :  # if it's inter com, mark down the sale and cost row
                    inter_com_sale_row.append(sale_row)
                    inter_com_cost_row.append(cost_row)
                elif t['is_inter_dept'] :  # if it's inter dept, mark down the sale and cost row
                    inter_dept_sale_row.append(sale_row)
                    inter_dept_cost_row.append(cost_row)

                if t['is_special_customer']:
                    special_customer_key = '%s|%s|%s' % (t['sumup_customer'], t['header'][1], t['header'][2])  # customer + saletype
                    if special_customer_key not in special_customer:
                        special_customer[special_customer_key] = []
                    special_customer[special_customer_key].append(sale_row)

                    if t['sumup_customer'] not in special_customer_color_mapping:
                        special_customer_color_mapping[t['sumup_customer']] = { 'rows' : [] , 'colorindex' : t['customer_color']}

            # fill the Subtotal rows for special customer ,such as jcp,walmat,kohls,etc
            for customer_key, rowlist in special_customer.items():
                customer, subline, sale_type = customer_key.split("|")
                special_customer_color_mapping[customer]['rows'].append(current_row)  # mark down the row's color
                _, current_row, formula_row, content = self._fill_summary(content_start_col, current_row, formula_row,
                                                content, row_length, rowlist, map(lambda v : v + 1, rowlist), 'Subtotal %s for %s(%s)' % (sale_type, customer, subline))


            # fill in the team's direct,inter com,inter dept and  summary data
            direct_row, current_row, formula_row, content = self._fill_summary(content_start_col, current_row, formula_row,
                                                content, row_length, direct_sale_row, direct_cost_row, 'Total Sales for %s-DIRECT SALES' % val['team'])
            inter_com_row, current_row, formula_row, content = self._fill_summary(content_start_col, current_row, formula_row,
                                                content, row_length, inter_com_sale_row, inter_com_cost_row, 'Total Sales for %s-INTER-CO' % val['team'])
            inter_dept_row, current_row, formula_row, content = self._fill_summary(content_start_col, current_row, formula_row,
                                                content, row_length, inter_dept_sale_row, inter_dept_cost_row, 'Total Sales for %s-INTER-DEPT' % val['team'])
            team_total_row, current_row, formula_row, content = self._fill_summary(content_start_col, current_row, formula_row,
                                                content, row_length, [direct_row, inter_com_row, inter_dept_row], [direct_row + 1, inter_com_row + 1, inter_dept_row + 1], 'Total Sales for %s' % val['team'])

            total_direct_sale.append(direct_row)
            total_direct_cost.append(direct_row + 1)
            total_inter_com_sale.append(inter_com_row)
            total_inter_com_cost.append(inter_com_row + 1)
            total_inter_dept_sale.append(inter_dept_row)
            total_inter_dept_cost.append(inter_dept_row + 1)
            purple_rows.extend([direct_row, inter_com_row, inter_dept_row, team_total_row])

        total_direct_row, current_row, formula_row, content = self._fill_summary(content_start_col, current_row, formula_row, content, row_length, total_direct_sale, total_direct_cost, "Grand Total-DIRECT SALES")
        total_inter_com_row, current_row, formula_row, content = self._fill_summary(content_start_col, current_row, formula_row, content, row_length, total_inter_com_sale, total_inter_com_cost, "Grand Total-INTER-CO")
        total_inter_dept_row, current_row, formula_row, content = self._fill_summary(content_start_col, current_row, formula_row, content, row_length, total_inter_dept_sale, total_inter_dept_cost, "Grand Total-INTER-DEPT")
        total_row, current_row, formula_row, content = self._fill_summary(content_start_col, current_row, formula_row, content, row_length,
                                                               [total_direct_row, total_inter_com_row, total_inter_dept_row], [total_direct_row + 1, total_inter_com_row + 1, total_inter_dept_row + 1], "Grand Total")

        # draw the adjustment rows
        adjust_row, current_row, formula_row, content = self._fill_summary(content_start_col, current_row, formula_row, content, row_length, [], [], "Adjustment for Factory")

        # draw the total after recon for the report
        total_direct_recon_row, current_row, formula_row, content = self._fill_summary(content_start_col, current_row, formula_row, content, row_length, [total_direct_row, ], [total_direct_row + 1, ], "Grand Total after Recon-DIRECT SALES")
        total_inter_com_recon_row, current_row, formula_row, content = self._fill_summary(content_start_col, current_row, formula_row, content, row_length, [total_inter_com_row, ], [total_inter_com_row + 1, ], "Grand Total after Recon-INTER-CO")
        total_inter_dept_recon_row, current_row, formula_row, content = self._fill_summary(content_start_col, current_row, formula_row, content, row_length, [total_inter_dept_row, adjust_row, ], [total_inter_dept_row + 1, adjust_row + 1], "Grand Total after Recon-INTER-DEPT")

        # draw the all total row for the report
        all_total_row, current_row, formula_row, content = self._fill_summary(content_start_col, current_row, formula_row, content, row_length,
                                                               [total_direct_recon_row, total_inter_com_recon_row, total_inter_dept_recon_row],
                                                               [total_direct_recon_row + 1, total_inter_com_recon_row + 1, total_inter_dept_recon_row + 1], "Grand Total after Recon")


        purple_rows.extend([total_direct_row, total_inter_com_row, total_inter_dept_row, total_row])

        row_length = max(map(len, content))
        content = [(c + ['', ] * row_length)[:row_length] for c in content]

        contentSheet = self.workBook.Sheets('CONTENT')
        # fill the rate header
        contentSheet.Range('%s%s:%s%s' % (content_start_col, start_row - 1, self._addColumn(content_start_col, 48 - 1), start_row - 1)).Value = list(chain(*zip([1] * 12, last_rate, [1] * 12, this_rate)))

        end_row = current_row - 2
        end_col = self._addColumn(start_col, row_length - 1)
        content_range = "%s%s:%s%s" % (start_col, start_row, end_col, end_row)
        contentSheet.Range(content_range).Value = content

        # draw line
        for line in ["xlEdgeBottom", "xlEdgeLeft", "xlEdgeRight", "xlEdgeTop"]:
            contentSheet.Range(content_range).Borders(XlBordersIndex[line]).Weight = XlBorderWeight["xlMedium"]
            contentSheet.Range(content_range).Borders(XlBordersIndex[line]).LineStyle = 1
        for line in ["xlInsideHorizontal", "xlInsideVertical", ]:
            contentSheet.Range(content_range).Borders(XlBordersIndex[line]).Weight = XlBorderWeight["xlThin"]
            contentSheet.Range(content_range).Borders(XlBordersIndex[line]).LineStyle = 1

        # mark the title to be colorful
        for r in title_row:  contentSheet.Cells(r, alphabet2number(start_col)).Interior.ColorIndex = 7
        # set the percentage format
        for r in formula_row : contentSheet.Range('%s%s:%s%s' % (content_start_col, r, end_col, r)).NumberFormatLocal = '0%'
        # make the grid color
        for rows, color  in [
                             (purple_rows, 24), ([adjust_row, ], 6),
                             ([total_direct_recon_row, total_inter_com_recon_row, total_inter_dept_recon_row, all_total_row, ], 7),
                            ]:
            for row in rows:
                contentSheet.Range('%s%s:%s%s' % (start_col, row, end_col, row + 2)).Interior.ColorIndex = color

        # make the special customer's summary rows to colorful
        for v in special_customer_color_mapping.values():
            for row in v['rows']:
                contentSheet.Range('%s%s:%s%s' % (start_col, row, end_col, row + 2)).Interior.ColorIndex = v['colorindex']



    def _fill_summary(self, content_start_col, current_row, formula_row, content, row_length, sale_row_list, cost_row_list, sale_title):
        def _k(a, b):
            if not a : return ['0', ] * b
            f = "=" + "+".join(['%(col)s' + unicode(row) for row in a])
            return [f % {'col' : self._addColumn(content_start_col, i)} for i in range(b)]

        def _m(srow, crow, b):
            f = '=IF(%(col)s%(srow)s=0,0,(%(col)s%(crow)s/%(col)s%(srow)s-1)*-1)'
            return [f % {'col' : self._addColumn(content_start_col, i), 'srow' : srow, 'crow': crow} for i in range(b)]

        first_row = current_row
        blank_row = ['', ]
        sale_row = [sale_title, '', '', 'Net Sales', ] + _k(sale_row_list, row_length)
        cost_row = ['', '', '', 'Cost'] + _k(cost_row_list, row_length)
        gp_row = ['', '', '', 'GP Rate'] + _m(first_row, first_row + 1, row_length)
        content.extend([sale_row, cost_row, gp_row, blank_row])
        formula_row.append(first_row + 2)
        last_row = first_row + 4

        return first_row, last_row, formula_row, content
