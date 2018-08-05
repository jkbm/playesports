from django.shortcuts import render
from core.tasks import temp_task

# Create your views here.
def index(request):
    temp_task.delay()

    return render(request, 'index.html')

def ajax(request):

    return render(request, 'ajax.html')

def ajax2(request):

    return render(request, 'ajax2.html')

def nopage(request):
    back = request.META.get('HTTP_REFERER')
    return render(request, 'under_construction.html', {'back': back})
