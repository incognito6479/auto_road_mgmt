from django.utils import translation


class AppLanguageMiddleware:
    """
    Activates Uzbek ('uz') for all application routes.
    Keeps English ('en-us') for the Django admin panel (/admin/).
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith("/admin/"):
            translation.activate("en-us")
        else:
            translation.activate("uz")

        response = self.get_response(request)
        translation.deactivate()
        return response
