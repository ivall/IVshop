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

$('#select_payment_type').on('change', function() {
  if (this.value == 1) {
  	$('.lvlup_selected').css('display', 'block');
	$('.microsms_selected').css('display', 'none');
  }
  else if (this.value == 2) {
  	$('.lvlup_selected').css('display', 'none');
  	$('.microsms_selected').css('display', 'block')
  }
});