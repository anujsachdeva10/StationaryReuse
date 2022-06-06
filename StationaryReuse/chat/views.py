from django.shortcuts import render
from chat.models import Thread, ThreadManager
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User


# Create your views here.

# This function is used to view the inbox of the user.
@login_required
def message_inbox(request):
    # by_user is defined in models in ThreadManager. This query gets us all the threads in which the user is participating.
    # We need to note that byuser gives only the threads but we need the chatmessages associated to the threads as well. We get
    # them using prefetch_related.
    threads = Thread.objects.by_user(user = request.user).prefetch_related('chatmessage_thread').order_by('timestamp')
    context = {
        'Threads' : threads
    }
    return render(request, 'chat/messages.html', context)

# This function is used when the user initiates a chat for the first time with another user.
@login_required
def text_person(request, receiver_id):
    sender = User.objects.get(pk = request.user.pk)
    receiver = User.objects.get(pk = receiver_id)
    print (sender, receiver)
    context = {}
    first_query = Thread.objects.filter(first_person = sender, second_person = receiver)
    second_query = Thread.objects.filter(first_person = receiver, second_person = sender)
    if (first_query.exists()):
        context = {
            'Threads' : first_query
        }
    elif (second_query.exists()):
        context = {
            'Threads' : second_query
        }
    else:
        print ("creating new thread")
        Thread.objects.create(first_person = sender, second_person = receiver)
        context = {
            'Threads' : Thread.objects.filter(first_person = sender, second_person = receiver)
        }
    return render(request, 'chat/messages.html', context)