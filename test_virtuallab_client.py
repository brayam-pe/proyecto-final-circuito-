import virtuallab_client
import os
import zipfile
from PySpice.Unit import *
from PySpice.Spice.Parser import SpiceParser

url_servidor = 'http://localhost:80'

# Registra a un profesor. Los valores de rol
nombre="Alexander"
id_profesor=787878
rol="professor"
contrasena_profesor="professor_pass"

print(virtuallab_client.registerUser(url_servidor,nombre,id_profesor,rol,contrasena_profesor))


# Registra a un estudiante.
nombre="Helena"
id_estudiante=99999
rol="student"
contrasena_estudiante="student_pass"

print(virtuallab_client.registerUser(url_servidor,nombre,id_estudiante,rol,contrasena_estudiante))



# Inicia sesión con el profesor
nombre="Alexander"
print(virtuallab_client.openSession(url_servidor,id_profesor,contrasena_profesor))

# Carga el laboratorio
ruta_archivo="client/rc.zip"
print(virtuallab_client.uploadLab(url_servidor,id_profesor,ruta_archivo))

# Lista los laboratorios disponibles para el profesor
print(virtuallab_client.listProfessorsLabs(url_servidor,id_profesor))

# Lista los estudiantes registrados
print(virtuallab_client.listStudents(url_servidor,id_profesor))

# Asigna una práctica de laboratorio a un estudiante
print(virtuallab_client.assignLab(url_servidor,id_profesor,"voltage_divider",id_estudiante))

# Cierra la sesión del usuario
print(virtuallab_client.closeSession(url_servidor,id_profesor))




# Inicia sesión con el usuario
print(virtuallab_client.openSession(url_servidor,id_estudiante,contrasena_estudiante))


# Lista los laboratorios disponibles para el estudiante
print(virtuallab_client.listStudentLabs(url_servidor,id_estudiante))

# Descarga el laboratorio
nombre_laboratorio="voltage_divider"
nombre_archivo=nombre_laboratorio+".zip"
print(virtuallab_client.downloadLab(url_servidor,id_estudiante,nombre_archivo))


# Abre el archivo zip y lee el contenido del archivo .cir
with zipfile.ZipFile(f"client/labs/{nombre_archivo}", "r") as archivo_zip:    
    with archivo_zip.open(nombre_laboratorio+".cir") as archivo:        
        lista_conexiones = archivo.read().decode("utf-8")
        print("Iniciando la simulación del laboratorio:", nombre_laboratorio)
        # Crea un objeto SpiceParser a partir del contenido del archivo .cir
        lista_conexiones = lista_conexiones.replace("\r\n", "\n").replace("\n", os.linesep)
        parser = SpiceParser(source=lista_conexiones)
        # Crea el circuito a partir del analizador
        circuito = parser.build_circuit()
        # Crea una instancia del simulador para ejecutar el análisis
        simulador = circuito.simulator(temperature=25, nominal_temperature=25)
        # Ejecuta la simulación (punto de operación)
        analisis = simulador.operating_point()
        # Imprime los voltajes de los nodos
        for nodo in analisis.nodes.values():
            print(f'Voltaje del nodo {nodo}: {float(nodo[0]):.4f} V')
        print("Simulación completada para el laboratorio:", nombre_laboratorio)

        

# Cierra la sesión del usuario
print(virtuallab_client.closeSession(url_servidor,id_estudiante))





