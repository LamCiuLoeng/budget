<%inherit file="budget.templates.master"/>
<%
	from repoze.what.predicates import in_any_group,in_group,has_permission
%>


<%def name="extTitle()">r-pac - Finance Budget</%def>
<%def name="extCSS()">
<link rel="stylesheet" type="text/css" href="/css/redmond/jquery-ui-1.10.1.custom.min.css" media="screen,print"/>
<link rel="stylesheet" type="text/css" href="/css/showLoading.css" media="screen,print"/>
<link rel="stylesheet" type="text/css" href="/css/custom/budget.css" media="screen,print"/>
<style type="text/css">
    .ui-tabs-anchor{
    	font-size : 6px;
    }
</style>

</%def>

<%def name="extJavaScript()">
<script type="text/javascript" src="/js/jquery-ui-1.10.1.custom.min.js"></script>
<script type="text/javascript" src="/js/jquery.numeric.js"></script>
<script type="text/javascript" src="/js/jquery.showLoading.min.js"></script>
<script type="text/javascript" src="/js/util.js"></script>
<script type="text/javascript" src="/js/custom/fee_index.js"></script>

<script language="JavaScript" type="text/javascript">
	$(document).ready(function(){
		var dateFormat = 'yy-mm-dd';
        $('.datePicker').datepicker({firstDay: 1 , dateFormat: dateFormat});
		
	});

    function toSearch(){
        $("#searchForm").submit();
    }
    
    function toDownload(){
        if($("input[name='fids']:checked").length <1){
            alert('Please select at lease one file to download');
            return;
        }else{
            $("#resultForm").submit();
        }
    }
    
    function selectall(obj,name){
        var t = $(obj);
        if(t.attr('checked')){
            $("input[type='checkbox'][name='"+name+"']").attr('checked','checked');
        }else{
            $("input[type='checkbox'][name='"+name+"']").removeAttr('checked');
        }
    }
    
</script>
</%def>

<div id="function-menu">
    <table width="100%" cellspacing="0" cellpadding="0" border="0">
  <tbody><tr>
  	<td width="36" valign="top" align="left"><img src="/images/images/menu_start.jpg"/></td>
	<td width="64" valign="top" align="left"><a href="/file/index"><img src="/images/images/budget_g.jpg"/></a></td>
	<td width="64" valign="top" align="left"><a href="#" onclick="toSearch()"><img src="/images/images/menu_search_g.jpg"/></a></td>
	<td width="64" valign="top" align="left"><a href="#" onclick="toDownload()"><img src="/images/images/download_g.jpg"/></a></td>
    <td width="23" valign="top" align="left"><img height="21" width="23" src="/images/images/menu_last.jpg"/></td>
    <td valign="top" style="background:url(/images/images/menu_end.jpg) repeat-x;width:100%"></td>
  </tr>
</tbody></table>
</div>

<div class="nav-tree">Finance Budget&nbsp;&nbsp;&gt;&nbsp;&nbsp;Finance Report Upload</div>


<div style="width:1400px;margin:0px;">
    <form action="fin_index" method="POST" id="searchForm">
    	<div class="case-list-one">
    		<ul>
        		<li class="label"><label class="fieldlabel">Team</label></li>
        		<li>
        			<select name="team_id" id="team_id" style="width:250px">
    					%if len(teams) > 1:
    						<option value="">--- Select Team ---</option>
    					%endif:
    					%for t in teams:
    					   %if unicode(t.id) == values['team_id']:
    						  <option value="${t.id}" selected="selected">${t.label}</option>
    					   %else:
    					      <option value="${t.id}">${t.label}</option>
    					   %endif
    					%endfor
    				</select>
        		</li>
        	</ul>	
        	<ul>
                <li class="label"><label for="create_time_from" class="fieldlabel">Upload Date(from)</label></li>
                <li><input type="text" name="create_time_from" class="datePicker width-250 inputText" id="create_time_from" value="${values['create_time_from']}"></li>
            </ul>
            <ul>
                <li class="label"><label for="create_time_to" class="fieldlabel">Upload Date(to)</label></li>
                <li><input type="text" name="create_time_to" class="datePicker width-250 inputText" id="create_time_to" value="${values['create_time_to']}"></li>
            </ul>
    	</div>
	</form>
	<br class="clear"/>
	
	<div style="margin:5px 0px 5px 10px;width:1200px;">
	   <%
        my_page = tmpl_context.paginators.result
        pager = my_page.pager(symbol_first="<<",show_if_single_page=True)
       %>
       
        <form action="download" method="POST" id="resultForm">
            <table cellspacing="0" cellpadding="0" border="0" id="dataTable" class="gridTable budget-table">
                <thead>
                    <tr>
                        <th style='width:20px;border-left:1px solid #ccc;'>
                            <input type="checkbox" onclick="selectall(this,'fids')" style="width:30px;"/>
                        </th>
                        <th style='width:500px'>File Name</th>
                        <th style='width:100px'>Uploaded By</th>
                        <th style='width:100px'>Team</th>
                        <th style='width:150px'>Upload Time</th>                    
                    </tr>
                </thead>
                %if len(result) < 1:
                    <tr>
                        <td colspan="8" style="border-left:1px solid #ccc">No Record Found.</td>
                    </tr>
                %else:
                    %for f,l,u in result:
                        <tr>
                            <td style='border-left:1px solid #ccc;'>
                                <input type="checkbox" name="fids" value="${f.uploadObject_id}" style="width:30px;"/>
                            </td>
                            <td style="text-align:left">${f.uploadObject.file_name}</td>
                            <td>${u}</td>
                            <td>${l}</td>
                            <td>${f.create_time.strftime("%Y/%m/%d %H:%M")}</td>
                        </tr>
                    %endfor
                %endif
                %if my_page.item_count > 0 :
                <tr>
                    <td style="text-align:right;border-right:0px;border-bottom:0px" colspan="20">
                        ${pager}, <span>${my_page.first_item} - ${my_page.last_item}, ${my_page.item_count} records</span>
                    </td>
                </tr>
                %endif
            </table>  
        </form>  
	</div>
</div>