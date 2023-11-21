from odoo import http
from odoo.addons.auth_signup.controllers.main import AuthSignupHome

class LibraryAuthSignupHome(AuthSignupHome):
    @http.route('/web/signup', type='http', auth='public', website=True, sitemap=False)
    def web_auth_signup(self, *args, **kw):
        response = super(LibraryAuthSignupHome, self).web_auth_signup(*args, **kw)
        # Aquí puedes agregar tu lógica personalizada
        return response

    @http.route('/web/reset_password', type='http', auth='public', website=True, sitemap=False)
    def web_auth_reset_password(self, *args, **kw):
        response = super(LibraryAuthSignupHome, self).web_auth_reset_password(*args, **kw)
        # Aquí puedes agregar tu lógica personalizada
        return response
