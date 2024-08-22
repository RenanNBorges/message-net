import os

from client.c import *
import threading

import sys


def interface():
    t = threading.Thread(target=c.handle_recv)
    t1 = threading.Thread(target=inicio)
    t.start()
    t1.start()


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
            "[1] Mandar mensagem\n[2] Abrir Conversa\n[3] Adicionar na Lista de Contatos\n[4] Mostrar Lista de Contatos\nInput: ")
        match choice:
            case "1":
                dst = input("Digite o ID do destino: ")
                msg = input("Digite a mensagem de até 218 caracteres: ")
                c.send_msg(dst, msg)
            case "2":
                contact_id = input('De quem? ')
                c.send_seen(contact_id)
                c.load_messages(contact_id)
            case "3":
                contact = input('Digite o ID do contato:')
                nick = input('Digite um nickname para o contato')
                print(c.user.save_contact(contact, nick))
            case "4":
                c.user.request_contacts()


def login():
    id = input("Insira o ID: ")
    if c.user.user_exists(id):
        c.user.load_user(id)
        print('eita')
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
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            t.stop()
            sys.exit(130)
        except SystemExit:
            os._exit(130)
