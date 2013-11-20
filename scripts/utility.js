function currentTime() {
	var d = new Date();
	var time = d.getHours();
	var min = d.getMinutes()
	return time += ":" + (min < 10 ? '0' : '') + min ;
}

function currentDateTime(time) {
	var s = $('.dateTitle').text();
	var d = new Date();
	
	var month = d.getMonth()+1;
	var day = d.getDate();

	var date = d.getFullYear() + '/' +
		(month<10 ? '0' : '') + month + '/' +
		(day<10 ? '0' : '') + day;
		
	$('.dateTitle').text(s + date + " " + time);
}

$(document).ready(function() {
	var pathname = window.location.pathname;
	var time = currentTime();
	if (pathname === '/chatcount') {
		$('.timeTitle').append(time);
	} 
    
    if (pathname === "/") {
        $('.navbar-nav li').addClass("active");
    } else {
        $('.navbar-nav li').removeClass("active");
    }
	
	currentDateTime(time);
	
	$('form').submit(function(event) {
		var reg = /[A-Za-zöäÖÄ0-9 _\/,:\-.\n]/;
		var s = $("textarea").val();
		
		for (var i = 0; i < s.length; i++) {
		  if (reg.test(s[i])) {
			continue;
		  } else {
			$('textarea').after("<p>VIRHE! Tähän kenttään saa syöttää vain akkosnumeerista dataa ja näitä merkkejä /,:-_.</p>");
			event.preventDefault();
			break;
		  }
		}
	});
	
});
