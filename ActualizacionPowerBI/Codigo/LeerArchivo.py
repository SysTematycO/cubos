import subprocess

def AbrirArchivo(ruta):
    archivo = subprocess.Popen([ruta], shell=True)
    return archivo

