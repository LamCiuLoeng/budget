<%inherit file="budget.templates.master"/>

<%def name="extTitle()">r-pac - Master</%def>

<%def name="extCSS()">
<link rel="stylesheet" href="/css/jquery.multiSelect.css" type="text/css" media="screen"/>
 <style type="text/css">

.width-220 {
    width: 220px;
}
  </style>
</%def>
<%def name="extJavaScript()">
<script type="text/javascript" src="/javascript/jquery.multiSelect.js"></script>
	<script language="JavaScript" type="text/javascript">
    //<![CDATA[
    	$(document).ready(function(){
    		$(".jqery_multiSelect").multiSelect();
    	});
    	
		function toSave(){
			$("form").submit();
		}
		
		function toUpdate() {
			$("form").attr("action", "/item/updateAttr");
			$("form").submit();
		}
    //]]>
   </script>
</%def>


<div id="function-menu">
    <table width="100%" cellspacing="0" cellpadding="0" border="0">
  <tbody><tr>
    <td width="36" valign="top" align="left"><img src="/images/images/menu_start.jpg"/></td>
    <td width="176" valign="top" align="left"><a href="/${funcURL}/index"><img src="/images/images/menu_${funcURL}_g.jpg"/></a></td>
    <td width="64" valign="top" align="left"><a href="#" onclick="toSave()"><img src="/images/images/menu_save_g.jpg"/></a></td>
    <td width="64" valign="top" align="left"><a href="/${funcURL}/index"><img src="/images/images/menu_cancel_g.jpg"/></a></td>
    <td width="23" valign="top" align="left"><img height="21" width="23" src="/images/images/menu_last.jpg"/></td>
    <td valign="top" style="background:url(/images/images/menu_end.jpg) repeat-x;width:100%"></td>
  </tr>
</tbody></table>
</div>

<div class="nav-tree">Master&nbsp;&nbsp;&gt;&nbsp;&nbsp;New or Update</div>

<div>
	${widget(values,action=saveURL)|n}
</div>





