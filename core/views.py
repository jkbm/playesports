from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views import generic

# Create your views here.
def index(request):
    
    return render(request, 'index.html')

def ajax(request):

    return render(request, 'ajax.html')

def ajax2(request):

    return render(request, 'ajax2.html')

def nopage(request, exception=None):
    back = request.META.get('HTTP_REFERER')
    return render(request, 'under_construction.html', {'back': back})

class Signup(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'
