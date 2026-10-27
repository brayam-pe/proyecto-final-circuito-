# Instalar el módulo requests haciendo desde una terminal: pip install requests
import requests
import os


# Función para registrar usuario
def registerUser(url,name,id,role,password):    
    response=requests.post(url+'/register',data=f'name={name}&id={id}&role={role}&password={password}')
    return response.content.decode('utf-8')

# Funciónn para abrir una sesión
def openSession(url,id,password):    
    response=requests.post(url+'/login',data=f'id={id}&password={password}')
    return response.content.decode('utf-8')

# Función para cerrar una sesión
def closeSession(url,id):    
    response=requests.post(url+'/logout',data=f'id={id}')
    return response.content.decode('utf-8')

# Función para enviar una práctica de laboratorio
def uploadLab(url,id,file_path):    
    
    filename = os.path.basename(file_path)

    headers = {'X-File-Name': filename,'X-Client-ID': str(id)    }
    with open(file_path, 'rb') as f:
        response=requests.post(url+'/upload_lab',data=f,headers=headers)
        return response.content.decode('utf-8')

# Función para recibir una práctica de laboratorio
def downloadLab(url,id,file_name):    
    headers = {'X-File-Name': file_name,'X-Client-ID': str(id)    }
    response=requests.get(url+'/download_lab',headers=headers)
    download_dir = "client/labs"
    os.makedirs(download_dir, exist_ok=True)
    target_path = os.path.join(download_dir, file_name)
    
    with open(target_path, "wb") as f:
        f.write(response.content)
        return f"File {file_name} downloaded to {target_path}"
    
    

# Función para obtener la lista de laboratorios disponibles para un estudiante
def listStudentLabs(url,id):    
    response=requests.get(url+'/list_student_labs',data=f'id={id}')
    return response.content.decode('utf-8')

# Función para obtener la lista de laboratorios disponibles para un profesor
def listProfessorsLabs(url,id):    
    response=requests.get(url+'/list_professors_labs',data=f'id={id}')
    return response.content.decode('utf-8')

# Función para obtener la lista de estudiantes registrados
def listStudents(url,id):    
    response=requests.get(url+'/list_students',data=f'id={id}')
    return response.content.decode('utf-8')

# Función para asignar una práctica de laboratorio a un estudiante
def assignLab(url,id,lab_name,student_id):    
    response=requests.post(url+'/assign_lab',data=f'id={id}&lab_name={lab_name}&student_id={student_id}')
    return response.content.decode('utf-8')


