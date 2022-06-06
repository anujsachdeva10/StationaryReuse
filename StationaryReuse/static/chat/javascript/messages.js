let input_message = $('#input-message')
let message_body = $('.msg_card_body')
let send_message_form = $('#send-message-form')
// Id of the logged in user.
let USER_ID = $('#logged-in-user').val()

// Here, we will get the info of the current window and get the endpoint where the wensockets listen.
let loc = window.location
let wsStart = 'ws://'

if (loc.protocal == 'https') {
    wsStart = 'wss://'
}
let endpoint = wsStart + loc.host + loc.pathname

// The point is we will get the message from the front-end to get it to the backend for saving and other functions
// we need to create socket which will help us to receive the data from the front end and send the data to the backend.
var socket = new WebSocket(endpoint)

// Every web socket has 4 events: onopen, onmessage, onerror, onclose and we need to override these functions.

// This message will be called whenever a socket is created on the frontend.
socket.onopen = async function(e) {
    console.log('open', e)
    // This event listener is called when we want to send some data from the webpage. With this we send the data from the 
    // frontend to the backend and in the consumer the receive function will get triggered which will then return some data.
    send_message_form.on('submit', function(e) {
        e.preventDefault()
        // Here, we are getting the necessary details to get the data stored in the models.
        let message = input_message.val()
        let send_to = get_active_other_user_id();
        let thread_id = get_active_thread_id();
        let data = {
            'message' : message,
            'sent_by' : USER_ID,
            'send_to' : send_to,
            'thread_id' : thread_id
        }
        // This function converts the javascipt object into JSON string.
        data = JSON.stringify(data)
        socket.send(data)
        $(this)[0].reset()
    })
}

// This function is called whenever the backend sends some message to the frontend.
socket.onmessage = async function(e) {
    console.log('message', e)
    // JSON.parse is used to convert a JSON string into a javascript object.
    let data = JSON.parse(e.data)
    let message = data['message']
    let sent_by_id = data['sent_by']
    let thread_id = data['thread_id']
    newMessage(message, sent_by_id, thread_id)
}

// This function is called when an error occur while establishing the connection.
socket.onerror = async function(e) {
    console.log('open', e)
}

// This function is called when we are about to close the socket.
socket.onclose = async function(e) {
    console.log('close', e)
}

// This message is called when we receive the message from the backend to the frontend to add the message to the user screen.
function newMessage(message, sent_by_id, thread_id) {
    if ($.trim(message) === '') {
        return false;
    }
    let message_element = ``;
    let chat_id = 'chat_' + thread_id
    // The below parameters are taken to display the dp properly. We assume that the first_person_dp is always the sender dp and hence if the sender is the second person we swap the dp's.
    let first_person_dp = $('#first_user_dp').val()
    let first_person_id = $('#first_user_id').val()
    let second_person_dp = $('#second_user_dp').val()
    let second_person_id = $('#second_user_id').val()
    // This is for the allignment purpose if the user is the sender then then message appears on R.H.S. else on L.H.S.
    // Here, we see one flaw in the logic if we only use if else construct the flaw is that once we sent the message for the sender the message will
    // get appended to the right of the screen but for all the rest of the users it will get appended to the left of the screen but we want that only the
    // receiver gets the message.
    if (USER_ID == second_person_id) {
        let temp = first_person_dp
        first_person_dp = second_person_dp
        second_person_dp = temp
    }
    if (sent_by_id == USER_ID) {
        message_element = `
            <div class = "d-flex mb-4 replied"> 
                <div class = "msg_cotainer_send">
                    ${message}
                    <span class = "msg_time_send"> 5A.M.</span>
                </div>
                <div class = "img_cont_msg">
                    <img src = "${first_person_dp}" alt = "something" class="rounded-circle user_img_msg">
                </div>
            </div>
        `   
    }
    else {
        message_element = `
            <div class = "d-flex mb-4 received"> 
                <div class = "img_cont_msg">
                    <img src = "${second_person_dp}" alt = "something" class="rounded-circle user_img_msg">
                </div>
                <div class = "msg_cotainer">
                    ${message}
                    <span class = "msg_time"> 8:40A.M.</span>
                </div>
            </div>
        `
    }
    // To resolve the issue we have used chat-id parameter. We will grab the body for only those chats which have the same chat-id and append the messages to them.
    let message_body = $('.messages-wrapper[chat-id="' + chat_id + '"] .msg_card_body')
    message_body.append($(message_element))
    message_body.animate({
        scrollTop : $(document).height()
    }, 100)
    input_message.val(null)
}

// This event is used to make the chat list clickable. So, whenever we click on the contact all the messages of that contact are loaded. 
$('.contact-li').on('click', function () {
    $('.contacts .active').removeClass('active')
    $(this).addClass('active')

    // message wrappers
    let chat_id = $(this).attr('chat-id')
    $('.messages-wrapper.is_active').removeClass('is_active')
    $('.messages-wrapper[chat-id="' + chat_id + '"]').addClass('is_active')
})

// This is used to return the id of the receiver. We have created div where in we have added the receiver id as an attr. which we can access here.
function get_active_other_user_id() {
    let other_user_id = $('.messages-wrapper.is_active').attr('other-user-id')
    other_user_id = $.trim(other_user_id)
    return other_user_id
}

// This is used to return the thread id. Basically the chat id is chat_(thread.id). So, we remove chat_ prefix from the chat-id attr.
function get_active_thread_id() {
    let chat_id = $('.messages-wrapper.is_active').attr('chat-id')
    let thread_id = chat_id.replace('chat_', '')
    return thread_id
}