from excepciones import Mensaje_Para_Redireccion_de_Exception

class Requires_el_Login_de_Exception(Mensaje_Para_Redireccion_de_Exception):
    def __init__(self, message='Estmimado usuario, debe iniciar sesión para acceder.', path_route='/iniciar_sesion', path_message='Inicia sesión'):
        super().__init__(message, path_route, path_message)

class LoginExpired(Mensaje_Para_Redireccion_de_Exception):
    def __init__(self, message='Estimado usuario, su sesión ha expirado ', path_route='/iniciar_sesion', path_message='Inicia sesión nuevamente'):
        super().__init__(message, path_route, path_message)