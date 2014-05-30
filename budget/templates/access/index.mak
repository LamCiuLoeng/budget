<%inherit file="budget.templates.master"/>

<%def name="extTitle()">r-pac - Access</%def>

<div class="main-div">
	<div id="main-content">
	    <div class="block">
	    	<a href="/access/user"><img src="/images/user.jpg" width="55" height="55" alt="" /></a>
	    	<p><a href="/access/user">User Management</a></p>
	    	<div class="block-content">The module is for the "User Management" .</div>
	    </div>
	    
	    <div class="block">
        <a href="/access/group"><img src="/images/group.jpg" width="55" height="55" alt="" /></a>
        <p><a href="/access/group">Group Management</a></p>
        <div class="block-content">The module is for the "Group Management" .</div>
      </div>
      
      <div class="block">
        <a href="/access/permission"><img src="/images/permission.jpg" width="55" height="55" alt="" /></a>
        <p><a href="/access/permission">Permission Management</a></p>
        <div class="block-content">The module is for the "Permission Management" .</div>
      </div>
	
	</div>
</div>