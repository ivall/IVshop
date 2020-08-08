toastr.options = {
	"closeButton": true,
	"debug": false,
	"newestOnTop": true,
	"progressBar": true,
	"positionClass": "toast-top-right",
	"preventDuplicates": true,
	"onclick": null,
	"showDuration": "300",
	"hideDuration": "1000",
	"timeOut": "5000",
	"extendedTimeOut": "1000",
	"showEasing": "swing",
	"hideEasing": "linear",
	"showMethod": "fadeIn",
	"hideMethod": "fadeOut"
};

$(function () {
  $('[data-toggle="tooltip"]').tooltip();
});
$(document).on('show.bs.modal', '#addOperatorModal', function (e) {
    first_operator = $('#select_payment_type').val();
    first_operator = first_operator + '_selected';
	$('.'+first_operator).css('display', 'block');
});
$('#select_payment_type').on('change', function() {
  if (this.value == 'lvlup_sms') {
  	$('.lvlup_sms_selected').css('display', 'block');
  	$('.lvlup_other_selected').css('display', 'none');
	$('.microsms_sms_selected').css('display', 'none');
  }
  else if (this.value == 'lvlup_other') {
  	$('.lvlup_sms_selected').css('display', 'none');
  	$('.lvlup_other_selected').css('display', 'block');
	$('.microsms_sms_selected').css('display', 'none');
  }
  else if (this.value == 'microsms_sms') {
  	$('.lvlup_sms_selected').css('display', 'none');
  	$('.lvlup_other_selected').css('display', 'none');
	$('.microsms_sms_selected').css('display', 'block');
  }
});