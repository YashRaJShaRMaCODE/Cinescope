import secrets


class PublicContentSecurityPolicyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.csp_nonce = secrets.token_urlsafe(18)
        response = self.get_response(request)
        content_type = response.get("Content-Type", "")
        if content_type.startswith("text/html") and not request.path.startswith("/admin/"):
            response["Content-Security-Policy"] = "; ".join((
                "default-src 'self'",
                "base-uri 'self'",
                "connect-src 'self'",
                "font-src 'self' https://fonts.gstatic.com",
                "form-action 'self'",
                "frame-ancestors 'none'",
                "img-src 'self' data: https://image.tmdb.org",
                "object-src 'none'",
                f"script-src 'self' 'nonce-{request.csp_nonce}'",
                "script-src-attr 'none'",
                "style-src 'self' https://fonts.googleapis.com",
                "upgrade-insecure-requests",
            ))
            response["Permissions-Policy"] = "camera=(), microphone=(), geolocation=(), payment=(), usb=()"
        return response
