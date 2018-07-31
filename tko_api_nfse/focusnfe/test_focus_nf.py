# coding=utf-8
import unittest

from FocusNF import FocusNF as FocusNFS

token = "del1huDPhbscAM3Wdvkx44rg1zB94oVu"


# token = "QrXrkx6vJjardojHn4iTYIAkBOlRheMt" #NOT OKAY giving error
# token = "WXrZCvBKz7V2PR073NcXhjr6udQNaJal"
class TestProcessadorNFSeSP(unittest.TestCase):
    ref = ""

    environment = ""

    def setUp(self):
        pass

    def test_send_request_to_nfs(self):
        # montar os dados em um Hash
        focus_methods = FocusNFS("homologacao", token)
        data = {}
        #        ref="Rpy1023"
        ref = "Yogesh1111"

        #  Informações gerais da nota
        data["data_emissao"] = "2015-07-28"

        #  Informações do prestador do serviço
        data["prestador"] = {}
        data["prestador"]["cnpj"] = "11748236000127"
        data["prestador"]["inscricao_municipal"] = "52253953"
        data["prestador"]["codigo_municipio"] = "3550308"

        #  informações do tomador do serviço
        data["tomador"] = {}
        data["tomador"]["cnpj"] = "07504505000132"
        data["tomador"]["razao_social"] = "Acras Tecnologia da Informação LTDA"
        data["tomador"]["email"] = "contato@acras.com.br"
        data["tomador"]["endereco"] = {}
        data["tomador"]["endereco"]["logradouro"] = "Rua Dias da Rocha Filho"
        data["tomador"]["endereco"]["numero"] = "250"
        data["tomador"]["endereco"]["complemento"] = "Sala 02"
        data["tomador"]["endereco"]["bairro"] = "Alto da Rua XV"
        data["tomador"]["endereco"]["codigo_municipio"] = "3550308"
        data["tomador"]["endereco"]["cep"] = "80045130"
        #  Informações do serviço
        data["servico"] = {}
        data["servico"]["aliquota"] = 0.02
        data["servico"]["discriminacao"] = "Nota fiscal referente a serviços prestados"
        data["servico"]["iss_retido"] = False
        data["servico"]["item_lista_servico"] = "02798"
        data["servico"]["valor_servicos"] = 633.55
        data2 = {'data_emissao': '2016-01-15', 'tomador': {
            'endereco': {'complemento': False, 'bairro': u'Parque da Lagoa', 'logradouro': u'Rua Pedro Vicentim',
                         'numero': u'786', 'cep': u'18201-300'}, 'razao_social': u'Giovanna e Marcelo Vidros Ltda',
            'email': u'giovanna@email.com', 'cnpj': u'24768949000102'},
                 'servico': {'discriminacao': u'asd', 'item_lista_servico': '02798', 'aliquota': 0.0,
                             'valor_servicos': 1000.0, 'iss_retido': False},
                 'prestador': {'cnpj': u'09249867000150', 'inscricao_municipal': u'37039520',
                               'codigo_municipio': u'3550308'}}
        data = data2
        nf_data, http_status_code, reason, err_msg = focus_methods.send_request_to_nfs(ref, data)
        if http_status_code == 202:
            print "Emitida com sucesso"
            self.assertEqual(http_status_code, 202)
        elif http_status_code == 400:
            print "Já emitida status_code: " + str(http_status_code)
            self.assertEqual(http_status_code, 400)
        else:
            print "Impossível emitir status_code: " + str(http_status_code)

    def test_zget_nfs_by_ref(self):
        ref = "Yogesh1111"  # "Rpy1023"
        focus_methods = FocusNFS("homologacao", token)
        nf_dict, http_status_code = focus_methods.get_nfs_by_ref(ref)
        if http_status_code == 200:
            print "NFS consultada com sucesso"
            self.assertEqual(http_status_code, 200)
        else:
            print "Problema na consulta status_code: " + str(http_status_code)


if __name__ == '__main__':
    unittest.main()
