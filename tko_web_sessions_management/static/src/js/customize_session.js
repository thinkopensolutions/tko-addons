/*---------------------------------------------------------
 * OpenErp Session Expired
 *---------------------------------------------------------*/

$( document ).ready(function(){
	$("body").click(function(){
		$.getJSON("/ajax/session/", function( data ){
		if(data)
			{
				var uid = data[0];
				if(uid.result == 'true')
				{
					location.reload();
				}	
			}
		});	

	});
}); 
