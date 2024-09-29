from django.shortcuts import render, HttpResponse
from django.contrib.auth.decorators import login_required


# Create your views here.
@login_required
def cupom_views(request):

    return render(request, template_name=("app_cupom/base.html"))
