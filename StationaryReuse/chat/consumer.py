import json
from channels.consumer import AsyncConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import Thread, ChatMessage

User = get_user_model()

chat_rooms_present = []

# This is the consumer which will be connected to the websocket from the frontend.
class ChatConsumer(AsyncConsumer):

    # Like web servers the consumers also have some default methods which we need to override.
    # Following are the 3 functions: connect, receive, disconnect.
    # This method will be called when the connection is established b/w the backend and the frontend.
    async def websocket_connect(self, event):
        print ('connected', event)
        # Here we are getting the logged in user.
        user = self.scope['user']
        chat_room = f'user_chatroom_{user.id}'
        self.chat_room = chat_room
        # Here, we are adding every user channel with the chatroom to keep the record.
        await self.channel_layer.group_add(
            chat_room,
            self.channel_name
        )
        print(self.channel_name, chat_room)
        # Here we are accepting the connection from the frontend to the backend. We need to accept the connection such that both the consumer and websocket are working.
        # If we do not accept the connection the consumer will connect and then just disconnect.
        await self.send({
            'type' : 'websocket.accept'
        })

    # This method will be called when the frontend sends some data to the backend and from here we can send the data back to the frontend where the onmessage function will
    # be triggered.
    async def websocket_receive(self, event):
        print ('receive', event)
        # Since we have got the data into JSON format we will convert into python dictionary using JSON.loads() method.
        received_data = json.loads(event['text'])
        # getting all the required data and validating it.
        msg = received_data.get('message')
        sent_by_id = received_data.get('sent_by')
        sent_to_id = received_data.get('send_to')
        thread_id = received_data.get('thread_id')

        if not msg:
            print ("Error: Empty message")
            return False
        
        sent_by_user = await self.get_user_object(sent_by_id)
        sent_to_user = await self.get_user_object(sent_to_id)
        thread_obj = await self.get_thread(thread_id)
        if not sent_by_user:
            print('Error: sent by user is incorrect')
        if not sent_to_user:
            print("Error: sent to user is incorrect")
        if not thread_obj:
            print("Error: Thread id is incorrect")


        await self.create_chat_message(thread_obj, sent_by_user, msg)

        # Getting the user id of the receiver to get the chatroom and thus the channels.
        other_user_chat_room = f'user_chatroom_{sent_to_id}'
        self_user = self.scope['user']
        response = {
            'message' : msg,
            'sent_by' : self_user.id,
            'sent_to' : sent_to_id,
            'thread_id' : thread_id
        }

        # Sending the message to the receiver. This will invoke the onmessage function of JS on receiver side.
        await self.channel_layer.group_send (
            other_user_chat_room,
            {
                'type' : 'chat_message',    # This is function defined below.
                # Json.dumps is used to convert the python dictionary into JSON string.
                'text' : json.dumps(response)
            }
        )

        # Sending the message to the sender. This will invoke the onmessage function of JS on the sender side.
        await self.channel_layer.group_send (
            self.chat_room,
            {
                'type' : 'chat_message',
                'text' : json.dumps(response)
            }
        )

        # await self.send({
        #     'type' : 'websocket.send',
        #     'text' : json.dumps(response)
        # })
    
    # Finally this method is called when we want to abort the connection.
    async def websocket_disconnect(self, event):
        print ('disconnect', event)

    # The dictionary sent from the channel_layer.send is the event here.
    async def chat_message(self, event):
        print("chat_message", event)
        await self.send({
            'type' : 'websocket.send',
            'text' : event['text']
        })

    # Here, we are using this decorator to get the connection closed securely.
    @database_sync_to_async
    def get_user_object(self, user_id):
        qs = User.objects.filter(id = user_id)
        if qs.exists():
            obj  = qs.first()
        else:
            obj = None
        return obj

    # This function is used to get the thread using the thread id. We need the thread id to append the new message into it.
    @database_sync_to_async
    def get_thread(self, thread_id):
        qs = Thread.objects.filter(id = thread_id)
        if qs.exists():
            obj  = qs.first()
        else:
            obj = None
        return obj

    # This function is used to insert the message into the database. Here, we need the user argument to check which of the two users in the thread sent the message.
    @database_sync_to_async
    def create_chat_message(self, thread, user, msg):
        qs = ChatMessage.objects.create(thread=thread, user = user, message = msg)

    