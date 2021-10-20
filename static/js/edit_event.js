$(document).ready(function() {
    $('.btn_center').remove();
    $('.btn_centerBIG').remove();
    elements = $('.card-footer');
    for (var i = 0; i < elements.length; i++) {
        elements[i].remove();
    };
    elements = $('.flexBigInput');
    for (var i = 0; i < elements.length; i++) {
        $(elements[i]).attr('contenteditable', false);
    };
});


function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}


jQuery.postJSON = function(url, args, callback) {
    args._xsrf = getCookie("_xsrf");
    $.ajax({url: url, data: $.param(args), dataType: "text", type: "POST",
        success: function(response) {
            window.location.replace('/board' + '/' + url.split('/')[2] + '/' + 'edit');
    }});
};


function save_changes(url_) {
    $('#useless').remove();
    $.postJSON(url_, $('main').html());
}