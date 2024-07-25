from django.shortcuts import render, HttpResponse
from django.contrib.auth.decorators import login_required
from .tasks import teste

# Create your views here.
@login_required
def dashboard(request):
    teste.delay(15, 115)
    return render(request, template_name=("app_dashboard/base.html"))
