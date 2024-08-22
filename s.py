from dataclasses import dataclass, field
from datetime import datetime, timezone
from random import randint
from socket import *
from typing import Optional, List
import threading

from setuptools.command.build_ext import if_dl

ID_LEN = 13

@dataclass(slots=True)
class Server:
    HOST: Optional[str] = '127.0.0.1'
    PORT: int = 19033
    users: dict = field(default_factory=dict)
    online: dict = field(default_factory=dict)
    server: socket = socket(AF_INET, SOCK_STREAM)

    def __del__(self):
        """Método da classe para fehcar o soquete adequadamente ao ser deletado"""
        self.server.close()

        print('Server closed')

    @staticmethod
    def gen_id(self, type_id : str):
        match type_id:
            case 'U':
                id = '0'
            case 'G':
                id = '1'

        return id + ''.join(str(randint(0, 9)) for _ in range(1, ID_LEN))

    def run(self):
        """Método que roda o servidor e o deixa escutando novas conexões com vários clientes"""
        self.server.bind((self.HOST, self.PORT))
        self.server.listen()
        print("Servidor Aberto para Conexões")
        try:
            while True:
                try:
                    client, addr = self.server.accept()
                    print(f'Conexão estabelecida com {client.getpeername()}')
                    t_listen = threading.Thread(target=self.listen_client, args=[client])
                    t_listen.start()
                except OSError as e:
                    print(f"Erro de rede: {e}")
                except Exception as e:
                    print(f"Erro inesperado: {e}")
        except KeyboardInterrupt:
            print("Servidor interrompido manualmente.")
        finally:
            self.__del__()  # ou `self.server.close()`

    def listen_client(self, client: socket):
        while True:
            try:
                data = client.recv(1024)
                if not data:
                    print(f'Client {client.getpeername()} disconnected')
                    del self.online[client]
                    client.close()
                    break
                recv = self.handle_request(client, data.decode())
                print(recv)
            except:
                break

    def register_user(self, client):
        while True:
            user_id = '0' + ''.join(str(randint(0, 9)) for _ in range(1, ID_LEN))
            if user_id not in self.users:
                break

        try:
            client.send(f'02{user_id}'.encode())
            self.users[user_id] = client
            return f'[{user_id}]'
        except Exception as e:
            return '[FAILED]'

    def user_online(self, client: socket, user_id: str):
        try:
            self.users[user_id] = client
            self.online[client] = user_id
            return f'[{user_id}]'
        except Exception:
            return '[NOT FOUND]'

    def forward_msg(self, src_id: str, dst_id: str, timestamp: str, data: str):
        dst_socket = self.users[dst_id]
        print('entrei no encaminhameno')
        print(f'[{src_id}][{dst_id}][{timestamp}]{data}]')
        if dst_id in self.online.values():
            msg = f'06{src_id}{dst_id}{timestamp}{data}'
            try:
                dst_socket.send(msg.encode())
                ts = datetime.fromtimestamp(int(timestamp)).strftime('%Y-%m-%d %H:%M:%S')
                self.confirm_rcv(src_id=src_id, dst_id=dst_id)
                return f'[{src_id}][{dst_id}][{ts}][{data}]'
            except:
                return ['FAILED']


    def confirm_rcv(self, src_id : str, dst_id : str):
        client_socket = self.users[src_id]
        timestamp = int(datetime.now(tz=timezone.utc).timestamp())
        msg = f'07{dst_id}{str(timestamp)}'
        try:
            client_socket.send(msg.encode())
        except Exception as e:
            print(f'Erro ao confirmar recebimento: {e}')

    def warn_seen_to(self, client_socket : socket, src_id : str, timestamp : str):
        dst_id = self.online[client_socket]
        src_socket = self.users[src_id]
        try:
            src_socket.send(f'09{dst_id}{timestamp}'.encode())
            ts = datetime.fromtimestamp(int(timestamp)).strftime('%Y-%m-%d %H:%M:%S')
            return f'[{dst_id}][{ts}]'
        except Exception as e:
            return '[FAILED]'


    def seen_from(self, client : socket, src_id : str, timestamp : str):
        print(f'[SEEN][{src_id}][{timestamp}]')
        return '[09]' + self.warn_seen_to(client_socket=client, src_id=src_id, timestamp=timestamp)

    def new_group(self):
        """

        :return:
        """


    def handle_request(self, client_socket: socket, data: str):
        print('a')
        match (data[:2]):
            case '01':
                print('[REG*]' + self.register_user(client_socket))
            case '03':
                print('[*ON*]' + self.user_online(client=client_socket, user_id=data[2:]))
            case '05':
                print('oi', data)
                return '[SEND]' + self.forward_msg(src_id=data[2:15], dst_id=data[15:28], timestamp=data[28:38], data=data[38:])
            case '08':
                return self.seen_from(client=client_socket, src_id=data[2:15], timestamp=data[15:])
            case '10':
                creator_id = self.online[client_socket]
                members = [data[i:i+13] for i in range(28, len(data), 13)]
                group_id = self.new_group(creator_id, members)
                return f'[GROUP CREATED]{group_id}'
            case other:
                print('oi', data[:2],)
                return
    



s = Server()
s.run()
