from django.shortcuts import render
from kmd_ntx_api.lib_const import *
from kmd_ntx_api.lib_helper import get_base_context


def error_400(request,  exception):
    context = get_base_context(request)
    context.update({
        "error":"400 - Bad Request"
    })
    return render(request,'error/generic_error.html', context)


def error_403(request, exception):
    context = get_base_context(request)
    context.update({
        "error":"403 - Verboten"
    })
    return render(request,'error/generic_error.html', context)


def error_404(request, exception):
    context = get_base_context(request)
    context.update({
        "error":"404 - Not Found"
    })
    return render(request,'error/generic_error.html', context)


def error_500(request):
    context = get_base_context(request)
    context.update({
        "error":"500 - Internal Server Error"
    })
    return render(request,'error/generic_error.html', context)
    

def error_502(request, exception):
    context = get_base_context(request)
    context.update({
        "error":"502 - Naughty Gateway"
    })
    return render(request,'error/generic_error.html', context)

