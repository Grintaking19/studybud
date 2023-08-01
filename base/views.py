from django.shortcuts import render, redirect
from  django.contrib.auth.models import User
from .models import Room, Topic, Message
from .form import RoomForm, MessageForm, UserForm
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm




def loginPage(request):

    page = 'login'
    # if the user is already logged in then redirect him to home page
    # so he can't access login page
    if (request.user.is_authenticated):
        return redirect('home')

    if (request.method == 'POST'):
        # 1- first we get the username and password from the request.POST
        username = request.POST.get('username')
        password = request.POST.get('password')

        # 2- then we check if the user exists in the database
        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request= request, message='Username does not exist')
        
        # 3- if user exists then authenticate the user
        user = authenticate(request, username=username, password=password)

        # 4- if the authentication is right then login by creating session for him using login function
        if user is not None:
            login(request, user)
            return redirect('home')
        # 5- if the authentication is wrong then show error message
        else: 
            messages.error(request= request, message='Username OR password is incorrect')

    context = {'page': page}
    return render (request, 'base/login_register.html', context)

def logoutUser(request):
    logout(request)
    return redirect('home')

def registerPage(request):
    page = 'register'
    form = UserCreationForm()
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username 
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'An error has occurred during registration')
    return render (request, 'base/login_register.html', context={'page': page, 'form': form})


def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    rooms = Room.objects.filter(
        Q(topic__name__icontains= q) 
        | Q(name__icontains= q)
        | Q(description__icontains= q)
        
        )
    
    room_count = rooms.count()
    messages = Message.objects.filter(Q(room__topic__name__icontains= q) | Q(room__name__icontains= q) | Q(user__username__icontains= q))    
    topics = Topic.objects.all()
    context = {'rooms': rooms, 'topics': topics, 'room_count': room_count, 'messages': messages}
    return render(request, 'base/home.html', context)

def room(request, pk):
    room = Room.objects.get(id=pk)
    messages = room.message_set.all().order_by('created') # get all messages of the room and order them by created date, Note: room is field in Message model, not vice versa.
    participants = room.participants.all()


    if request.method == 'POST':
        message = request.POST.get('body')
        Message.objects.create(
            user = request.user,
            room = room,
            body = message
        )
        room.participants.add(request.user)
        return redirect('room', pk=room.id)

    context = {'room': room, 'messages': messages, 'participants': participants}
    return render(request, 'base/room.html', context)

@login_required(login_url = 'login')
def createRoom(request):
    form  = RoomForm()
    topics = Topic.objects.all()
    if (request.method == 'POST'):
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        print('Post Request: ',request.POST)
        Room.objects.create(
            host = request.user,
            topic = topic,
            name = request.POST.get('name'),
            description = request.POST.get('description')
        )
        return redirect('home')


    context = {'form': form, 'topics': topics}
    return render(request, 'base/room_form.html', context)

@login_required(login_url = 'login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()
    # check if the user is the host of the room, if not then send redirect him to page contains error message
    # so if user is not the host then he can't update the room
    if request.user != room.host:
        return HttpResponse('You are not allowed here!')

    if (request.method == 'POST'):
        print('Patch Request: ',request.POST)
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.description = request.POST.get('description')
        room.topic = topic
        room.save()
        return redirect('home')

    context = {'form': form, 'topics': topics, 'room': room}
    return render(request, 'base/room_form.html', context)

@login_required(login_url = 'login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)

    # check if the user is the host of the room, if not then send redirect him to page contains error message
    # so if user is not the host then he can't delete the room
    if request.user != room.host:
        return HttpResponse('You are not allowed here!')

    if (request.method == 'POST'):
        room.delete()
        return redirect('home')

    context = {'obj': room}
    return render(request, 'base/delete.html', context)


@login_required(login_url = 'login')
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)
    
    if request.user != message.user:
        return HttpResponse('You are not allowed here!')

    if request.method == 'POST':
        message.delete()
        return redirect('delete-message', pk=message.id)

    return render(request, 'base/delete.html', context={'obj': message})


@login_required(login_url = 'login')
def updateMessage(request, pk):
    message = Message.objects.get(id=pk)
    form = MessageForm(instance=message)
    
    # check if the user is the host of the room, if not then send redirect him to page contains error message
    # so if user is not the host then he can't update the room
    if request.user != message.user :
        return HttpResponse('You are not allowed here!')

    if (request.method == 'POST'):
        form = MessageForm(request.POST, instance= message)
        print('Patch Request: ',request.POST)
        if form.is_valid():
            form.save()
            return redirect('room', pk=message.room.id)

    context = {'form': form}
    return render(request, 'base/room_form.html', context)



def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all() # relation between user and room is many to many, so we use room_set
    messages = user.message_set.all() # relation between user and message is one to many, so we use message_set
    topics = Topic.objects.all()
    return render(request, 'base/profile.html', {'user': user, 'rooms': rooms, 'messages': messages, 'topics': topics, 'room_count': rooms.count})


@login_required(login_url = 'login')
def updateUser(request, pk):
    user = User.objects.get(id=pk)
    form = UserForm(instance=user)

    if request.user != user:
        return HttpResponse('You are not allowed here!')
    
    if (request.method == 'POST'):
        form = UserForm(request.POST, instance=user)
        print('Patch Request: ',request.POST)
        if form.is_valid():
            form.save()
            return redirect('user-page', pk=user.id)

    context = {'form': form}
    return render(request, 'base/update-user.html', context)
    


def topicsPage(request):
    topics = Topic.objects.filter(name__icontains=request.GET.get('q'))
    return render(request, 'base/topics.html', {'topics': topics})

def activityPage(request):
    messages = Message.objects.filter(body__icontains=request.GET.get('q'))
    return render(request, 'base/activity.html', {'messages': messages})

