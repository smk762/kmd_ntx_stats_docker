from django.shortcuts import render

def get_base_context(request):
    season = get_page_season(request)
    scheme_host = get_current_host(request)
    context = {
        "season":season,
        "scheme_host": scheme_host,
        "sidebar_links":get_sidebar_links(season),
        "eco_data_link":get_eco_data_link()
    }


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
    
