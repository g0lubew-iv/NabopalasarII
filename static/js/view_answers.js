$(document).ready(function() {})


function selectForm(arrayUsers) {
        for (var i = 0; i < arrayUsers.length; ++i) {
            if ($("#SELECT option:selected").hasClass(`SSS${arrayUsers[i]}`)) {
                // Admin have choose answers of this user. Take it their!
                el = document.querySelector(`.sel${arrayUsers[i]}`);
                el.style.display = 'block';
            }
            else {
                el = document.querySelector(`.sel${arrayUsers[i]}`);
                el.style.display = 'none';
            }
        }
}