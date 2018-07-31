# coding=utf-8
import ast
import json
import requests
import yaml


class FocusNF():
    # CONSTANTES da empresa e do acesso à API
    __environment = "";
    __url_base = "http://@environment@.acrasnfe.acras.com.br"
    __url_service_consulta = ""
    __url_service_emission = ""

    def __init__(self, environment, token):
        self.__url_base = self.__url_base.replace("@environment@", environment)
        self.__url_service_consulta = self.__url_base + "/nfse/@ref@?token=@token@"
        self.__url_service_emission = self.__url_base + "/nfse.json?ref=@ref@&token=@token@"
        self.__url_service_cancel = self.__url_base + "/nfse/@ref@?token=@token@"

        self.__url_service_consulta = self.__url_service_consulta.replace("@token@", token)
        self.__url_service_emission = self.__url_service_emission.replace("@token@", token)
        self.__url_service_cancel = self.__url_service_emission.replace("@token@", token)

    def get_nfs_by_ref(self, reference):
        url_to_request = self.__url_service_consulta.replace("@ref@", reference)
        r = requests.get(url_to_request)
        nf_dict = yaml.load(r.text)
        return nf_dict, r.status_code

    def send_request_to_nfs(self, reference, data):
        url_to_request = self.__url_service_emission.replace("@ref@", reference)
        json_data = json.dumps(data)
        r = requests.post(url_to_request, data=json_data)
        nf_dict = yaml.load(r.text)

        # print "..Erro no envio da nota: código HTTP: " + str(r.status_code) + ', mensagem: ' + r.reason
        err_msg = ""
        if r.status_code != 202:
            results = ast.literal_eval(r.content)
            erros = results["erros"]
            err_msg = "  Detalhes dos erros"
            for e in erros:
                err_msg = err_msg = str("\n\r  * " + e["codigo"] + ": " + e["mensagem"])
        return nf_dict, r.status_code, r.reason, err_msg

    def cancel_nfse_by_ref(self, reference):
        url_to_request = self.__url_service_cancel.replace("@ref@", reference)
        r = requests.delete(url_to_request)
        nf_dict = yaml.load(r.text)
        return nf_dict, r.status_code
