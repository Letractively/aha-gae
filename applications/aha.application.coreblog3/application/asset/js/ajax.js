// basic Ajax functions

function replace_id(target, data) {
    // A function to replace element

    $("#"+target).html(data);

}

function remote_request(url, target, data) {
    // A function to post remote request, and replace element
    // according to given response

    $.post(url, data, function(result) {replace_id(target, result);});

}


function remote_get_request(url, target, data) {
    // A function to post remote request, and replace element
    // according to given response

    $.get(url, data, function(result) {replace_id(target, result);});

}

function remote_form_request(form, target, after) {
    // A function to post remote form request, and replace element
    // according to given response

    var fields = $('#'+form.id).serialize();
    var action = $('#'+form.id).attr('action');
    remote_request(action, target, fields);

    return false;

}

function show_status_menu(id, target) {
    // A function to replace given block filling with form to change status
    remote_get_request(target, 'state_'+id, {});

}

// handle toggle form
$(document).ready(function () {
$('.toggle-button').toggle(
    function() { // handlerOdd
        $(this).attr('src', '/style/img/expanded.gif');
        $(this).parent().siblings('.togglable').slideToggle('fast');
        },
    function() { // handlerEven
        $(this).attr('src', '/style/img/collapsed.gif');
        $(this).parent().siblings('.togglable').slideToggle('fast');
        }
    );
});


