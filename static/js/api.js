$(document).ready(function() {
    $.ajaxSetup({
     beforeSend: function(xhr, settings) {
         function getCookie(name) {
             var cookieValue = null;
             if (document.cookie && document.cookie != '') {
                 var cookies = document.cookie.split(';');
                 for (var i = 0; i < cookies.length; i++) {
                     var cookie = jQuery.trim(cookies[i]);
                     // Does this cookie string begin with the name we want?
                     if (cookie.substring(0, name.length + 1) == (name + '=')) {
                         cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                         break;
                     }
                 }
             }
             return cookieValue;
         }
         if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
             // Only send the token to relative URLs i.e. locally.
             xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
         }
     }
});
    $(document).on("click", ".add-server", function () {
        $('.add-server').prop('disabled', true);
        $('.add-server').html('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>');
        var server_name = $("#server-name").val();
        var server_ip = $("#server-ip").val();
        var rcon_password = $("#rcon-password").val();
        var rcon_port = $("#rcon-port").val();
        $.ajax({
            url: '/add_server/',
            type: 'POST',
            data: {server_name: server_name, server_ip: server_ip, rcon_password: rcon_password, rcon_port: rcon_port, },
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
        var product_description = CKEDITOR.instances.id_product_description1.getData();
        var product_commands = $("#product_commands").val();
        var product_image = $("#product_image").val();
        var lvlup_other_price = $("#lvlup_other_price").val();
        var lvlup_sms_price = $("#lvlup_sms_price").val();
        var microsms_sms_price = $("#microsms_sms_price").val();
        $.ajax({
            url: '/add_product/',
            type: 'POST',
            data: {product_name: product_name, server_id: server_id, product_description: product_description,
                lvlup_sms_price: lvlup_sms_price, lvlup_other_price: lvlup_other_price, product_commands: product_commands,
                product_image: product_image, microsms_sms_price: microsms_sms_price, captcha: grecaptcha.getResponse()},
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
    $(document).on("click", ".add_payment_operator", function () {
        $(this).prop('disabled', true);
        $(this).html('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>');
        var server_id = $("#server_id").val();
        selected_operator = $('#select_payment_type').val();
        if (selected_operator == 'lvlup_sms') {
            var operator_name = $("#lvlup_sms_operator_name").val();
            var client_id = $("#lvlup_client_id").val();
            $.ajax({
                url: '/add_operator/lvlup_sms',
                type: 'POST',
                data: {server_id: server_id, operator_name: operator_name, client_id: client_id},
                success: function () {
                    location.reload(true);
                },
                error: function (data) {
                    toastr.error(data.responseJSON.message);
                    $('.add_payment_operator').prop('disabled', false);
                    $('.add_payment_operator').html('Dodaj');
                }
            });
        }
        else if (selected_operator == 'lvlup_other') {
            var operator_name = $("#lvlup_other_operator_name").val();
            var api_key = $('#lvlup_api_key').val();
            $.ajax({
                url: '/add_operator/lvlup_other',
                type: 'POST',
                data: {server_id: server_id, operator_name: operator_name, api_key: api_key},
                success: function () {
                    location.reload(true);
                },
                error: function (data) {
                    toastr.error(data.responseJSON.message);
                    $('.add_payment_operator').prop('disabled', false);
                    $('.add_payment_operator').html('Dodaj');
                }
            });
        }
        else if (selected_operator == 'microsms_sms') {
            var operator_name = $("#microsms_sms_operator_name").val();
            var client_id = $('#microsms_client_id').val();
            var service_id = $('#microsms_service_id').val();
            var sms_content = $('#microsms_sms_content').val();
            $.ajax({
                url: '/add_operator/microsms_sms',
                type: 'POST',
                data: {server_id: server_id, operator_name: operator_name, client_id: client_id, service_id: service_id, sms_content: sms_content},
                success: function () {
                    location.reload(true);
                },
                error: function (data) {
                    toastr.error(data.responseJSON.message);
                    $('.add_payment_operator').prop('disabled', false);
                    $('.add_payment_operator').html('Dodaj');
                }
            });
        }
    });
    $(document).on("click", ".buy_button", function () {
        var product_id = $(this).attr('product_id');
        if ($('#lvlup_sms' + product_id).is(':checked')) {
            var sms_number = $('#hiddenlvlup_sms' + product_id).val();
            $('#lvlup_modal').modal('show');
            $('.btn-success').addClass('lvlup_sms_buy_button');
            $('.btn-success').removeClass('microsms_sms_buy');
            $('.btn-success').removeClass('lvlup_other_buy_button');
            $('.lvlup-modal-body').html(`
            <p>Wyślij SMS na numer <b>` + sms_number + `</b> o treści <b>AP.HOSTMC</b>. W odpowiedzi dostaniesz kod, który wpiszesz niżej.</p>
            <input type="hidden" id="product_id_modal" value="` + product_id + `">
            <input type="hidden" id="product_sms_number_modal" value="` + sms_number + `">
            <label for="lvlup_player_nick" class="col-form-label">Nick gracza</label>
            <input type="text" name="lvlup_player_nick" class="form-control" id="lvlup_player_nick">
            <label for="lvlup_sms_code" class="col-form-label">Kod SMS</label>
            <input type="text" name="lvlup_sms_code" class="form-control" id="lvlup_sms_code">
            <p>Kupując produkt akceptujesz <a href="https://www.dotpay.pl/regulamin-serwisow-sms-premium/">regulamin płatności SMS</a>. 
            <a href="https://www.dotpay.pl/kontakt/uslugi-sms-premium/">Formularz reklamacyjny</a></p>`)
            $(".btn-success").removeClass("lvlup_other_buy_button");
            } else if ($('#lvlup_other' + product_id).is(':checked')) {
                $('#lvlup_modal').modal('show');
                $('.btn-success').addClass('lvlup_other_buy_button');
                $('.btn-success').removeClass('lvlup_sms_buy_button');
                $('.btn-success').removeClass('microsms_sms_buy');
                $('.lvlup-modal-body').html(`
                <input type="hidden" id="product_id_modal" value="` + product_id + `">
                <label for="player_nick" class="col-form-label">Nick gracza</label>
                <input type="text" name="player_nick" class="form-control" id="player_nick">`);
                $(".btn-success").removeClass("lvlup_sms_buy_button");
            } else if ($('#microsms_sms' + product_id).is(':checked')) {
                var sms_number = $('#hiddenmicrosms_sms' + product_id).val();
                var sms_content = $('#sms_microsms_content').val();
                $('.btn-success').addClass('microsms_sms_buy');
                $('.btn-success').removeClass('lvlup_sms_buy_button');
                $('.btn-success').removeClass('lvlup_other_buy_button');
                $('#microsms_modal').modal('show');
                $('.microsms-modal-body').html(`
                <p>Wyślij SMS na numer <b>` + sms_number + `</b> o treści <b>`+ sms_content +`</b>. W odpowiedzi dostaniesz kod, który wpiszesz niżej.</p>
                <input type="hidden" id="product_id_modal" value="` + product_id + `">
                <input type="hidden" id="product_sms_number_modal" value="` + sms_number + `">
                <label for="microsms_player_nick" class="col-form-label">Nick gracza</label>
                <input type="text" name="microsms_player_nick" class="form-control" id="microsms_player_nick">
                <label for="microsms_sms_code" class="col-form-label">Kod SMS</label>
                <input type="text" name="microsms_sms_code" class="form-control" id="microsms_sms_code">
                <p>Kupując produkt akceptujesz <a href="https://microsms.pl/files/regulations/">regulamin płatności SMS</a>. 
                <a href="https://microsms.pl/customer/complaint/">Formularz reklamacyjny</a></p>`)
            }
        else {
                toastr.warning('Wybierz rodzaj płatności.');
        }
    });
    $(document).on("click", ".lvlup_sms_buy_button", function () {
        $(this).prop('disabled', true);
        $(this).html('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>');
        var product_id = $('#product_id_modal').val();
        var sms_number = $('#hiddenlvlup_sms'+product_id).val();
        var player_nick = $('#lvlup_player_nick').val();
        var sms_code = $('#lvlup_sms_code').val();
        $.ajax({
            url: '/buy_sms/',
            type: 'POST',
            data: {product_id: product_id, sms_number: sms_number, player_nick: player_nick, sms_code: sms_code, payment_type: "1"},
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
    $(document).on("click", ".microsms_sms_buy", function () {
        $(this).prop('disabled', true);
        $(this).html('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>');
        var product_id = $('#product_id_modal').val();
        var sms_number = $('#hiddenmicrosms_sms'+product_id).val();
        var player_nick = $('#microsms_player_nick').val();
        var sms_code = $('#microsms_sms_code').val();
        $.ajax({
            url: '/buy_sms/',
            type: 'POST',
            data: {product_id: product_id, sms_number: sms_number, player_nick: player_nick, sms_code: sms_code, payment_type: "2"},
            success: function (data) {
                toastr.success(data.message);
                $('#lvlup_modal').modal('hide');
                $('.microsms_sms_buy').prop('disabled', false);
                $('.microsms_sms_buy').html('Kup');
            },
            error: function (data) {
                toastr.error(data.responseJSON.message);
                $('.microsms_sms_buy').prop('disabled', false);
                $('.microsms_sms_buy').html('Kup');
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
        var rcon_port = $("#rcon_port").val();
        $.ajax({
            url: '/save_settings2/',
            type: 'POST',
            data: {server_name: server_name, server_id: server_id, server_ip: server_ip, rcon_password: rcon_password, rcon_port},
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
        var server_id = $("#server_id").val();
        $.ajax({
            url: '/remove_product/',
            type: 'POST',
            data: {product_id: product_id, server_id: server_id},
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
    $(document).on("click", ".remove_payment_operator", function () {
        $(this).prop('disabled', true);
        var operator_id = $(this).attr('operator_id');
        var server_id = $("#server_id").val();
        $.ajax({
            url: '/remove_payment_operator/',
            type: 'POST',
            data: {operator_id: operator_id, server_id: server_id},
            success: function () {
                location.reload();
            },
            error: function (data) {
                toastr.error(data.responseJSON.message);
                $('.remove_payment_operator').prop('disabled', false);
            }
        });
    });
    $(document).on("click", ".open_edit_product_button", function () {
        var product_id = $(this).attr('product_id');
        var server_id = $("#server_id").val();
        $.ajax({
            url: '/api/product/'+product_id,
            type: 'GET',
            data: {server_id: server_id},
            success: function (data) {
                $('.edit_product_button').attr('product_id', product_id);
                $('#edit_product_name').val(data.product_name);
                CKEDITOR.instances.id_product_description.setData(data.product_description);
                $('#edit_lvlup_other_price').val(data.lvlup_other_price);
                $('#edit_lvlup_sms_price').val(data.lvlup_sms_number);
                $('#edit_microsms_sms_price').val(data.microsms_sms_number);
                $('#edit_product_commands').val(data.product_commands);
                $('#edit_product_image').val(data.product_image);
                $('#editProductModal').modal('show');
            },
            error: function (data) {
                toastr.error(data.responseJSON.detail);
            }
        });
    });
    $(document).on("click", ".edit_product_button", function () {
        var product_id = $(this).attr('product_id');
        var product_name = $("#edit_product_name").val();
        var product_description = CKEDITOR.instances.id_product_description.getData();
        var lvlup_other_price = $("#edit_lvlup_other_price").val();
        var lvlup_sms_price = $("#edit_lvlup_sms_price").val();
        var microsms_sms_price = $("#edit_microsms_sms_price").val();
        var product_commands = $("#edit_product_commands").val();
        var product_image = $("#edit_product_image").val();
        console.log(lvlup_sms_price);
        $.ajax({
            url: '/add_product/',
            type: 'POST',
            data: {product_id: product_id, product_name: product_name, product_description: product_description,
                   lvlup_sms_price: lvlup_sms_price, microsms_sms_price: microsms_sms_price,
                   product_commands: product_commands, product_image: product_image, edit_mode: 'True', lvlup_other_price: lvlup_other_price},
            success: function (data) {
                $('#editProductModal').modal('hide');
                toastr.success(data.message)
            },
            error: function (data) {
                toastr.error(data.responseJSON.message);
            }
        });
    });
    $(document).on("click", ".generate_voucher_button", function () {
        var product_id = $('#add_voucher_product').val();
        var server_id = $("#server_id").val();
        $.ajax({
            url: '/generate_voucher/',
            type: 'POST',
            data: {product_id: product_id, server_id: server_id},
            success: function (data) {
                $('#addVoucherModal').modal('hide');
                toastr.success(data.message)
            },
            error: function (data) {
                toastr.error(data.responseJSON.message);
            }
        });
    });
    $(document).on("click", ".use_voucher_button", function () {
        var player_nick = $('#voucher_nick').val();
        var voucher_code = $('#voucher_code').val();
        var server_id = $('#server_id').val();
        $.ajax({
            url: '/use_voucher/',
            type: 'POST',
            data: {player_nick: player_nick, voucher_code: voucher_code, server_id: server_id},
            success: function (data) {
                toastr.success(data.message)
            },
            error: function (data) {
                toastr.error(data.responseJSON.message);
            }
        });
    });
    $(document).on("click", ".castomize_site_button", function () {
        var server_id = $('#server_id').val();
        var server_logo = $('#server_logo_image').val();
        var own_css = $('#server_own_css').val();
        var shop_style = $('#shop_style').val();
        var discord_webhook = $('#discord_webhook').val();
        var admins = $('#admins').val();
        $.ajax({
            url: '/customize_website/',
            type: 'POST',
            data: {server_id: server_id, server_logo: server_logo, own_css: own_css, shop_style: shop_style, discord_webhook: discord_webhook, admins: admins},
            success: function (data) {
                toastr.success(data.message)
            },
            error: function (data) {
                toastr.error(data.responseJSON.message);
            }
        });
    });
});