from django.contrib import admin
from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Q
from . models import Thread, ChatMessage

# First we need to register this model.
admin.site.register(ChatMessage)

# Once we have registered the model then we will have to make the class inline for us to add the messages to the thread form the admin site.
class ChatMessage(admin.TabularInline):
    model = ChatMessage

# This class provide validations such that if there exists a thread between two user we are not able to create another thread between them.
# class ThreadForm(forms.ModelForm):
#     def clean(self):
#         super(ThreadForm, self).clean()
#         first_person = self.cleaned_data.get('first_person')
#         second_person = self.cleaned_data.get('second_person')

#         lookup1 = Q(first_person = first_person) & Q(second_person = second_person)
#         lookup2 = Q(first_person = second_person) & Q(second_person = first_person)
#         lookup = Q(lookup1 | lookup2)
#         qs = Thread.objects.filter(lookup)
#         if qs.exists():
#             raise ValidationError(f'Thread between {first_person} and {second_person} already exists')


# Here we are writing a function with the help of which we will be able to create a thread and add messages to it from the admin itself.
class ThreadAdmin(admin.ModelAdmin):
    inlines = [ChatMessage]
    class Meta:
        model = Thread

# Register your models here.

admin.site.register(Thread, ThreadAdmin)
