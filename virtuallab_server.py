
import argparse
from urllib.parse import urlparse
from urllib.parse import parse_qs
from http.server import BaseHTTPRequestHandler, HTTPServer
from json import dumps
import virtuallab_functions


class Server(HTTPServer):
    def __init__(self, address, request_handler):
        super().__init__(address, request_handler)


class RequestHandler(BaseHTTPRequestHandler):
    def __init__(self, request, client_address, server_class):
        self.server_class = server_class
        super().__init__(request, client_address, server_class)

    def do_GET(self):
        resource=urlparse(self.path).path
        match resource:
                    
            case '/download_lab':    
                id = self.headers.get('X-Client-ID')
                filename = self.headers.get('X-File-Name')                

                data=virtuallab_functions.downloadLab(id,filename)

                if data == "error":
                    self.send_response(404)
                    self.send_header("Content-Type", "text/plain")
                    self.send_header("Content-Length", str(len(data)))
                    self.end_headers()
                    self.wfile.write(data.encode('utf-8'))
                else:
                    self.send_response(200)
                    self.send_header("Content-Type", "application/octet-stream")                
                    self.send_header("Content-Length", str(len(data)))            
                    self.end_headers()                                        
                    self.wfile.write(data)
                    
            
        
            case '/list_student_labs':
                content_len = int(self.headers.get('Content-Length'))
                post_body = self.rfile.read(content_len)
                params_dict=parse_qs(post_body.decode(), strict_parsing=True)
                response=str(virtuallab_functions.listStudentLabs(params_dict['id'][0]))
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.send_header("Content-Length", str(len(response)))
                self.end_headers()
                self.wfile.write(str(response).encode('utf8'))
                self.wfile.flush()

            case '/list_professors_labs':
                content_len = int(self.headers.get('Content-Length'))
                post_body = self.rfile.read(content_len)
                params_dict=parse_qs(post_body.decode(), strict_parsing=True)
                response=str(virtuallab_functions.listProfessorsLabs(params_dict['id'][0]))
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.send_header("Content-Length", str(len(response)))
                self.end_headers()
                self.wfile.write(str(response).encode('utf8'))
                self.wfile.flush()
            
            case '/list_students':
                content_len = int(self.headers.get('Content-Length'))
                post_body = self.rfile.read(content_len)
                params_dict=parse_qs(post_body.decode(), strict_parsing=True)
                response=str(virtuallab_functions.listStudents(params_dict['id'][0]))
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.send_header("Content-Length", str(len(response)))
                self.end_headers()
                self.wfile.write(str(response).encode('utf8'))
                self.wfile.flush()    



    def do_POST(self):
        resource=urlparse(self.path).path
        print(resource)
        match resource:
            case "/register":
                content_len = int(self.headers.get('Content-Length'))
                post_body = self.rfile.read(content_len)
                params_dict=parse_qs(post_body.decode(), strict_parsing=True)
                response=virtuallab_functions.registerUser(params_dict['name'][0],params_dict['id'][0],params_dict['role'][0],params_dict['password'][0])

            case "/login":
                content_len = int(self.headers.get('Content-Length'))
                post_body = self.rfile.read(content_len)
                params_dict=parse_qs(post_body.decode(), strict_parsing=True)
                response=virtuallab_functions.openSession(params_dict['id'][0],params_dict['password'][0])
            case "/logout":
                content_len = int(self.headers.get('Content-Length'))
                post_body = self.rfile.read(content_len)
                params_dict=parse_qs(post_body.decode(), strict_parsing=True)
                response=virtuallab_functions.closeSession(params_dict['id'][0])

            case "/upload_lab":
                file_name = self.headers.get('X-File-Name', 'lab0.zip')
                id = self.headers.get('X-Client-ID')
                content_len = int(self.headers.get('Content-Length'))
                file_data = self.rfile.read(content_len)
                response=virtuallab_functions.uploadLab(id,file_name,file_data)

            case "/assign_lab":
                content_len = int(self.headers.get('Content-Length'))
                post_body = self.rfile.read(content_len)
                params_dict=parse_qs(post_body.decode(), strict_parsing=True)
                response=virtuallab_functions.assignLab(params_dict['id'][0],params_dict['lab_name'][0],params_dict['student_id'][0])




        
        
        
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.send_header("Content-Length", str(len(response)))
        self.end_headers()
        self.wfile.write(str(response).encode('utf8'))
        self.wfile.flush()

def start_server(addr, port, server_class=Server, handler_class=RequestHandler):
    server_address = (addr, port)
    http_server = server_class(server_address, handler_class)
    print(f"Starting server on {addr}:{port}")
    http_server.serve_forever()


def main():
    parser = argparse.ArgumentParser(description="Run a simple HTTP server.")
    parser.add_argument(
        "-l",
        "--listen",
        default="0.0.0.0",
        help="Specify the IP address which server should listen",
    )
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=80,
        help="Specify the port which server should listen",
    )
    args = parser.parse_args()
    start_server(addr=args.listen, port=args.port)


if __name__ == "__main__":
    main()