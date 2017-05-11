from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.conf import settings

import django.contrib.auth

import json
import numpy

import sheets_backend.sockets

import sheets_app.models as models

# Create your views here.

def get_user_sheet_id(user, sheet_id):
    return str(user.id) + '_' + sheet_id

def mypipeline(backend, strategy, details, response, user=None, *args, **kwargs):
    print('mypipline')
    print('backend ',backend)
    print('strategy',strategy)
    print('details ',details)
    print('response',response)
    print('user    ',user)

    user.profile_image_url = response['image'].get('url')
    user.save()

def cells_values(ret):
    cells = ret.cells
    def f(c):
        return c.value
    return numpy.vectorize(f, otypes=[str])(cells).tolist()

def cells_array(ret):
    cells = ret.cells
    def f(c):
        return json.dumps([c.string, c.value])
    return numpy.vectorize(f, otypes=[str])(cells).tolist()

def index(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('social:begin', args=['google-oauth2',])+'?next='+reverse('index'))

    user = django.contrib.auth.get_user(request)
    print('index')
    print('GET',list(request.GET.items()))


    if user.is_authenticated():
        sheets = list(user.sheet_user_creator.all())
    else:
        sheets = []
    
    context = {'user': user, 'sheets': sheets}
    return render(request, 'sheets_app/index.html', context)

def sheet(request, sheet_id):
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('social:begin', args=['google-oauth2',])+'?next='+reverse('index'))
    
    sheet = get_object_or_404(models.Sheet, pk=sheet_id)
    
    u = django.contrib.auth.get_user(request)
    
    print('user',repr(u))
    for k, v in u.__dict__.items():
        print('  ', k, v)

    sp = sheets_backend.sockets.SheetProxy(sheet.sheet_id, settings.WEB_SHEETS_PORT)
    
    ret = sp.get_sheet_data()

    print(ret)
    print(repr(ret.cells))

    cells = cells_array(ret)
    
    print('cells',repr(cells))
    
    context = {
        'cells': json.dumps(cells),
        'script': ret.script,
        'script_output': ret.script_output,
        'user': u,
        'sheet': sheet
        }
    return render(request, 'sheets_app/sheet.html', context)

def set_cell(request, sheet_id):
    r = int(request.POST['r'])
    c = int(request.POST['c'])
    s = request.POST['s']

    sheet = get_object_or_404(models.Sheet, pk=sheet_id)
 
    sp = sheets_backend.sockets.SheetProxy(sheet.sheet_id, settings.WEB_SHEETS_PORT)

    ret = sp.set_cell(r, c, s)

    ret = sp.get_cell_data()
    
    cells = cells_array(ret)

    return JsonResponse({'cells':cells})

def set_exec(request, sheet_id):
    print('set script')
    print('post')
    for k, v in request.POST.items(): print('  ',k,v)
    s = request.POST['text']
    print('set exec')
    print(repr(s))
    sheet = get_object_or_404(models.Sheet, pk=sheet_id)
 
    sp = sheets_backend.sockets.SheetProxy(sheet.sheet_id, settings.WEB_SHEETS_PORT)

    ret = sp.set_exec(s)

    ret = sp.get_sheet_data()
    
    cells = cells_array(ret)

    return JsonResponse({'cells':cells, 'script':ret.script, 
            'script_output':ret.script_output,})

def add_column(request, sheet_id):
    if not request.POST['i']:
        i = None
    else:
        i = int(request.POST['i'])

    sheet = get_object_or_404(models.Sheet, pk=sheet_id)
 
    sp = sheets_backend.sockets.SheetProxy(sheet.sheet_id, settings.WEB_SHEETS_PORT)

    ret = sp.add_column(i)

    ret = sp.get_cell_data()
    
    cells = cells_array(ret)

    return JsonResponse({'cells':cells})

def add_row(request, sheet_id):
    if not request.POST['i']:
        i = None
    else:
        i = int(request.POST['i'])

    sheet = get_object_or_404(models.Sheet, pk=sheet_id)
 
    sp = sheets_backend.sockets.SheetProxy(sheet.sheet_id, settings.WEB_SHEETS_PORT)

    ret = sp.add_row(i)

    ret = sp.get_cell_data()
    
    cells = cells_array(ret)

    return JsonResponse({'cells':cells})

@login_required
def sheet_new(request):
    sheet_name = request.POST['sheet_name']

    c = sheets_backend.sockets.Client(settings.WEB_SHEETS_PORT)

    ret = c.sheet_new()

    s = models.Sheet()
    s.user_creator = request.user
    s.sheet_id = ret.i
    s.sheet_name = sheet_name
    s.save()

    return redirect('sheets:sheet', s.id)



