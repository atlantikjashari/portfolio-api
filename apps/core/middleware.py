import time


class ResponseTimeMiddleware:
    """Adds X-Response-Time-Ms so the Backend Lab can show server-side processing time."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start = time.perf_counter()
        response = self.get_response(request)
        response["X-Response-Time-Ms"] = f"{(time.perf_counter() - start) * 1000:.1f}"
        return response
