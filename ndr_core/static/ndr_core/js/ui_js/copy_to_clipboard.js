/**
 * Copy the text of a given element to the clipboard
 * @param elemId Id of the element to copy
 */
function copyToClipboard(elemId) {
    let target = $( "[id='copyTarget_"+elemId+"']" );
    navigator.clipboard.writeText(target.text());
    notification("Copied to clipboard", 1000, elemId);

  }

/**
 * Display a notification
 * @param s String to display
 * @param time Time to display for (in ms)
 * @param elemId Id of the element to display the notification for
 */
function notification(s, time, elemId) {
    let target = $( "[id='copyNotification_"+elemId+"']" );
    $("<span>" + s + "</span>").appendTo(target).fadeTo(time, 1, function() {
        $(this).fadeTo(1000, 0, function() {
          $(this).remove()
        });
    });
}

/**
 * Call the url and display a notification
 * @param url Url to call
 * @param elemId Id of the element to display the notification for
 */
function callUrl(url, elemId) {
    fetch(url);
    notification("Marked For Correction", 1000, elemId);
}