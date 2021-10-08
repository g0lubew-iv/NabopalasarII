$(document).ready(function() {
    $('.btn_center').remove();
    $('.btn_centerBIG').remove();
    elements = $('.form-select');
    for (var i = 0; i < elements.length; i++) {
        $(elements[i]).parent().remove();
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


function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}


jQuery.postJSON = function(url, args, callback) {
    args._xsrf = getCookie("_xsrf");
    $.ajax({url: url, data: $.param(args), dataType: "json", type: "POST",
        success: function(response) {
    }});
};


function closeEvent() {
    window.close();
}


function getParent(el) {
    if (el.parentElement){
        return el.parentElement;
  }

  if (el.parentNode){
        return el.parentNode;
  }

  return null;
}


function post_results(url_) {
// Collecting user's answers on forms
      var answers = document.getElementsByTagName('input');
// first - 'search' input of base page (navbar), last - submit button
      var res = ['<br>'];
      for (var a = 1; a < answers.length - 1; a++) {
//        if (answers[a].id.indexOf('inputGroupFile') >= 0) {
//            res_ = `<div class="card">
//                      <div class="card-body">
//                        ${(answers[a].files.length > 0) ? answers[a].files[0].name : '<small style="color:#777777;">There is nothing</small>'}
//                      </div>
//                    </div>`
//            res.push(res_);
//        }
          res.push(answers[a]);
      }
      const form_res = document.getElementById("event_questions");
      results = {"textarea": [], "text": [], "radio": [], "checkbox": [], "file": []};
      for (var el = 0; el < form_res.length - 2; el++) {
          // last two elements of form are not inputs
          if (form_res[el].tagName == 'TEXTAREA') {
              if (form_res[el].value) {
                  results["textarea"].push({"idElement": getParent(form_res[el]).id, "value": form_res[el].value});
              }
          }
          else {
              if (form_res[el].type == 'text') {
                if (form_res[el].value) {
                    results["text"].push({"idElement": getParent(getParent(form_res[el])).id, "value": form_res[el].value});
                }
              }
              else
                  if (form_res[el].type == 'radio') {
                    if (form_res[el].checked) {
                        results["radio"].push({"idElement": form_res[el].id, "value": form_res[el].value});
                    }
                  }
                  else
                      if (form_res[el].type == 'checkbox') {
                        if (form_res[el].checked) {
                            results["checkbox"].push({"idElement": form_res[el].id, "value": form_res[el].value});
                        }
                      }
                      else
                          if (form_res[el].type == 'file') {
                            if (form_res[el].value) {
                                results["file"].push({"idElement": form_res[el].id, "value": form_res[el].value});
                            }
                          }
          }
      }
      // console.log(results);
      $.postJSON(url_, results);
      $('main').html(`<br><br><div class="alert alert-success alert-dismissible fade show" role="alert">
                            <h4 class="alert-heading">Great, really!</h4>
                            <p>Oh yes, you have completed this event.<br>What to do with your answers next will be decided by the admin of this board.</p>
                            <hr>
                            <p class="mb-0">Thank you for standing up!</p>
                            <button type="button" class="btn-close" data-bs-dismiss="alert" onclick="closeEvent();" aria-label="Close"></button>
                      </div>`);
      // window.location.replace('/board' + '/' + url_.split('/')[2] + '/' + 'view');
}