from datetime import datetime, timedelta
from typing import Dict

from dsm.epaxos.cmd.state import Command
from dsm.epaxos.net.impl.generic.server import ReplicaAddress, logger


class ReplicaClient:
    def __init__(
        self,
        peer_id: int,
        peer_addr: Dict[int, ReplicaAddress],
    ):
        self.peer_id = peer_id
        self.peer_addr = peer_addr

        self.channel = self.init(peer_id)
        self.blacklisted = []

    def init(self, peer_id: int):
        raise NotImplementedError()

    @property
    def leader_id(self):
        raise NotImplementedError()

    def connect(self, replica_id=None):
        raise NotImplementedError()

    def poll(self, max_wait) -> bool:
        raise NotImplementedError()

    def send(self, command: Command):
        raise NotImplementedError()

    def recv(self):
        raise NotImplementedError()

    def request(self, command: Command, timeout=0.5, timeout_resend=0.05, retries=5):
        assert self.leader_id is not None

        start = datetime.now()

        while True:
            total_to_wait = retries

            poll_result = None

            self.send(command)

            while True:
                poll_result = self.poll(timeout_resend)
                retries -= 1

                if poll_result:
                    rtn = self.recv()
                    # logger.info(f'Client `{self.peer_id}` -> {self.replica_id} Send={command} Recv={rtn.payload}')

                    end = datetime.now()
                    latency = (end - start).total_seconds()
                    return latency, rtn
                elif retries == 0:
                    break
                else:
                    self.send(command)


            # logger.info(f'Client `{self.peer_id}` -> {self.replica_id} RetrySend={command}')
            self.blacklisted = [self._replica_id]
            # logger.info(f'{self.peer_id} Blacklisted {self._replica_id}')
            self.connect()
