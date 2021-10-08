$(document).ready(function() {
    $('.btn_center').remove();
    $('.btn_centerBIG').remove();
    elements = $('.form-select');
    for (var i = 0; i < elements.length; i++) {
        if (elements[i].id != "SELECT_SEL") {$(elements[i]).parent().remove()};
    };
    elements = $('.card-footer');
    for (var i = 0; i < elements.length; i++) {
        elements[i].remove();
    };
    elements = $('.flexSmallInput');
    for (var i = 0; i < elements.length; i++) {
        $(elements[i]).attr('contenteditable', false);
    };
    elements = $('.flexBigInput');
    for (var i = 0; i < elements.length; i++) {
        $(elements[i]).attr('contenteditable', false);
    };
    elements = $('.flexInput');
    for (var i = 0; i < elements.length; i++) {
        $(elements[i]).attr('contenteditable', false);
    };
    elements = $('.formTitle');
    for (var i = 0; i < elements.length; i++) {
        $(elements[i]).attr('contenteditable', false);
    };
    elements = $('.btn-close');
    for (var i = 0; i < elements.length; i++) {
        elements[i].remove();
    };
    elements = $('.btn.btn-outline-info.btn-sm');
    for (var i = 0; i < elements.length; i++) {
        $(elements[i]).remove();
    };
    $('.select_Admin').remove();
    for (var i = 0; i < 3; i++) {
        $('br').last().remove();
    };
    $('body')
    .one('focus.textarea', '.formUserManyAnswer', function(e) {
        baseH = this.scrollHeight;
    })
    .on('input.textarea', '.formUserManyAnswer', function(e) {
        if(baseH < this.scrollHeight) {
            $(this).height(0).height(this.scrollHeight);
        }
        else {
            $(this).height(0).height(baseH);
        }
    });
});


function change_answers(dictAnswers, n, author) {
        for (var key in dictAnswers[n]) {
            if (key == author) {
                ans = dictAnswers[n][key];
            }
        }
        for (var key in ans) {
            el = document.getElementById(key);
            if (el.tagName == 'DIV') {
                el.childNodes.length == 1 ? child = el.childNodes[0] : child = el.childNodes[1].childNodes[3];
                child.value = ans[key];
            }
            else {
                if (el.className == 'form-check-input') {
                    el.checked = true;
                }
                else {
                    // file...

                }
            }
        }
}


function selectForm13(arrayUsers, answers) {
        for (var i = 0; i < arrayUsers.length; ++i) {
            if ($("#SELECT_SEL option:selected").hasClass(`SSS${arrayUsers[i]}`)) {
                // Admin have choose answers of this user. Take it their!
                change_answers(answers, i, arrayUsers[i]);
            }
        }
}