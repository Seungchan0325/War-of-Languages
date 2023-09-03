from system.network import Network


def global_network_handling(state: str):
    network = Network.instance()

    for sock in network.connection:
        data = network.pick(sock)
        if data is None:
            continue
        msg = data.decode()
        if msg.startswith("get_state"):
            network.recv(sock)
            network.send(sock, state.encode())
            network.close(sock)


class SingletonInstane:
    __instance = None

    @classmethod
    def __get_instance(cls):
        return cls.__instance

    @classmethod
    def instance(cls, *args, **kargs):
        cls.__instance = cls(*args, **kargs)
        cls.instance = cls.__get_instance
        return cls.__instance
