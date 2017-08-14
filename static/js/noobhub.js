$(document).ready(function(){
	$('#myTab a:first').tab('show');
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
