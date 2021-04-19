from django.shortcuts import render

def error_400(request,  exception):
        context = {
        	"error":"400 - Bad Request"
        }
        return render(request,'error/generic_error.html', context)

def error_403(request, exception):
        context = {
        	"error":"403 - Verboten"
        }
        return render(request,'error/generic_error.html', context)

def error_404(request, exception):
        context = {
        	"error":"404 - Not Found"
        }
        return render(request,'error/generic_error.html', context)

def error_500(request):
        context = {
        	"error":"500 - Internal Server Error"
        }
        return render(request,'error/generic_error.html', context)

def error_502(request, exception):
        context = {
        	"error":"502 - Naughty Gateway"
        }
        return render(request,'error/generic_error.html', context)
