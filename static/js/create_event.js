var numberForms = 1;
var numberTitles = 0;
var numberImages = 0;
var numberVideos = 0;
var numberFiles = 0;
var currentColor = 'secondary';


function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}


jQuery.postJSON = function(url, args, callback) {
    args._xsrf = getCookie("_xsrf");
    $.ajax({url: url, data: $.param(args), dataType: "text", type: "POST",
        success: function(response) {
        window.close();
    }});
};


function saveChanges(url_) {
    $.postJSON(url_, $('main').html());
}


function fileIsLoaded() {
  alert("Successfully load!");
}


function changeColor(Color) {
    var forms = document.getElementsByName("Form");
    for (var f = 0; f < numberForms; f++) {
        $(forms[f]).parent().html($(forms[f]).parent().html().replaceAll('border-' + currentColor, 'border-' + Color));
    }
    currentColor = Color;
}


function deleteTITLE(numberTitle) {
    numberTitles--;
    var titleEl = document.getElementById('TITLE' + String(numberTitle));
    $(titleEl).remove();
}


function deleteIMAGE(numberImage) {
    numberImages--;
    var imEl = document.getElementById('IMAGE' + String(numberImage));
    $(imEl).remove();
}


function deleteFILE(numberFile) {
    numberFiles--;
    var fileEl = document.getElementById('FILE' + String(numberFile));
    $(fileEl).remove();
}


function deleteVIDEO(numberVideo) {
    numberVideos--;
    var videoEl = document.getElementById('VIDEO' + String(numberVideo));
    $(videoEl).remove();
}


function addCheckBox(idForm) {
    var checkboxes = document.getElementById("checkboxes" + String(idForm));
    var number_checkboxes = $(checkboxes).html().split('<br>').length;
    var last_checkbox = ""
    if (number_checkboxes > 1) {
        var counter = 1;
        while (last_checkbox.length == 0) {
            var last_checkbox = $(checkboxes).html().split('<br>')[number_checkboxes - counter];
            counter++;
        }
    }
    else {
        var last_checkbox = $(checkboxes).html();
    }
    // var last_checkbox = $(checkboxes).html().split('<br>')[number_checkboxes - 1];
    var new_checkbox = last_checkbox.replaceAll(`removeCheckBox(${idForm}, ${number_checkboxes})`, `removeCheckBox(${idForm}, ${number_checkboxes+1})`).replaceAll('checkbox' + String(number_checkboxes), 'checkbox' + String(number_checkboxes + 1)).replaceAll('Option ' + String(number_checkboxes), 'Option ' + String(number_checkboxes + 1));
    $(checkboxes).append('<br>' + new_checkbox);
}


function addOtherCheckBox(idForm) {
    var res = document.getElementById("result" + String(idForm));
    $(res).html($(res).html().replace(`>Other...</button>`, `
    disabled >

    </button>
    `));
}


function removeCheckBox(idForm, idBox) {
    if (idBox > 1) {
        // first checkbox we cannot delete...
        var allBoxes = $(document.getElementById("checkboxes" + String(idForm)));
        var checkBoxDeleted = $(document.getElementById("checkboxes" + String(idForm))).html().split('<br>')[idBox - 1];
        $(allBoxes).html($(allBoxes).html().replaceAll(checkBoxDeleted, ''));
    }
}


function addRadio(idForm) {
    var radios = document.getElementById("radios" + String(idForm));
    var number_radios = $(radios).html().split('<br>').length;
    var last_radio = ""
    if (number_radios > 1) {
        var counter_ = 1;
        while (last_radio.length == 0) {
            var last_radio = $(radios).html().split('<br>')[number_radios - counter_];
            counter_++;
        }
    }
    else {
        var last_radio = $(radios).html();
    }
    // var last_checkbox = $(checkboxes).html().split('<br>')[number_checkboxes - 1];
    var new_radio = last_radio.replaceAll(`removeRadio(${idForm}, ${number_radios})`, `removeRadio(${idForm}, ${number_radios+1})`).replaceAll('radio' + String(number_radios), 'radio' + String(number_radios + 1)).replaceAll('Option ' + String(number_radios), 'Option ' + String(number_radios + 1)).replaceAll(`value="option${number_radios}"`, `value="option${number_radios + 1}"`);
    $(radios).append('<br>' + new_radio);
}


function removeRadio(idForm, idRadio) {
    if (idRadio > 1) {
        // first radio we cannot delete too...
        var allRadios = $(document.getElementById("radios" + String(idForm)));
        var radioDeleted = $(document.getElementById("radios" + String(idForm))).html().split('<br>')[idRadio - 1];
        $(allRadios).html($(allRadios).html().replaceAll(radioDeleted, ''));
    }
}


function copyForm(idForm) {
    var container = $("#FormsContainer");
    numberForms++;
    var numberCopied = Number(idForm.split("CLONE")[1]);
    var formCopied = document.getElementsByName("Form")[numberCopied - 1];
    container.append(`<div class="card border-${currentColor} mb-3" name="Form" style="max-width:50em;display:block;margin-left:auto;margin-right:auto;">` + formCopied.innerHTML.replaceAll
    (`id="${idForm}" onclick="copyForm('btnCLONE${numberCopied}')"`, `id="btnCLONE${numberForms}" onclick="copyForm('btnCLONE${numberForms}')"`).replaceAll(`id="SELECT${numberCopied}" onclick="selectForm(${numberCopied})"`, `id="SELECT${numberForms}" onclick="selectForm(${numberForms})"`).replaceAll(`id="result${numberCopied}"`, `id="result${numberForms}"`).replaceAll(`onclick="deleteForm(${numberCopied})"`, `onclick="deleteForm(${numberForms})"`) + `</div>`);
}


function deleteForm(idFormInteger) {
    var container = $("#FormsContainer");
    var forms = document.getElementsByName("Form");
    var formDeleted = forms[idFormInteger - 1];
    formDeleted.remove();
    numberForms--;
    for (let i = 0; i < numberForms; i++) {
        var idFORM = Number(forms[i].innerHTML.split('"selectForm(')[1].split(')"')[0]);
        if (idFORM > numberForms) {
            // Ops...
            var $newEl = $(`<div class="card border-secondary mb-3" name="Form" style="max-width:50em;display:block;margin-left:auto;margin-right:auto;">` + formDeleted.innerHTML.replaceAll(`id="${idFORM}" onclick="copyForm('btnCLONE${idFORM}')"`, `id="btnCLONE${idFORM - 1}" onclick="copyForm('btnCLONE${idFORM - 1}')"`).replaceAll(`id="SELECT${idFORM}" onclick="selectForm(${idFORM})"`, `id="SELECT${idFORM-1}" onclick="selectForm(${idFORM-1})"`).replaceAll(`id="result${idFORM}"`, `id="result${idFORM-1}"`).replaceAll(`onclick="deleteForm(${idFORM})"`, `onclick="deleteForm(${idFORM-1})"`) + `</div>`);
            $newEl.appendTo(container);
            forms[i].remove();
        }
    }
}


function addNewForm() {
    var container = $("#FormsContainer");
    numberForms++;
    container.append(`<div class="card border-secondary mb-3" name="Form" style="max-width:50em;display:block;margin-left:auto;margin-right:auto;">
        <div class="card-body">
            <div class="row">
                <div class="col">
                    <div class="formTitle" contenteditable="true">Form without a header</div>
                </div>
                <div class="col">
                    <select class="form-select" style="width:20em;margin-left:5em;" id="SELECT${numberForms}" onclick="selectForm(${numberForms})">
                      <option disabled selected>None</option>
                      <option class="sel1">Text (string)</option>
                      <option class="sel2">Text (paragraph)</option>
                      <option class="sel3"> One  from the list</option>
                      <option class="sel4">A few from the list</option>
                      <option class="sel5">Uploading a file</option>
                    </select>
                </div>
            </div>
        </div>
        <div class="card-body">
            <div id="result1"></div><br>
            <div class="flexSmallInput" name="description_form" contenteditable="true">... And without a description?</div>
        </div>
        <br>
        <div class="card-footer">
            <div class="btn-group btn-group-sm" role="group" style="margin-left:43em;">
                <button type="button" class="btn btn-outline-secondary" id="btnCLONE${numberForms}" onclick="copyForm('btnCLONE${numberForms}')">
                     <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-files" viewBox="0 0 16 16">
                      <path d="M13 0H6a2 2 0 0 0-2 2 2 2 0 0 0-2 2v10a2 2 0 0 0 2 2h7a2 2 0 0 0 2-2 2 2 0 0 0 2-2V2a2 2 0 0 0-2-2zm0 13V4a2 2 0 0 0-2-2H5a1 1 0 0 1 1-1h7a1 1 0 0 1 1 1v10a1 1 0 0 1-1 1zM3 4a1 1 0 0 1 1-1h7a1 1 0 0 1 1 1v10a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V4z"/>
                    </svg>
                </button>
                <button class="btn btn-outline-secondary" onclick="deleteForm(${numberForms})">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-trash" viewBox="0 0 16 16">
                      <path d="M5.5 5.5A.5.5 0 0 1 6 6v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm2.5 0a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm3 .5a.5.5 0 0 0-1 0v6a.5.5 0 0 0 1 0V6z"/>
                      <path fill-rule="evenodd" d="M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4h-.5a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1H6a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1h3.5a1 1 0 0 1 1 1v1zM4.118 4 4 4.059V13a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V4.059L11.882 4H4.118zM2.5 3V2h11v1h-11z"/>
                    </svg>
                </button>
            </div>
        </div>
    </div>`);
}


function changeFilterFiles(checkbox) {
    idThisForm = Number(checkbox.id.split('_')[1]);
    if (checkbox.checked) {
        // on
    } else {
        // off

    }
}


function selectForm(idFormInteger) {
        if ($(`#SELECT${idFormInteger} option:selected`).hasClass("sel1")) {
            $(`#result${idFormInteger}`).html(`
            <div class="input-group flex-nowrap">
            <span class="input-group-text" id="addon-wrapping">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-filter-left" viewBox="0 0 16 16">
              <path d="M2 10.5a.5.5 0 0 1 .5-.5h3a.5.5 0 0 1 0 1h-3a.5.5 0 0 1-.5-.5zm0-3a.5.5 0 0 1 .5-.5h7a.5.5 0 0 1 0 1h-7a.5.5 0 0 1-.5-.5zm0-3a.5.5 0 0 1 .5-.5h11a.5.5 0 0 1 0 1h-11a.5.5 0 0 1-.5-.5z"/>
            </svg>
            </span>
            <input type='text' class="form-control" value='&nbsp;Short user answer' style='background-color:#ffffff;color:#777777;max-width:25em;'readonly>
            </div>
            `);
        } else if ($(`#SELECT${idFormInteger} option:selected`).hasClass("sel2")) {
            $(`#result${idFormInteger}`).html(`<textarea type='text' class='formUserManyAnswer' readonly>&nbsp;Detailed user answer</textarea>`);
        } else if ($(`#SELECT${idFormInteger} option:selected`).hasClass("sel3")) {
            $(`#result${idFormInteger}`).html(`
            <div id="radios${idFormInteger}">
                <div class="form-check">
                <div class="row">
                    <div class="col">
                        <div style="margin-left:1em;">
                          <input class="form-check-input" type="radio" id="radio1_${idFormInteger}" name="radioRADIO_${idFormInteger}" value="option1" style="transform:scale(1.1);border-color:#333333;" disabled>
                          <div class="flexInput" contenteditable="true">&nbsp;Option 1</div>
                        </div>
                    </div>
                    <div class="col">
                        <button type="button" class="btn-close" aria-label="Close" onclick="removeRadio(${idFormInteger}, 1)"></button>
                    </div>
                </div>
                </div>
            </div>
            <br><button type="button" style="margin-left:1em;" class="btn btn-outline-info btn-sm" onclick="addRadio(${idFormInteger})">Add an option</button>
            <input type="checkbox" class="btn-check" id="other-radio-${idFormInteger}" autocomplete="off">
            <label style="color:#777777;" class="btn btn-outline-info btn-sm" for="other-radio-${idFormInteger}">Add the "Other" option</label>
            `);
        } else if ($(`#SELECT${idFormInteger} option:selected`).hasClass("sel4")) {
            $(`#result${idFormInteger}`).html(`
            <div id="checkboxes${idFormInteger}">
                <div class="row">
                    <div class="col">
                    <div style="margin-left:1em;">
                      <input class="form-check-input" type="checkbox" id="checkbox1_${idFormInteger}" style="transform:scale(1.3);border-color:#333333;" disabled>
                      <div class="flexInput" contenteditable="true">&nbsp;Option 1</div>
                    </div>
                    </div>
                    <div class="col">
                    <button type="button" class="btn-close" aria-label="Close" onclick="removeCheckBox(${idFormInteger}, 1)"></button>
                    </div>
                </div>
            </div>
            <br>
            <button type="button" style="margin-left:1em;" class="btn btn-outline-info btn-sm" onclick="addCheckBox(${idFormInteger})">Add an option</button>
            <input type="checkbox" class="btn-check" id="other-checkbox-${idFormInteger}" autocomplete="off">
            <label style="color:#777777;" class="btn btn-outline-info btn-sm" for="other-checkbox-${idFormInteger}">Add the "Other" option</label>
            `);
        } else if ($(`#SELECT${idFormInteger} option:selected`).hasClass("sel5")) {
            $(`#result${idFormInteger}`).html(`
            <div class="row">

            <div class="col">
            <div class="input-group">
              <input type="file" class="form-control" id="inputGroupFile_${idFormInteger}" style='background-color:#ffffff;color:#777777;max-width:25em;' multiple accept="image/*, text/*, application/*, video/*, audio/*" readonly>
              <button class="btn btn-outline-success" type="button" id="inputGroupFileAddon" disabled>
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-upload" viewBox="0 0 16 16">
                  <path d="M.5 9.9a.5.5 0 0 1 .5.5v2.5a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-2.5a.5.5 0 0 1 1 0v2.5a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2v-2.5a.5.5 0 0 1 .5-.5z"/>
                  <path d="M7.646 1.146a.5.5 0 0 1 .708 0l3 3a.5.5 0 0 1-.708.708L8.5 2.707V11.5a.5.5 0 0 1-1 0V2.707L5.354 4.854a.5.5 0 1 1-.708-.708l3-3z"/>
              </svg>
              </button>
            </div>
            </div>

            <div class="col" style="margin-left:2em;">
                <div class="select_Admin">
                <p style="color:#777777;">For more information about mime types, <a href="https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types/Common_types" style="decoration:none;color:black;" target="_blank">see here</a></p>
                <div class="form-check">
                  <input class="form-check-input" type="checkbox" name="flexRadioDefault" id="flexRadioDefault1_${idFormInteger}" onchange="changeFilterFiles(this);" checked>
                  <label class="form-check-label" for="flexRadioDefault1">
                    Image
                  </label>
                </div>

                <div class="form-check">
                  <input class="form-check-input" type="checkbox" name="flexRadioDefault" id="flexRadioDefault2_${idFormInteger}" onchange="changeFilterFiles(this);" checked>
                  <label class="form-check-label" for="flexRadioDefault2">
                    Text
                  </label>
                </div>

                <div class="form-check">
                  <input class="form-check-input" type="checkbox" name="flexRadioDefault" id="flexRadioDefault5_${idFormInteger}" onchange="changeFilterFiles(this);" checked>
                  <label class="form-check-label" for="flexRadioDefault5">
                    Application
                  </label>
                </div>

                <div class="form-check">
                  <input class="form-check-input" type="checkbox" name="flexRadioDefault" id="flexRadioDefault3_${idFormInteger}" onchange="changeFilterFiles(this);" checked>
                  <label class="form-check-label" for="flexRadioDefault3">
                    Video
                  </label>
                </div>

                <div class="form-check">
                  <input class="form-check-input" type="checkbox" name="flexRadioDefault" id="flexRadioDefault4_${idFormInteger}" onchange="changeFilterFiles(this);" checked>
                  <label class="form-check-label" for="flexRadioDefault4">
                    Audio
                  </label>
                </div>
                </div>
                </div>
            </div>
            `);
        }
    }


function createNewTitle() {
    numberTitles++;
    var container = $("#FormsContainer");
    container.append(`<div class="card text-dark bg-light mb-3" id="TITLE${numberTitles}" style="max-width:50em;display:block;margin-left:auto;margin-right:auto;">
      <div class="card-body" style="text-align:center;">
          <div class="flexBigInput" style="font-size:20pt;" contenteditable="true">${numberTitles} title</div>
      </div>
      <div class="card-body">
          <div class="flexSmallInput" contenteditable="true">And... new description?</div>
      </div>
      <div class="card-footer">
            <button class="btn btn-outline-danger" style="margin-left:45.2em;" onclick="deleteTITLE(${numberTitles})">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-trash" viewBox="0 0 16 16">
                      <path d="M5.5 5.5A.5.5 0 0 1 6 6v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm2.5 0a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm3 .5a.5.5 0 0 0-1 0v6a.5.5 0 0 0 1 0V6z"/>
                      <path fill-rule="evenodd" d="M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4h-.5a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1H6a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1h3.5a1 1 0 0 1 1 1v1zM4.118 4 4 4.059V13a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V4.059L11.882 4H4.118zM2.5 3V2h11v1h-11z"/>
                    </svg>
            </button>
      </div>
    </div>`);
}
