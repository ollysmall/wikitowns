$(document).ready(function() {

$('.upvote_website').click(function(){
  $(this).toggleClass("clicked-button");
  var websiteid = $(this).attr('data-websiteid');
  var vote_total = $('.vote_total[data-websiteid=' + websiteid + ']');
  var downvote_button = $('.downvote_website[data-websiteid=' + websiteid + ']');

  if (downvote_button.hasClass("clicked-button")){
    downvote_button.toggleClass("clicked-button");
  }

  $.ajax({

               type: "POST",
               url: '/upvote_website/',
               data: {'websiteid': websiteid},
               dataType: "json",

               success: function(response){
                                   vote_total.html(response + '&nbsp;');


                },
                error: function(response) {
                       window.location.href = '/accounts/login/';
                }
          });
    })

$('.downvote_website').click(function(){
  $(this).toggleClass("clicked-button");
  var websiteid = $(this).attr('data-websiteid');
  var vote_total = $('.vote_total[data-websiteid=' + websiteid + ']');
  var upvote_button = $('.upvote_website[data-websiteid=' + websiteid + ']');

  if (upvote_button.hasClass("clicked-button")){
    upvote_button.toggleClass("clicked-button");
  }


  $.ajax({
               type: "POST",
               url: '/downvote_website/',
               data: {'websiteid': websiteid},
               dataType: "json",

               success: function(response){
                                   vote_total.html(response + '&nbsp;');
                },
                error: function(response) {
                       window.location.href = '/accounts/login/';
                }
          });
    })

$('.bookmark_website').click(function(){
  $(this).toggleClass("clicked-button");
  var websiteid = $(this).attr('data-websiteid');

  $.ajax({
             type: "POST",
             url: '/bookmark_website/',
             data: {'websiteid': websiteid},
             dataType: "json",

             success: function(response){


              },
              error: function(response) {
                     window.location.href = '/accounts/login/';
              }
        });
  })

//gets the csrf token
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

var csrftoken = getCookie('csrftoken');

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

});
