"""Genera un QR que apunta al servidor local de Control QPR asignados.

Util para abrirlo rapido desde el celular sin tipear la URL a mano.
Recorda: solo funciona si el celular esta en la misma red interna
que la compu que corre el servidor (ver README).
"""
import qrcode

URL = "http://22.43.142.175:8731"

img = qrcode.make(URL, box_size=10, border=4)
img.save("QR_control_qpr.png")
print("Listo! QR guardado para:", URL)
