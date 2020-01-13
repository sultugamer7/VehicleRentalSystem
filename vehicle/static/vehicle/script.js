// Show / hide password
function show_hide(password, fa) {
    if ($('#'+password).get(0).type == 'password') {
        $('#'+password).get(0).type = 'text';
        $('.'+fa).addClass('fa-eye-slash').removeClass('fa-eye');
    } else {
        $('#'+password).get(0).type = 'password';
        $('.'+fa).addClass('fa-eye').removeClass('fa-eye-slash');
    }
}