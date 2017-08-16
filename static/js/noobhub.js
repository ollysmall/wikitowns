$(document).ready(function(){
	$('#myTab a:first').tab('show');

	//changes button text on click for descriptions button
	$(document).on("click", '.description-button', function(e){
    var $this = $(this);
    $this.toggleClass('SeeMore');
    if($this.hasClass('SeeMore')){
        $this.text('View description').append('&nbsp;&nbsp;<i class="fa fa-caret-down" aria-hidden="true"></i>');
    } else {
        $this.text('Hide description').append('&nbsp;&nbsp;<i class="fa fa-caret-up" aria-hidden="true"></i>');
    }
	})
});

$(function() {
    $('a[data-toggle="tab"]').on('shown.bs.tab', function (e) {
        // save the latest tab
        localStorage.setItem('lastTab', $(this).attr('href'));
    });

    // go to the latest tab, if it exists:
    var lastTab = localStorage.getItem('lastTab');
    if (lastTab) {
        $('[href="' + lastTab + '"]').tab('show');
        //window.localStorage.removeItem("lastTab");
    }
});
