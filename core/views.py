from django.shortcuts import render


# Create your views here.
def index(request):
    
    return render(request, 'index.html')

def ajax(request):

    return render(request, 'ajax.html')

def ajax2(request):

    return render(request, 'ajax2.html')

def nopage(request):
    back = request.META.get('HTTP_REFERER')
    return render(request, 'under_construction.html', {'back': back})
