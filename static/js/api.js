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
        $.ajax({
            url: '/add_product/',
            type: 'POST',
            data: {product_name: product_name, server_id: server_id, product_description: product_description,
                product_price: product_price, product_sms_price: product_sms_price},
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
});