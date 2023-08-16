from .utils.structures import *
from .objects import *


# def help() -> None:
#     from danielutils import IndentedWriter, file_exists
#     FILE = "./client_secrets.json"
#     if not file_exists(FILE):
#         print(f"Creating {FILE}")
#         with open(FILE, "w", encoding="utf8") as f:
#             w = IndentedWriter(f)

#             w.write("{")
#             w.indent()
#             w.write("\"installed\": {")
#             w.indent()
#             w.write("\"client_id\": \"\"")
#             w.write("\"project_id\": \"\"")
#             w.write("\"auth_uri\": \"https://accounts.google.com/o/oauth2/auth\"")
#             w.write("\"token_uri\": \"https://oauth2.googleapis.com/token\"")
#             w.write(
#                 "\"auth_provider_x509_cert_url\": \"https://www.googleapis.com/oauth2/v1/certs\"")
#             w.write("\"client_secret\": \"\"")
#             w.write("\"redirect_uris\": [")
#             w.indent()
#             w.write("\"http://localhost\"")
#             w.undent()
#             w.write("]")
#             w.undent()
#             w.write("}")
#             w.undent()
#             w.write("}")
#         print("please fill in missing values")
#         print("see https://console.cloud.google.com/")
#     else:
#         pass
