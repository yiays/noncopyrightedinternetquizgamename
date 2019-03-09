let lasttime=0;
function getstate(){
	$.ajax({
		method:"POST",
		data:{'cmd':'getstate'},
		success: function(data){
			if(data.answered){
				$('.quadparent').addClass('dead');
				$('.quadparent').removeClass('live');
				$('.chosen').removeClass('chosen');
			}else{
				$('.dead').removeClass('dead');
				$('.quadparent').addClass('live');
				$('.chosen').removeClass('chosen');
			}
			if(data.time>0){
				if(data.time>lasttime){
					/*$('#countdown svg').clone(true);
					$('#countdown svg:first-of-type').remove();*/
					$('#countdown svg circle:last-child').css('animation','countdown '+data.time+'s linear infinite forwards');
				}
				$('#countdown-number').text(data.time);
			}else{
				$('#countdown-number').text("...");
			}
			$('.username').text(data.player);
			$('.lead').text(data.lead);
			$('.score').text(data.score);
			lasttime=data.time;
		},
		error: function(response) {
			console.log("Failed to get state.");
			if(response.status==410){
				alert("Game over! Thanks for playing!");
				window.location="/";
			}
			if(response.status==403){
				alert("You're not authorised to be here.");
				window.location="/";
			}
			return false;
		}
	});
	setTimeout(getstate,1000);
}

$(document).ready(function(){
	getstate()
	
	let dummyEm = $('.dummy-em').innerHeight();
	$(".quadparent").css('height',($(window).height()-dummyEm).toString()+'px');
});
$(window).resize(function() {
	let dummyEm = $('.dummy-em').innerHeight();
	$(".quadparent").css('height',($(window).height()-dummyEm).toString()+'px');
});

function sendclick(col,me){
	$.ajax({
		method:"POST",
		data:{
			'cmd':'btn',
			'answer':col
		},
		success: function(data) {
			$('.quadparent').addClass('dead');
			$('.quadparent').removeClass('live');
			$(me).addClass('chosen');
		},
		error: function() {
			console.log("Failed to send button press.");
			return false;
		}
	});
}
$('.red').click(function(){
	if($(this).parent().hasClass('live')){
		sendclick(0,this);
	}
});
$('.blue').click(function(){
	if($(this).parent().hasClass('live')){
		sendclick(1,this);
	}
});
$('.yellow').click(function(){
	if($(this).parent().hasClass('live')){
		sendclick(2,this);
	}
});
$('.green').click(function(){
	if($(this).parent().hasClass('live')){
		sendclick(3,this);
	}
});