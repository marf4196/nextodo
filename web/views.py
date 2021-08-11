from django.http.response import HttpResponse
from django.shortcuts import render
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login, logout
from .models import Task, TempUser
from django.conf import settings
import datetime
import random
import string
from kavenegar import *
import time

api = KavenegarAPI('7A336337304B75774A5748326E673871756F2F657572764F576D6747526F63626A33556F674A514B4135303D')
random_str = lambda N: ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(N))

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def grecaptcha_verify(request):
    data = request.POST
    captcha_rs = data.get('g-recaptcha-response')
    url = "https://www.google.com/recaptcha/api/siteverify"
    params = {
        'secret': settings.RECAPTCHA_SECRET_KEY,
        'response': captcha_rs,
        'remoteip': get_client_ip(request)
    }
    verify_rs = requests.get(url, params=params, verify=True)
    verify_rs = verify_rs.json()
    return verify_rs.get("success", False)

def RateLimited(maxPerSecond): # a decorator. @RateLimited(10) will let 10 runs in 1 seconds
    minInterval = 1.0 / float(maxPerSecond)
    def decorate(func):
        lastTimeCalled = [0.0]
        def rateLimitedFunction(*args,**kargs):
            elapsed = time.process_time() - lastTimeCalled[0]
            leftToWait = minInterval - elapsed
            if leftToWait>0:
                time.sleep(leftToWait)
            ret = func(*args,**kargs)
            lastTimeCalled[0] = time.process_time()
            return ret
        return rateLimitedFunction
    return decorate

def index_view(request, *args, **kwargs):
    print(f'\n\n\n----------------\n\n\n{request.user.username} : {get_client_ip(request)} opened index view at {datetime.datetime.now()}\n\n\n----------------\n\n\n')
    print(request.user.username)
    context = {
        'user': request.user
    }
    return render(request, 'index.html', context)


@RateLimited(4)
def register_view(request, *args, **kwargs):
    print(f'\n\n\n----------------\n\n\n{get_client_ip(request)} opened register view at {datetime.datetime.now()}\n\n\n----------------\n\n\n')
    
    if request.user.is_anonymous:
        if request.POST:
            if not grecaptcha_verify(request): # captcha was not correct
                context = {'message': 'reCaptcha failed, or maybe you are robot?'} #TODO: forgot password
                return render(request, 'register.html', context)
            if not User.objects.filter(username = request.POST['username']).exists():
                if not User.objects.filter(email = request.POST['email']).exists():
                    if request.POST['password'] == request.POST['passwordconf']:
                        username = request.POST['username']
                        email = request.POST['email']
                        password = request.POST['password']
                        
                        if not TempUser.objects.filter(username=username).exists():
                            if not TempUser.objects.filter(email=email).exists():
                                code = random_str(28)
                                while TempUser.objects.filter(code=code).exists():
                                    code = random_str(28)
                                TempUser.objects.create(username=username, password=password, email=email, code=code)
                            else:
                                context = {
                                    'email': request.POST['username'],
                                    'message': 'Email already exists',
                                }
                                return render(request, 'register.html', context)
                        else:
                            context = {
                                'email': request.POST['email'],
                                'message': 'Username already exists',
                            }
                            return render(request, 'register.html', context)
            
                        tempCode = TempUser.objects.get(username=username).code
                        activeMessage = f'برای فعال سازی اکانت خود روی لینک زیر کلیک کنید\n94.183.230.36:8000/active/?username={username}&code={code}'
                        # params = { 'sender' : '1000596446',
                        #            'receptor': '09171878751',
                        #            'message' :activeMessage }
                        # response = api.sms_send( params)
                        print(f'\n\n\n----------------\n\n\n{activeMessage}\n\n\n----------------\n\n\n')
                        
                        context = {
                        'username': request.POST['username'],
                        'email': request.POST['email'],
                        'phone': '09171878751',
                        'code' : tempCode,
                        'message': 'Contact 09171878751 for activation code',
                        }
                        return render(request, 'register.html', context)
                    else:
                        context = {
                        'username': request.POST['username'],
                        'email': request.POST['email'],
                        'message': 'Your password didn\'t match',
                        }
                        return render(request, 'register.html', context)
                else:
                    context = {
                        'username': request.POST['username'],
                        'message': 'Email already exists',
                    }
                    return render(request, 'register.html', context)
            else:
                context = {
                    'email': request.POST['email'],
                    'message': 'Username already exists',
                }
                return render(request, 'register.html', context)
        context = {}
        return render(request, 'register.html', context)
    else:
        return redirect('/')

@RateLimited(4)
def active_view(request, *args, **kwargs):
    print(f'\n\n\n----------------\n\n\n{get_client_ip(request)} opened active view at {datetime.datetime.now()}\n\n\n----------------\n\n\n')

    username = request.GET['username']
    code = request.GET['code']

    if TempUser.objects.filter(username=username).exists():
        if TempUser.objects.filter(code=code).exists():
            if TempUser.objects.filter(code=code, username=username).exists():
                tempuser = TempUser.objects.get(code=code, username=username)
                User.objects.create_user(tempuser.username, tempuser.email, tempuser.password)                
                tempuser.delete()
                context = {
                    'message': 'You account has been created\nyou can loging now'
                }
                return render(request, 'active.html', context)
            else:
                context = {
                    'message': 'something went wrong'
                }
                return render(request, 'active.html', context)
        else:
            context = {
            'message': 'Code is not correct'
        }
        return render(request, 'active.html', context)
    else:
        context = {
            'message': 'Username doesn\t exists'
        }
        return render(request, 'active.html', context)

@RateLimited(4)
def login_view(request, *args, **kwargs):
    print(f'\n\n\n----------------\n\n\n{get_client_ip(request)} opened login view at {datetime.datetime.now()}\n\n\n----------------\n\n\n')

    if request.user.is_anonymous:
        if request.POST:
            usermail = request.POST['usermail']
            password = request.POST['password']
            username = ''
            if User.objects.filter(username = usermail).exists():
                username = usermail
            elif User.objects.filter(email = usermail).exists():
                username = User.objects.filter(email = usermail).username
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('/tasks')
            else:
                context = {
                    'message': 'Password or username/email doesn\'t match'
                }
                return render(request, 'login.html', context)
        else:
            return render(request, 'login.html')
    else:
        return redirect('/')

def logout_view(request, *args, **kwargs):
    print(f'\n\n\n----------------\n\n\n{get_client_ip(request)} opened logout view at {datetime.datetime.now()}\n\n\n----------------\n\n\n')

    if not request.user.is_anonymous:
        logout(request)
    return redirect('/')

def tasks_view(request, *args, **kwargs): #TODO update function for status
    print(f'\n\n\n----------------\n\n\n{get_client_ip(request)} opened tasks view at {datetime.datetime.now()}\n\n\n----------------\n\n\n')

    if not request.user.is_anonymous:
        task = Task.objects.filter(user = request.user.id)
        context = {
            'user': request.user,
            'task'    : task
        }
        return render(request, 'tasks.html', context)
    else:
        return redirect('/')


def taskAdd_view(request, *args, **kwargs):
    print(f'\n\n\n----------------\n\n\n{get_client_ip(request)} opened task add view at {datetime.datetime.now()}\n\n\n----------------\n\n\n')

    if not request.user.is_anonymous:
        user = request.user
        createDate = datetime.datetime.now()

        taskText = request.POST['text']
        priority = request.POST['priority']
        statuse = request.POST['statuse']
        dueDate = request.POST['due_date']
        actionDate = request.POST['action_date']

        thisTask = Task(user=user, create_date=createDate, text=taskText, priority=priority, statuse=statuse, due_date=dueDate, action_date= actionDate)
        thisTask.save()


        return redirect('/tasks/')
    else:
        return redirect('/')

def taskShow_view(request, id):
    print(f'\n\n\n----------------\n\n\n{get_client_ip(request)} opened task show view at {datetime.datetime.now()}\n\n\n----------------\n\n\n')

    if not request.user.is_anonymous:
        task = Task.objects.get(id=id)
        if task.user == request.user: 
            context = {
                    'user': request.user,
                    'task'    : task
                }
            return render(request, 'tasks_edit.html', context)
        else:
            return HttpResponse('YOU CANT DO THAT')
    else:
        return redirect('/')

def taskEdit_view(request, id):
    print(f'\n\n\n----------------\n\n\n{get_client_ip(request)} opened task view view at {datetime.datetime.now()}\n\n\n----------------\n\n\n')

    if not request.user.is_anonymous:
        task = Task.objects.get(id=id, user = request.user)

        taskText = request.POST['text']
        priority = request.POST['priority']
        statuse = request.POST['statuse']
        dueDate = request.POST['due_date']
        actionDate = request.POST['action_date']

        task.text = taskText
        task.priority = priority
        task.statuse = statuse
        task.due_date = dueDate
        task.action_date = actionDate

        task.save()
        return redirect('/tasks/')
    else:
        return redirect('/')

def taskDelete_view(request, id):
    print(f'\n\n\n----------------\n\n\n{get_client_ip(request)} opened task delete view at {datetime.datetime.now()}\n\n\n----------------\n\n\n')
    
    if not request.user.is_anonymous:
        if not request.user == Task.objects.get(id=id).user:
            return redirect('/')
        else:
            task = Task.objects.get(id = id, user=request.user)
            task.delete()
            return redirect('/tasks/')
    else:
        return redirect('/')

def taskDeleteConfirm_view(request, id):
    print(f'\n\n\n----------------\n\n\n{get_client_ip(request)} opened task delete confirm view at {datetime.datetime.now()}\n\n\n----------------\n\n\n')

    if not request.user.is_anonymous:
        task = Task.objects.get(id = id, user=request.user)
        context = {
            'task'    : task
        }
        return render(request, 'deleteConfirm.html', context)
    else:
        return redirect('/')