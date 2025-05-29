import unittest
from app import app

class PruebasDeLaApp(unittest.TestCase):
    def setUp(self):
        # Configura la app para pruebas
        self.app = app.test_client()
        app.config['TESTING'] = True

    def test_pagina_inicio(self):
        # Verifica que la página de inicio cargue correctamente
        respuesta = self.app.get('/')
        self.assertEqual(respuesta.status_code, 200)

    def test_login_incorrecto(self):
        # Simula un intento de login con usuario falso
        respuesta = self.app.post('/form-login', data={
            'txtuser': 'clientaae',
            'txtpassword': '1234'
        }, follow_redirects=True)
        self.assertIn(b'Usuario no encontrado', respuesta.data)

if __name__ == '__main__':
    unittest.main()
