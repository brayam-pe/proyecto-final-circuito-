# Implementación de las funciones solicitadas para el servidor del laboratorio virtual.
# Se conservan sin cambios virtuallab_server.py y virtuallab_client.py.
# La persistencia usa archivos de texto JSON Lines, no una base de datos.

import json
import os
import zipfile
from io import BytesIO

SERVER_DIR = os.path.dirname(os.path.abspath(__file__))
usersFile = os.path.join(SERVER_DIR, "users.txt")
sessionsFile = os.path.join(SERVER_DIR, "sessions.txt")
labsFile = os.path.join(SERVER_DIR, "labs.txt")
assignmentsFile = os.path.join(SERVER_DIR, "assignments.txt")
labsDirectory = os.path.join(SERVER_DIR, "labs")


def _read_records(path):
    if not os.path.exists(path):
        return []
    records = []
    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            try:
                if line.strip():
                    records.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return records


def _write_records(path, records):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as file:
        for item in records:
            file.write(json.dumps(item, ensure_ascii=True) + "\n")


def _json(value):
    # ASCII evita que Content-Length del servidor base falle con nombres acentuados.
    return json.dumps(value, ensure_ascii=True)


def _user(user_id):
    for item in _read_records(usersFile):
        if str(item.get("id")) == str(user_id):
            return item
    return None


def _logged_in(user_id):
    return any(str(item.get("id")) == str(user_id) for item in _read_records(sessionsFile))


def _has_role(user_id, role):
    user = _user(user_id)
    return user is not None and user.get("role") == role


def _safe_zip_name(name):
    if not name:
        return None
    name = str(name)
    base = os.path.basename(name)
    if base != name or not base.lower().endswith(".zip") or base.lower() == ".zip":
        return None
    return base


def _key(name):
    name = os.path.basename(str(name)).strip()
    if name.lower().endswith(".zip"):
        name = name[:-4]
    return name.casefold()


def _all_labs():
    os.makedirs(labsDirectory, exist_ok=True)
    labs = {}
    for item in _read_records(labsFile):
        filename = _safe_zip_name(item.get("file_name"))
        if filename and os.path.isfile(os.path.join(labsDirectory, filename)):
            labs[filename.casefold()] = {
                "lab_name": item.get("lab_name") or os.path.splitext(filename)[0],
                "file_name": filename,
                "professor_id": str(item.get("professor_id", "")),
            }
    # También incluye ZIP de ejemplo que ya estén en la carpeta del servidor.
    for filename in os.listdir(labsDirectory):
        filename = _safe_zip_name(filename)
        if filename and filename.casefold() not in labs:
            labs[filename.casefold()] = {
                "lab_name": os.path.splitext(filename)[0],
                "file_name": filename,
                "professor_id": "",
            }
    return sorted(labs.values(), key=lambda x: x["lab_name"].casefold())


def _lab(name):
    key = _key(name)
    for item in _all_labs():
        if key in (_key(item["lab_name"]), _key(item["file_name"])):
            return item
    return None


def writeUserDataToFile(user_data):
    os.makedirs(os.path.dirname(usersFile), exist_ok=True)
    with open(usersFile, "a", encoding="utf-8") as file:
        file.write(json.dumps(user_data, ensure_ascii=True) + "\n")


def registerUser(name, id, role, password):
    role = str(role).strip().lower()
    role = {"profesor": "professor", "estudiante": "student"}.get(role, role)
    if not str(name).strip() or not str(id).strip() or not str(password):
        return "error"
    if role not in ("professor", "student"):
        return "error"
    if _user(id):
        return "User already registered"
    user_data = {
        "name": str(name).strip(),
        "id": str(id).strip(),
        "role": role,
        "password": str(password),
    }
    writeUserDataToFile(user_data)
    return f"User {user_data['name']} with role {role} registered"


def openSession(id, password):
    user = _user(id)
    if user is None or user.get("password") != str(password):
        return "error"
    sessions = _read_records(sessionsFile)
    if not any(str(item.get("id")) == str(id) for item in sessions):
        sessions.append({"id": str(id)})
        _write_records(sessionsFile, sessions)
    return "Session was succesfully opened"


def closeSession(id):
    sessions = _read_records(sessionsFile)
    remaining = [item for item in sessions if str(item.get("id")) != str(id)]
    if len(remaining) == len(sessions):
        return "error"
    _write_records(sessionsFile, remaining)
    return "Session was succesfully closed"


def uploadLab(id, file_name, file_data):
    if not _has_role(id, "professor") or not _logged_in(id):
        return "error"
    filename = _safe_zip_name(file_name)
    if filename is None or not isinstance(file_data, (bytes, bytearray)):
        return "error"
    if not zipfile.is_zipfile(BytesIO(file_data)):
        return "error"
    os.makedirs(labsDirectory, exist_ok=True)
    try:
        with open(os.path.join(labsDirectory, filename), "wb") as file:
            file.write(file_data)
    except OSError:
        return "error"
    labs = [x for x in _read_records(labsFile)
            if str(x.get("file_name", "")).casefold() != filename.casefold()]
    labs.append({
        "lab_name": os.path.splitext(filename)[0],
        "file_name": filename,
        "professor_id": str(id),
    })
    _write_records(labsFile, labs)
    return "File was succesfully received"


def downloadLab(id, file_name):
    if not _has_role(id, "student") or not _logged_in(id):
        return "error"
    filename = _safe_zip_name(file_name)
    if filename is None:
        return "error"
    assigned = any(
        str(x.get("student_id")) == str(id)
        and _key(x.get("file_name", "")) == _key(filename)
        for x in _read_records(assignmentsFile)
    )
    if not assigned:
        return "error"
    lab = _lab(filename)
    if lab is None:
        return "error"
    try:
        with open(os.path.join(labsDirectory, lab["file_name"]), "rb") as file:
            return file.read()
    except OSError:
        return "error"


def listStudentLabs(id):
    if not _has_role(id, "student") or not _logged_in(id):
        return "error"
    labs = {_key(x["file_name"]): x for x in _all_labs()}
    result = []
    for assignment in _read_records(assignmentsFile):
        if str(assignment.get("student_id")) == str(id):
            lab = labs.get(_key(assignment.get("file_name", "")))
            if lab:
                result.append({
                    "lab_name": lab["lab_name"],
                    "file_name": lab["file_name"],
                    "professor_id": str(assignment.get("professor_id", "")),
                })
    return _json(result)


def listProfessorsLabs(id):
    if not _has_role(id, "professor") or not _logged_in(id):
        return "error"
    return _json(_all_labs())


def listStudents(id):
    if not _has_role(id, "professor") or not _logged_in(id):
        return "error"
    students = [
        {"name": x.get("name", ""), "id": str(x.get("id", ""))}
        for x in _read_records(usersFile) if x.get("role") == "student"
    ]
    return _json(students)


def assignLab(id, lab_name, student_id):
    if not _has_role(id, "professor") or not _logged_in(id):
        return "error"
    if not _has_role(student_id, "student"):
        return "error"
    lab = _lab(lab_name)
    if lab is None:
        return "error"
    assignments = _read_records(assignmentsFile)
    duplicate = any(
        str(x.get("student_id")) == str(student_id)
        and _key(x.get("file_name", "")) == _key(lab["file_name"])
        for x in assignments
    )
    if not duplicate:
        assignments.append({
            "student_id": str(student_id),
            "file_name": lab["file_name"],
            "professor_id": str(id),
        })
        _write_records(assignmentsFile, assignments)
    labs = _read_records(labsFile)
    if not any(str(x.get("file_name", "")).casefold() == lab["file_name"].casefold()
               for x in labs):
        labs.append({
            "lab_name": lab["lab_name"],
            "file_name": lab["file_name"],
            "professor_id": str(id),
        })
        _write_records(labsFile, labs)
    return "Lab was succesfully assigned"
