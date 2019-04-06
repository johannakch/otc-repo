from django.contrib.auth.models import User
from django.shortcuts import render
from django.core.mail import EmailMessage


def request_new_password(request):
    context = {'sendmail_success': False}
    if request.method == 'POST':
        if 'request_new_pw' in request.POST:
            superusers = [user.email for user in User.objects.filter(is_superuser=True)]
            subject = 'Reservierungssystem OTC - Anfrage zur Passwortänderung'
            name = request.POST['username']
            user_email = request.POST['email']
            message = '{} ({}) benötigt ein neues Passwort. Bitte neues Passwort zuweisen.'.format(name, user_email)
            try:
                email = EmailMessage(subject, message, to=superusers)
                code = email.send()
                if code == 1:
                    context.update({
                        'sendmail_success': True
                    })
                else:
                    context.update({
                        'sendmail_success': False,
                        'tried_to_send': True,
                    })
            except Exception as e:
                print(e)
                context.update({
                    'sendmail_success': False,
                    'tried_to_send': True,
                    #'admin_contact': 'mariusschmitt@algrande.net'
                })

    return render(request, 'registration/request_new_password.html', context)