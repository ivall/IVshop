$(document).ready(function() {
    $(document).on("click", ".add-server", function () {
        $('.add-server').prop('disabled', true);
        $('.add-server').html('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>');
        var server_name = $("#server-name").val();
        var server_ip = $("#server-ip").val();
        var rcon_password = $("#rcon-password").val();
        $.ajax({
            url: '/add_server/',
            type: 'POST',
            data: {server_name: server_name, server_ip: server_ip, rcon_password: rcon_password},
            success: function (data) {
                $(".server-ip").val("");
                toastr.success(data.message);
                $('#addServerModal').modal('hide');
                $('.add-server').prop('disabled', false);
                $('.add-server').html('Dodaj');
            },
            error: function (data) {
                toastr.error(data.responseJSON.message);
                $('.add-server').prop('disabled', false);
                $('.add-server').html('Dodaj');
            }
        });
    });
    $(document).on("click", ".add_product_button", function () {
        $('.add_product_button').prop('disabled', true);
        $('.add_product_button').html('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>');
        var server_id = $("#server_id").val();
        var product_name = $("#product_name").val();
        var product_description = $("#product_description").val();
        var product_price = $("#product_price").val();
        var product_sms_price = $("#product_sms_price").val();
        var product_commands = $("#product_commands").val();
        $.ajax({
            url: '/add_product/',
            type: 'POST',
            data: {product_name: product_name, server_id: server_id, product_description: product_description,
                product_price: product_price, product_sms_price: product_sms_price, product_commands: product_commands},
            success: function (data) {
                toastr.success(data.message);
                $('#addProductModal').modal('hide');
                $('.add_product_button').prop('disabled', false);
                $('.add_product_button').html('Dodaj');
            },
            error: function (data) {
                toastr.error(data.responseJSON.message);
                $('.add_product_button').prop('disabled', false);
                $('.add_product_button').html('Dodaj');
            }
        });
    });
    $(document).on("click", ".save-settings", function () {
        $('.save-settings').prop('disabled', true);
        $('.save-settings').html('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>');
        var payment_type = $("#select_payment_type").val();
        var server_id = $("#server_id").val();
        var client_id = $("#lvlup_client_id").val();
        var api_key = $("#lvlup_api_key").val();
        $.ajax({
            url: '/save_settings/',
            type: 'POST',
            data: {payment_type: payment_type, server_id: server_id, client_id: client_id, api_key: api_key},
            success: function (data) {
                $("#lvlup_client_id").val("");
                $("#lvlup_api_key").val("");
                toastr.success(data.message);
                $('#settingsModal').modal('hide');
                $('.save-settings').prop('disabled', false);
                $('.save-settings').html('Zapisz');
            },
            error: function (data) {
                toastr.error(data.responseJSON.message);
                $('.save-settings').prop('disabled', false);
                $('.save-settings').html('Zapisz');
            }
        });
    });
    $(document).on("click", ".buy_button", function () {
        var product_id = $(this).attr('product_id');
        var sms_number = $('#sms_lvlup_number'+product_id).val();
        if($('#sms_lvlup'+product_id).is(':checked')) {
            $('#lvlup_modal').modal('show');
            $('.btn-success').addClass('lvlup_sms_buy_button');
            $('.modal-body').html(`
            <p>Wyślij SMS na numer <b>`+sms_number+`</b> o treści <b>AP.HOSTMC</b></p>
            <input type="hidden" id="product_id_modal" value="`+product_id+`">
            <input type="hidden" id="product_sms_number_modal" value="`+sms_number+`">
            <label for="player_nick" class="col-form-label">Nick gracza</label>
            <input type="text" name="player_nick" class="form-control" id="player_nick">
            <label for="sms_code" class="col-form-label">Kod SMS</label>
            <input type="text" name="sms_code" class="form-control" id="sms_code">`)
        }
        else if($('#other_lvlup'+product_id).is(':checked')) {
            $('#lvlup_modal').modal('show');
            $('.btn-success').addClass('lvlup_other_buy_button');
            $('.modal-body').html(`
            <input type="hidden" id="product_id_modal" value="`+product_id+`">
            <label for="player_nick" class="col-form-label">Nick gracza</label>
            <input type="text" name="player_nick" class="form-control" id="player_nick">`)
        }
    });
    $(document).on("click", ".lvlup_sms_buy_button", function () {
        $(this).prop('disabled', true);
        $(this).html('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>');
        var product_id = $('#product_id_modal').val();
        var sms_number = $('#product_sms_number_modal').val();
        var player_nick = $('#player_nick').val();
        var sms_code = $('#sms_code').val();
        $.ajax({
            url: '/buy_sms/',
            type: 'POST',
            data: {product_id: product_id, sms_number: sms_number, player_nick: player_nick, sms_code: sms_code},
            success: function (data) {
                toastr.success(data.message);
                $('#lvlup_modal').modal('hide');
                $('.lvlup_sms_buy_button').prop('disabled', false);
                $('.lvlup_sms_buy_button').html('Kup');
            },
            error: function (data) {
                toastr.error(data.responseJSON.message);
                $('.lvlup_sms_buy_button').prop('disabled', false);
                $('.lvlup_sms_buy_button').html('Kup');
            }
        });
    });
    $(document).on("click", ".lvlup_other_buy_button", function () {
        $(this).prop('disabled', true);
        $(this).html('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>');
        var product_id = $('#product_id_modal').val();
        var player_nick = $('#player_nick').val();
        $.ajax({
            url: '/buy_other/',
            type: 'POST',
            data: {product_id: product_id, player_nick: player_nick},
            success: function (data) {
                window.location.replace(data.message);
            },
            error: function (data) {
                toastr.error(data.responseJSON.message);
                $('.lvlup_other_buy_button').prop('disabled', false);
                $('.lvlup_other_buy_button').html('Kup');
            }
        });
    });
    $(document).on("click", ".save-settings2", function () {
        $('.save-settings2').prop('disabled', true);
        $('.save-settings2').html('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>');
        var server_name = $("#server_name").val();
        var server_id = $("#server_id").val();
        var server_ip = $("#server_ip").val();
        var rcon_password = $("#rcon_password").val();
        $.ajax({
            url: '/save_settings2/',
            type: 'POST',
            data: {server_name: server_name, server_id: server_id, server_ip: server_ip, rcon_password: rcon_password},
            success: function (data) {
                $("#rcon_password").val("");
                $("#server_name").val(server_name);
                $("#server_ip").val(server_ip);
                toastr.success(data.message);
                $('#settings2Modal').modal('hide');
                $('.save-settings2').prop('disabled', false);
                $('.save-settings2').html('Zapisz');
            },
            error: function (data) {
                toastr.error(data.responseJSON.message);
                $('.save-settings2').prop('disabled', false);
                $('.save-settings2').html('Zapisz');
            }
        });
    });
    $(document).on("click", ".remove_product", function () {
        $(this).prop('disabled', true);
        var product_id = $(this).attr('product_id');
        $.ajax({
            url: '/remove_product/',
            type: 'POST',
            data: {product_id: product_id},
            success: function (data) {
                toastr.success(data.message);
                $('.product'+product_id).remove();
                $('.remove_product').prop('disabled', false);
            },
            error: function (data) {
                toastr.error(data.responseJSON.message);
                $('.remove_product').prop('disabled', false);
            }
        });
    });
    $(document).on("click", ".open_edit_product_button", function () {
        var product_id = $(this).attr('product_id');
        $.ajax({
            url: '/product_info/',
            type: 'GET',
            data: {product_id: product_id},
            success: function (data) {
                $('.edit_product_button').attr('product_id', product_id);
                $('#edit_product_name').val(data.product_name);
                $('#edit_product_description').val(data.product_description);
                $('#edit_product_price').val(data.price);
                $('#edit_product_sms_price').val(data.sms_number);
                $('#edit_product_commands').val(data.commands);
                $('#editProductModal').modal('show');
            },
            error: function (data) {
                toastr.error(data.responseJSON.message);
            }
        });
    });
    $(document).on("click", ".edit_product_button", function () {
        var product_id = $(this).attr('product_id');
        var product_name = $("#edit_product_name").val();
        var product_description = $("#edit_product_description").val();
        var product_price = $("#edit_product_price").val();
        var product_sms_price = $("#edit_product_sms_price").val();
        var product_commands = $("#edit_product_commands").val();
        $.ajax({
            url: '/add_product/',
            type: 'POST',
            data: {product_id: product_id, product_name: product_name, product_description: product_description,
                   product_price: product_price, product_sms_price: product_sms_price,
                   product_commands: product_commands, edit_mode: 'True'},
            success: function (data) {
                $('#editProductModal').modal('hide');
                toastr.success(data.message)
            },
            error: function (data) {
                toastr.error(data.responseJSON.message);
            }
        });
    });
});