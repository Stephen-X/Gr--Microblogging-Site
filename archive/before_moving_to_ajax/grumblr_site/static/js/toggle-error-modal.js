/**
 * A jQuery script used to toggle the bootstrap modal used for
 * displaying error messages. It also allows users to dismiss
 * the modal with any key presses.
 *
 * @author Stephen Xie <[redacted]@cmu.edu>
 */

// show the error modal
$('#error_modal').modal('show');

// when modal is shown, disable autofocus in the input
// field; users will not be able to type in anything in
// the background until they dismiss the modal
$('#error_modal').on('shown.bs.modal', function () {
    $('#autofocus_field').blur();
});

// on any key press by the user, dismiss the error modal
$(document).keypress(function () {
    $('#error_modal').modal('hide');
});

// after user dismiss the modal, re-enable autofocus in
// the input field and close the temporary event listener
$('#error_modal').on('hidden.bs.modal', function () {
    $('#autofocus_field').focus();
    $(document).off('keypress');
});
