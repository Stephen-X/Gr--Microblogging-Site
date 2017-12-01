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
 *
 * Note: this method follows HTTP polling strategy; you'll need to repeatedly call this method in a fixed interval
 * in order to update the grumbles stream. Use updateStreamWS() for real-time communications (WebSocket).
 */
function updateStream() {
    var msgStream = $("#messages-stream");
    var lastTimeUpdated = (typeof msgStream.data("last-updated") === "undefined") ? "" : msgStream.data("last-updated");
    // get the last time the stream is updated, or empty if this data is not found (this is the first update)

    // determine the API address
    var apiUrl;
    if (view === "profile") {
        apiUrl = "/api/get-messages/profile/" + profile_username + "/" + lastTimeUpdated;
    } else if (view === "global") {
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
                    msgStream.data("isEmpty", false);
                }
                for (var i = 0; i < data.messages.length; i++) {
                    var message = data.messages[i];
                    // each message card is wrapped inside a div tag with a label attribute of its id;
                    // useful for locating existing messages
                    // Note: the advantage of setting the id explicitly rather than hiding it inside
                    // jQuery's .data() is that you can search for the message page-wide using
                    // jQuery's Attribute Equals Selector: $("div[data-grumble-id='" + id + "']")
                    var message_html = $("<div class='grumble' data-grumble-id='" + message.id + "'>" + message.html + "</div>");
                    msgStream.prepend(message_html);  // add each message HTML code to the top of the list
                }
            }
        });
}

/**
 * Update message stream in real-time with WebSockets.
 * Used in global / profile view.
 */
function updateStreamWS() {
    var msgStream = $("#messages-stream");
    var apiUrl = "/api/get-messages-stream/";
    console.log("Connecting to global stream socket");  // TODO: for debugging

    // use the WebSocket wrapper provided by Django Channels to simplify the calls
    var webSocketBridge = new channels.WebSocketBridge();
    webSocketBridge.connect(apiUrl);
    webSocketBridge.listen(function(data) {

        if (msgStream.data("isEmpty")) {  // clear that "No message" sentence
            msgStream.html("");
            msgStream.data("isEmpty", false);
        }

        if (view === "profile" && data.author !== profile_username) {
            // if this is the profile page, pass grumbles that don't belong to the
            // profile owner
            return;
        }

        var content = data.html;  // html code of the new grumble
        // search for existing grumble with the same id; replace if it exists,
        // otherwise create new
        var existingMsg = $("div[data-grumble-id='" + data.id + "']");
        if (existingMsg.length) {
            existingMsg.html(content);
        } else {
            var newMsg = $("<div class='grumble' data-grumble-id='" + data.id + "'>" + content + "</div>");
            msgStream.prepend(newMsg);
        }
    });

    // TODO: for debugging
    webSocketBridge.socket.onopen = function() { console.log("Connected to global stream socket"); }
    webSocketBridge.socket.onclose = function() { console.log("Disconnected to global stream socket"); }
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
    $("#msg-sent-btn").click(postMessage);
    var autofocusField = $("#autofocus_field");
    autofocusField.keypress(function(event) {
        // also post message when user presses enter key in the input field
        if (event.which === 13) {  // 13 represents enter key press
            postMessage();
        }
    });
    $("#messages-stream").data("isEmpty", true);  // initially, the message stream doesn't contain any messages

    updateStream();  // view is a parameter indicating if this is global / follower view passed in from the template
    autofocusField.focus();  // same as adding autofocus attribute to the element


    if (view !== "following") {
        // update stream in real-time using WebSocket
        updateStreamWS();
    } else {
        // periodically update the stream every 5s
        // Note: HTTP Polling is used instead for the following page, because checking whether every
        // new grumble is made by an author followed by the current user requires database searching;
        // this will not scale well in real life where we have lots of new grumbles posted every second.
        // The idea of creating a message group for each user which will be subscribed by all of his / her
        // followers does not seem to scale well either, as many groups maintained on the server will
        // definitely consume a large amount of resources.
        // TODO: new plausible solution: query and store usernames of all following users in a set; use it to filter
        // message stream locally.
        window.setInterval(function(){
            updateStream();
        }, 5000);
    }


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
