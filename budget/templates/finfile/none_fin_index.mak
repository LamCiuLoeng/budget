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
    
    .template{
        display : none;
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
		
	});

    function toSubmit(){
        if(!$("#team_id").val()){ 
            alert("Please select the 'Team' before submit!.");
            return;
        }else{
            $(".template").remove();
            $('form').submit();
        }
    }
    
    var count = 11;
    function toAdd(){
        var t = $(".template").clone();
        t.removeClass('template');
        var index = count++;
        $('input[type="file"]',t).each(function(){
            var k = $(this);
            k.attr('name',k.attr('name')+index);
        });
        $('#filetbl').append(t);
    }
    
    function toDel(obj){
        var t = $(obj);
        $(t.parents('tr')[0]).remove();
    }
</script>
</%def>

<div id="function-menu">
    <table width="100%" cellspacing="0" cellpadding="0" border="0">
  <tbody><tr>
  	<td width="36" valign="top" align="left"><img src="/images/images/menu_start.jpg"/></td>
	<td width="64" valign="top" align="left"><a href="/file/index"><img src="/images/images/budget_g.jpg"/></a></td>	
    <td width="23" valign="top" align="left"><img height="21" width="23" src="/images/images/menu_last.jpg"/></td>
    <td valign="top" style="background:url(/images/images/menu_end.jpg) repeat-x;width:100%"></td>
  </tr>
</tbody></table>
</div>

<div class="nav-tree">Finance Budget&nbsp;&nbsp;&gt;&nbsp;&nbsp;Finance Report Upload</div>


<div style="width:1400px;margin:0px;">
    <form action="upload" method="POST" enctype="multipart/form-data">
    
    
	<div class="case-list-one" style='width:900px;'>
        %if len(teams) > 1 :
            <ul style="width:800px">
                <li class="label"><label class="fieldlabel">Team</label></li>
                <li>
                    <select name="team_id" id="team_id">
                        <option value=""></option>
                        %for t in teams:
                            <option value="${t.id}">${t}</option>
                        %endfor
                    </select>
                </li>
            </ul>
        %elif len(teams) == 1:
            <input type="hidden" name="team_id" id="team_id" value="${teams[0].id}"/>
        %endif
    
		<ul style="width:800px">
    		<li class="label"><label class="fieldlabel">File</label></li>
    		<li>
    		    <table id="filetbl">
    		        <tr>
    		            <td><input type="file" name="file10"/></td>
    		            <td style="width:100px"><input type="button" value="Add" onclick="toAdd()" class="btn"/></td>
    		            <td style="width:100px"><input type="button" value="Upload" class="btn" onclick="toSubmit()"/></td>
    		        </tr>
    		        <tr class="template">
    		            <td><input type="file" name="file"/></td>
    		            <td><input type="button" value="Del" onclick="toDel(this)" class="btn"/>
    		        </tr>
    		    </table>
    		</li>
    	</ul>
	</div>	
  	
	</form>
	
	<br class="clear"/>
	
	<div style="margin:5px 0px 5px 10px;width:1200px;">
	   <%
        my_page = tmpl_context.paginators.result
        pager = my_page.pager(symbol_first="<<",show_if_single_page=True)
       %>
        <table cellspacing="0" cellpadding="0" border="0" id="dataTable" class="gridTable budget-table">
            <thead>
                <tr>
                    <th style='width:500px;border-left:1px solid #ccc;'>File Name</th>
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
                        <td style='border-left:1px solid #ccc;text-align:left'>${f.uploadObject.file_name}</td>
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
	</div>
</div>