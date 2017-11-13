/**
 * Main logic for comment posting.
 * Notes: Must load jQuery library before executing this program.
 *
 * @author Stephen Xie <[redacted]@cmu.edu>
 */

/**
 * Post new comment to the backend, and update the frontend template respectively.
 */
function postComment(event) {
    var messageCard = $(event.target).parents(".msg-card");
    var input_field = $(event.target).parents(".input-group").find("input");
    var msg_id = messageCard.data("message-id");
    // find the target comment submit button that user clicked, then find its belonging message card,
    // and retrieve the message id data
    if (input_field.val()) {  // if use did input something, send the post request
        $.post("/api/post-comment/" + msg_id + "/", {"content": input_field.val()})
            .done(function() {
                // clear the old input
                input_field.val("");
                // update the comment list
                getComments(messageCard)
            });
    }
}

/**
 * Get all comments for the given message.
 * TODO: only gets the latest comments, like message updating.
 *
 * @param messageCard element with the .msg-card class
 */
function getComments(messageCard) {
    var msg_id = messageCard.data("message-id");
    var commentList = messageCard.find(".comment-list");
    // get the last time this comment list is updated
    var lastTimeUpdated = (typeof commentList.data("last-updated") === "undefined") ? "" : commentList.data("last-updated");

    $.get("/api/get-comments/" + msg_id + "/" + lastTimeUpdated)
        .done(function(data) {
            commentList.data("last-updated", data["last_updated"]);  // update last updated time with data from backend API
            if (!lastTimeUpdated) {
                // clear the list if lastTimeUpdated is not recorded before; this avoids duplicate comment addition
                commentList.html("");
            }
            for (var i = 0; i < data.comments.length; i++) {
                commentList.append(data.comments[i]);  // add each comment HTML code to the end of the list
            }
        });
}

/**
 * Initializations after the page is loaded.
 */
$(document).ready(function() {
    $(document).on("click", ".comment-sent-btn", postComment);
    $(document).on("keypress", ".comment-input", function(event) {
        // also post comment when user presses enter key in the input field
        if (event.which == 13) {  // 13 represents enter key press
            postComment(event);
        }
    });

    // -- pass CSRF token in every POST request using jQuery ----------------------
    // source: https://docs.djangoproject.com/en/1.11/ref/csrf/#ajax

    // acquire the token
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    var csrftoken = getCookie('csrftoken');
    // then set the token on the AJAX request
    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

    // -------------------------------------------------------------------------------
});
