import virtuallab_client
import zipfile
from PySpice.Unit import *
from PySpice.Spice.Parser import SpiceParser

url="http://localhost:8000"

# Registra un usuario profesor
name="Alexander"
id_professor=787878
role="professor"
password_professor="professor_pass"

print(virtuallab_client.registerUser(url,name,id_professor,role,password_professor))


# Registra un usuario estudiante
name="Helena"
id_student=99999
role="student"
password_student="student_pass"

print(virtuallab_client.registerUser(url,name,id_student,role,password_student))



# Inicia sesión con profesor
name="Alexander"
print(virtuallab_client.openSession(url,id_professor,password_professor))

# Carga laboratorio
file_path="client/rc.zip"
print(virtuallab_client.uploadLab(url,id_professor,file_path))

# Listar laboratorios disponibles para el usuario profesor
print(virtuallab_client.listProfessorsLabs(url,id_professor))

# Listar estudiantes registrados
print(virtuallab_client.listStudents(url,id_professor))

# Asignar práctica de laboratorio a un estudiante
print(virtuallab_client.assignLab(url,id_professor,"voltage_divider",id_student))

# Cierra sesión con usuario
print(virtuallab_client.closeSession(url,id_professor))




# Inicia sesión con usuario
print(virtuallab_client.openSession(url,id_student,password_student))


# Listar laboratorios disponibles para el usuario estudiante
print(virtuallab_client.listStudentLabs(url,id_student))

# Descarga laboratorio
lab_name="voltage_divider"
file_name=lab_name+".zip"
print(virtuallab_client.downloadLab(url,id_student,file_name))


# Abre el archivo zip y lee el contenido del archivo .cir
with zipfile.ZipFile(f"client/labs/{file_name}", "r") as zip_ref:    
    with zip_ref.open(lab_name+".cir") as file:        
        netlist = file.read().decode("utf-8")
        print("Starting simulation for lab:", lab_name)
        # Crea un objeto SpiceParser a partir del contenido del archivo .cir
        parser = SpiceParser(source=netlist)
        # Crea el circuito a partir del parser
        circuit = parser.build_circuit()
        # Crea una instancia del simulador para ejecutar el análisis
        simulator = circuit.simulator(temperature=25, nominal_temperature=25)
        # Ejecuta la simulación (punto de operación)
        analysis = simulator.operating_point()
        # Imprime los voltajes de los nodos
        for node in analysis.nodes.values():
            print(f'Node {node}: {float(node[0]):.4f} V')
        print("Simulation completed for lab:", lab_name)

        

# Cierra sesión con usuario
print(virtuallab_client.closeSession(url,id_student))





