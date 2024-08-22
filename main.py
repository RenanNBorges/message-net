import os

from client.c import *
import threading

import sys


def interface():
    t = threading.Thread(target=c.handle_recv)
    t1 = threading.Thread(target=inicio)
    t.start()
    t1.start()

def get_members():
    members = []
    for i in range(7):
        member = input("Insira o ID do membro:\n[0] para Finalizar\n[#] Voltar Ao Menu")
        match member:
            case "0":
                if len(members) < 1:
                    print("Número insuficiente!")
                    return get_members()
                else:
                    return members
            case "#":
                return False
            case other:
                members.append(member)


def menu():
    timeout = 0
    while not c.conn_user():
        sleep(1)
        timeout += 1
        if timeout == 10:
            print('Failed')
            return inicio()
            break

    while True:
        print("### Menu ###")
        choice = input(
            "[1] Mandar mensagem\n[2] Abrir Conversa\n[3] Adicionar na Lista de Contatos\n[4] Mostrar Lista de Contatos\n[5]Criar GrupoInput: ")
        match choice:
            case "1":
                dst = input("Digite o ID do destino: ")
                msg = input("Digite a mensagem de até 218 caracteres: ")
                if not c.send_msg(dst, msg):
                    print("Lenght Error")
            case "2":
                contact_id = input('De quem? ')
                c.send_seen(contact_id)
                c.user.load_messages(contact_id)
            case "3":
                contact = input('Digite o ID do contato:')
                nick = input('Digite um nickname para o contato')
                print(c.user.save_contact(contact, nick))
            case "4":
                c.user.request_contacts()
            case "5":
                members_list = get_members()
                if members_list:
                    c.create_new_gp(members_list)


def login():
    id = input("Insira o ID: ")
    if len(id) == 13:
        c.user.load_user(id)
        return menu()
    return inicio()


def inicio():
    try:
        choice = int(input("### CHAT ###\n[0] Registrar\n[1] Login\n[2] Exit\nInput:"))
        match choice:
            case 0:
                c.request_register()
                return menu()
            case 1:
                login()
            case 2:
                print('b')
                c.__del__()
                return exit(0)
    except Exception as e:
        print(e)
        c.__del__()


global t_active
t_active = True
c = Client()


def main():
    interface()


if __name__ == '__main__':
    main()