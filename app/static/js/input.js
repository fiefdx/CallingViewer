function inputInit () {
    var $table_body = $("#dot_matrix_input");
    var $table_body_display = $("#display_dot_matrix");
    var $input_area = $("textarea#text_input");
    var $btn_clear = $("#btn-clear");
    var $btn_clear_ok = $("#warning_clear_input_ok");
    var $input_list_ul = $("#inputs_list_ul");
    var $btn_save = $("#btn-save");
    var $btn_save_as = $("#btn-save-as");
    var $save_as_input = $("#save_input");
    var $input_title = $("#input_title");
    var $input_list = $("#input_list");
    var $btn_delete = $("#btn-delete");
    var $btn_delete_ok = $("#warning_delete_input_ok");
    var $sets_list_ul = $("#sets_list_ul");
    var $inputs_in_set_list_ul = $("#inputs_in_set_list_ul");
    var $btn_add_to_set = $("#btn-add-to-set");

    var current_input_id = null;
    var current_set_id = null;
    var current_set_input_id = null;
    var data = {};

    var local = window.location.host;
    var uri = 'ws://' + local + '/input/websocket';
    console.log('Uri: ' + uri)

    var WebSocket = window.WebSocket || window.MozWebSocket;
    if (WebSocket) {
        try {
            var socket = new WebSocket(uri);
        } catch (e) {}
    }

    if (socket) {
        socket.onopen = function() {
            console.log("websocket onopen");
            $btn_clear.bind('click', function() {$('#warning_clear_input_modal').modal('show');});
            $btn_clear_ok.bind('click', clear_input);
            // $btn_save.bind('click', function() {$('#save_input_modal').modal('show');})
            $btn_save.bind('click', save_input);
            $btn_save_as.bind('click', function() {$('#save_as_input_modal').modal('show');})
            $save_as_input.bind('click', create_input);
            $btn_delete.bind('click', function() {$('#warning_delete_input_modal').modal('show');})
            $btn_delete_ok.bind('click', delete_input);
            generate_matrix(8, 8);
            generate_display_matrix(8, 8);
        };

        socket.onmessage = function(msg) {
            console.log("websocket onmessage");
            data = JSON.parse(msg.data);
            console.log(data);
            if (data.inputs) {
                $input_list_ul.empty();
                data.inputs.forEach(function (value, index, array_inputs) {
                    console.log(index + ' ' + value);
                    $input_list_ul.append(
                        '<a id="a_' + value.id + '" class="input_list_item list-group-item">' + 
                            '<p class="col-md-12 input_item_key">' + 
                                '<span id="input_num_badge" class="badge">' + (index + 1) + '</span>&nbsp' +
                                value.key + '&nbsp;' + 
                            '</p>' +
                        '</a>'
                    );
                    initInputClick(value.id);
                });
            }

            if (data.current_input_id) {
                current_input_id = data.current_input_id;
                $('a#a_' + current_input_id).attr("class","input_list_item list-group-item active");
            }

            if (data.input) {
                load_matrix(data.input.value, 8, 8);
            }

            if (data.save) {
                if (data.save == true) {
                    $('#save_input_modal').modal('show');
                } else {
                    $('#save_input_failed_modal').modal('show');
                }
            }

            if (data.sets) {
                $sets_list_ul.empty();
                data.sets.forEach(function (value, index, array_inputs) {
                    console.log(index + ' ' + value);
                    $sets_list_ul.append(
                        '<a id="as_' + value.id + '" class="input_list_item list-group-item">' + 
                            '<p class="col-md-12 input_item_key">' + 
                                '<span id="input_num_badge" class="badge">' + (index + 1) + '</span>&nbsp' +
                                value.key + '&nbsp;' + 
                            '</p>' +
                        '</a>'
                    );
                    initSetClick(value.id);
                });
            }

            if (data.current_set_id) {
                current_set_id = data.current_set_id;
                $('a#as_' + current_set_id).attr("class","input_list_item list-group-item active");
            }

            if (data.set) {
                load_set(data.set.value);
            }
        };

        socket.onclose = function() {
            console.log("websocket onclose");
            $input_area.css({'background-color' : '#CC0000'});
        };
    }


    

    function initInputClick(input_id) {
        $('a#a_' + input_id).bind("click", function () {
            var data = {};
            data['input'] = {'cmd':'select', 'input_id':input_id};
            console.log("click old_id: " + current_input_id);
            if (current_input_id != null)
                $('a#a_' + current_input_id).attr("class","input_list_item list-group-item");
            current_input_id = input_id;
            console.log("click new_id: " + current_input_id);
            $('a#a_' + current_input_id).attr("class","input_list_item list-group-item active");
            socket.send(JSON.stringify(data));
        });
    }

    function initSetClick(set_id) {
        $('a#as_' + set_id).bind("click", function () {
            var data = {};
            data['set'] = {'cmd':'select', 'set_id':set_id};
            console.log("click old_id: " + current_set_id);
            if (current_set_id != null)
                $('a#as_' + current_set_id).attr("class","input_list_item list-group-item");
            current_set_id = set_id;
            console.log("click new_id: " + current_set_id);
            $('a#as_' + current_set_id).attr("class","input_list_item list-group-item active");
            socket.send(JSON.stringify(data));
        });
    }

    function initSetInputClick(v, o) {
        var set_input_id = v.id
        $('a#as_input_' + set_input_id).bind("click", function () {
            // console.log("click!");
            if (current_set_input_id != null)
                $('a#as_input_' + current_set_input_id).attr("class","input_list_item list-group-item");
            current_set_input_id = set_input_id;
            $('a#as_input_' + current_set_input_id).attr("class","input_list_item list-group-item active");
            load_display_matrix(v.value, 8, 8);
            if (o[v.id]) {
                $("#text_output").val(JSON.stringify(o[v.id]));
            }
        });
    }

    function load_set(v) {
        var inputs = v.inputs;
        var outputs = v.outputs;
        $inputs_in_set_list_ul.empty();
        inputs.forEach(function (value, index, array_inputs) {
            console.log(index + ' ' + value);
            $inputs_in_set_list_ul.append(
                '<a id="as_input_' + value.id + '" class="input_list_item list-group-item">' + 
                    '<p class="col-md-12 input_item_key">' + 
                        '<span id="input_num_badge" class="badge">' + (index + 1) + '</span>&nbsp' +
                        value.key + '&nbsp;' + 
                    '</p>' +
                '</a>'
            );
            initSetInputClick(value, outputs);
        });
        current_set_input_id = inputs[0].id;
        $('a#as_input_' + current_set_input_id).attr("class","input_list_item list-group-item active");
        load_display_matrix(inputs[0].value, 8, 8);
        console.log("load_set");
    }

    function save_input() {
        var data = {};
        if (current_input_id != null) {
            data['input'] = {'cmd':'save', 'input_id':current_input_id, 'value':$("#text_input").val()};
            socket.send(JSON.stringify(data));
        }
    }

    function create_input() {
        var data = {};
        data['input'] = {'cmd':'create', 'key':$input_title.val(), 'value':$("#text_input").val()};
        socket.send(JSON.stringify(data));
        $input_list.scrollTop(0);
    }

    function delete_input() {
        var data = {};
        if (current_input_id != null) {
            data['input'] = {'cmd':'delete', 'current_input_id':current_input_id};
            socket.send(JSON.stringify(data));
        }
    }

    function generate_matrix(w, h) {
        for (var y=0; y<h; y++) {
            var tr = '<tr id="line">';
            for (var x=0; x<w; x++) {
                tr += '<td id="' + (y*w+x) + '" class="dot" style="height: 10px; width: 10px; padding-bottom: 1px; padding-right: 2px; padding-left: 2px; padding-top: 1px;">' + "0" + '</td>'
            }
            tr += '</tr>'
            $table_body.append(tr);
        }
        $("td.dot").bind('click', dot_click);
        get_matrix_value(8, 8)
    }

    function generate_display_matrix(w, h) {
        for (var y=0; y<h; y++) {
            var tr = '<tr id="line">';
            for (var x=0; x<w; x++) {
                tr += '<td id="' + (y*w+x) + '" class="display_dot" style="height: 10px; width: 10px; padding-bottom: 0px; padding-right: 0px; padding-left: 0px; padding-top: 0px;">' + "0" + '</td>'
            }
            tr += '</tr>'
            $table_body_display.append(tr);
        }
    }

    function load_matrix(d, w, h) {
        console.log("load: ", d)
        for (var y=0; y<h; y++) {
            for (var x=0; x<w; x++) {
                // console.log("d[", y, "]", "[", x, "]=", d[y][x])
                if (d[y][x] == "1") {
                    $("#dot_matrix_input tr td#" + (y*w+x)).text("1");
                    $("#dot_matrix_input tr td#" + (y*w+x)).css("background-color","grey")
                } else {
                    $("#dot_matrix_input tr td#" + (y*w+x)).text("0");
                    $("#dot_matrix_input tr td#" + (y*w+x)).css("background-color","white")
                }
            }
        }
        get_matrix_value(w, h)
    }

    function load_display_matrix(d, w, h) {
        console.log("load: ", d)
        for (var y=0; y<h; y++) {
            for (var x=0; x<w; x++) {
                // console.log("d[", y, "]", "[", x, "]=", d[y][x])
                if (d[y][x] == "1") {
                    $("#display_dot_matrix tr td#" + (y*w+x)).text("1");
                    $("#display_dot_matrix tr td#" + (y*w+x)).css("background-color","grey")
                } else {
                    $("#display_dot_matrix tr td#" + (y*w+x)).text("0");
                    $("#display_dot_matrix tr td#" + (y*w+x)).css("background-color","white")
                }
            }
        }
    }

    function dot_click() {
        // console.log($(this));
        if ($(this).text() == "0") {
            $(this).text("1");
            $(this).css("background-color","grey");
        } else {
            $(this).text("0");
            $(this).css("background-color","white");
        }
        get_matrix_value(8, 8);
    }

    function clear_matrix(w, h) {
        for (var y=0; y<h; y++) {
            for (var x=0; x<w; x++) {
                $("#dot_matrix_input tr td#" + (y*w+x)).text("0");
                $("#dot_matrix_input tr td#" + (y*w+x)).css("background-color","white")
            }
        }
        get_matrix_value(8, 8);
    }

    function clear_input() {
        clear_matrix(8, 8);
    }

    function get_matrix_value(w, h) {
        var r = [];
        for (var y=0; y<h; y++) {
            var l = "";
            for (var x=0; x<w; x++) {
                var v = $("#dot_matrix_input tr td#" + (y*w+x)).text();
                l += v;
                // console.log(l);
            }
            r.push(l);
        }
        $("#text_input").val(JSON.stringify(r));
        console.log(r);
    }

    
}