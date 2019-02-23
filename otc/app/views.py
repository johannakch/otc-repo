from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.

from django.http import HttpResponse


def index(request):
    context = {}
    return render(request, 'app/index.html', context)