function baseInit (current_nav, scheme, locale, msg) {
    var $user_settings = $('a#Settings');
    var $show_delete_user = $('a#delete_user');
    var $delete_user = $('button#delete_user');
    var $show_sign_out = $('a#Logout');
    var $sign_out = $('button#sign_out');

    var local = window.location.host;

    $user_settings.bind("click", showSettings);
    $show_delete_user.bind("click", deleteConfirm);
    $delete_user.bind("click", deleteUser);
    $show_sign_out.bind("click", logoutConfirm);
    $sign_out.bind("click", signOut);
    $("#settings_modal").on("hidden.bs.modal", resetModal);
    $("li#" + current_nav).attr("class", "active");
    $("input#redirect_to").val(window.location.pathname);
    $(".r_passwd").change(function(){
        if(!is_in(" ", this.value) && this.value.length >= 6) {
            r_passwd = this.value;
            $("#r_passwd").attr("class","glyphicon glyphicon-ok col-xs-2");
        } else {
            $("#r_passwd").attr("class","glyphicon glyphicon-remove col-xs-2");
            alert(msg.password_alert);
        }
    });
    $(".r_passwd_confirm").keyup(function() {
        if(r_passwd.indexOf(this.value) == 0 && r_passwd.length == this.value.length) {
            r_passwd_confirm = this.value;
            $("#r_passwd_confirm").attr("class","glyphicon glyphicon-ok col-xs-2");
        } else {
            $("#r_passwd_confirm").attr("class","glyphicon glyphicon-remove col-xs-2");
        }
    });

    function resetModal(e) {
        console.log("Reset: ", e.target.id);
        $("#" + e.target.id).find("input:text").val("");
        $("#" + e.target.id).find("input:password").val("");
        $("#r_passwd").attr("class","glyphicon glyphicon-star col-xs-2");
        $("#r_passwd_confirm").attr("class","glyphicon glyphicon-star col-xs-2");
    }

    function showSettings() {
        if(locale == 'zh' || locale == 'zh_CN') {
            $('input:radio[name="optionsRadios"]').filter('[value="zh_CN"]').prop('checked', true);
        } else {
            $('input:radio[name="optionsRadios"]').filter('[value="en_US"]').prop('checked', true);
        }
        $('#settings_modal').modal('show');
    }

    function deleteConfirm() {
        $('#delete_user_modal').modal('show');
    }

    function deleteUser() {
        window.location.href = location.protocol + "//" + local + "/delete_user";
    }

    function logoutConfirm() {
        $('#sign_out_modal').modal('show');
    }

    function signOut() {
        window.location.href = location.protocol + "//" + local + "/logout";
    }

    function is_in(substr, str) {
        if(str.indexOf(substr, 0) != -1) {
            return 1;
        } else {
            return 0;
        }
    }
}