from django.http import HttpResponse


# Create your views here.
def debug(request):
    from .services.functions import check_new_entires

    check_new_entires(
        blockchain_name='polygon',
        address='0x205c648b40cdCF13fF177d122Db9Fe848A07A23e',
    )

    return HttpResponse('Start DEBUGING...')
