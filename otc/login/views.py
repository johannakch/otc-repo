from django.contrib.auth.models import User
from django.shortcuts import render
from django.core.mail import send_mail

# Create your views here.


def request_new_password(request):
    context = {}
    if request.method == 'POST':
        print(request.POST)
        if 'request_new_pw' in request.POST:
            superusers = [user.email for user in User.objects.filter(is_superuser=True)]
            print(superusers)
            subject = 'Reservierungssystem OTC - Anfrage zur Passwortänderung'
            name = request.POST['username']
            message = '{} benötigt ein neues Passwort. Bitte neues Passwort zuweisen.'.format(name)
            email = request.POST['email']
            from_email = email
            to_email = superusers
            try:
                send_mail(subject, message, from_email, [to_email[0]])
            except Exception as e:
                print(e)
                print("failed")



    return render(request, 'registration/request_new_password.html', context)