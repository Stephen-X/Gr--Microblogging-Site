/**
 * Main logic for grumble posting and auto-refreshing.
 * Notes: Must load jQuery library before executing this program.
 *
 * @author Stephen Xie <[redacted]@cmu.edu>
 */

var thisScript = document.getElementById("grumbles-ctrl");
// which view does this script operates on ("global", "following" or "profile")?
var view = thisScript.getAttribute("data-view").toLowerCase();
// if this is the profile page, what's the ID of the user to which this page belongs?
var profile_username = thisScript.getAttribute("data-user");

/**
 * Post new message to the backend, and update the frontend template with the latest messages.
 * Note: message posting is currently allowed only in global stream page.
 */
function postMessage() {
    var newMessage = $("#autofocus_field");  // input field from the message send box in grumble_stream
    $.post("/api/post-message/", {"message": newMessage.val()})
        .done(function() {
            // add 1 to the total grumbles counter
            modifyTotalGrumbles(1);

            updateStream();  // update the message stream
            // clear previous input content, then autofocus on input field again
            newMessage.val("");
            newMessage.focus();
        });
}


/**
 * Update the stream to keep up with the latest changes.
 */
function updateStream() {
    var msgStream = $("#messages-stream");
    var lastTimeUpdated = (typeof msgStream.data("last-updated") === "undefined") ? "" : msgStream.data("last-updated");
    // get the last time the stream is updated, or empty if this data is not found (this is the first update)

    // determine the API address
    var apiUrl;
    if (view == "profile") {
        apiUrl = "/api/get-messages/profile/" + profile_username + "/" + lastTimeUpdated;
    } else if (view == "global") {
        apiUrl = "/api/get-messages/global/" + lastTimeUpdated;
    } else {
        apiUrl = "/api/get-messages/follower/" + lastTimeUpdated;
    }

    // then make the connection!
    $.get(apiUrl)
    // this will return a list of messages that range from lastTimeUpdated (or the default starting time if it's
    // empty; excluded value) to current time
        .done(function(data) {
            msgStream.data("last-updated", data["last_updated"]);  // update last updated time with data from backend API
            if (data.messages.length <= 0 && msgStream.data("isEmpty")) {
                msgStream.html("<p>No message has been posted yet.</p>");

            } else {
                if (msgStream.data("isEmpty")) {  // clear that "No message" sentence
                    msgStream.html("");
                }
                msgStream.data("isEmpty", false);
                for (var i = 0; i < data.messages.length; i++) {
                    var message = data.messages[i];
                    var message_html = $(message.html);
                    message_html.data("message-id", message.id);  // each message element is labeled with its id
                    msgStream.prepend(message_html);  // add each message HTML code to the top of the list
                }
            }
        });
}

/**
 * Modify the total grumbles counter in template dynamically.
 *
 * Note: this is just a convenient hack to increment the counter when the page is not refreshed;
 * it does not reflect the latest status in the database.
 */
function modifyTotalGrumbles(amount) {
    var totalGrumbles = $("#total-grumbles");
    var oldCount = parseInt(totalGrumbles.text(), 10);
    totalGrumbles.html(oldCount + amount);
}

/**
 * Initializations after the page is loaded.
 */
$(document).ready(function() {
    // add event-handlers
    $('#msg-sent-btn').click(postMessage);
    $('#autofocus_field').keypress(function(event) {
        // also post message when user presses enter key in the input field
        if (event.which == 13) {  // 13 represents enter key press
            postMessage();
        }
    });
    $("#messages-stream").data("isEmpty", true);  // initially, the message stream doesn't contain any messages

    updateStream();  // view is a parameter indicating if this is global / follower view passed in from the template
    $('#autofocus_field').focus();  // same as adding autofocus attribute to the element

    // periodically update the stream every 10s
    window.setInterval(function(){
        updateStream();
    }, 10000);

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
