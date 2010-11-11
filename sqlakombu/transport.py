from Queue import Empty

from anyjson import serialize, deserialize
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker

from kombu.transport import virtual

from sqlakombu.models import Queue, Message, metadata


class Channel(virtual.Channel):
    _session = None
    _engines = {}   # engine cache

    def _open(self):
        conninfo = self.connection.client
        if conninfo.hostname not in self._engines:
            engine = create_engine(conninfo.hostname)
            Session = sessionmaker(bind=engine)
            metadata.create_all(engine)
            self._engines[conninfo.hostname] = engine, Session
        return self._engines[conninfo.hostname]

    @property
    def session(self):
        if self._session is None:
            _, Session = self._open()
            self._session = Session()
        return self._session

    def _get_or_create(self, queue):
        obj = self.session.query(Queue).filter(Queue.name == queue) \
                    .first()
        if not obj:
            obj = Queue(queue)
            self.session.add(obj)
            try:
                self.session.commit()
            except OperationalError:
                self.session.rollback()
        return obj

    def _new_queue(self, queue, **kwargs):
        self._get_or_create(queue)

    def _put(self, queue, payload, **kwargs):
        obj = self._get_or_create(queue)
        message = Message(serialize(payload), obj)
        self.session.add(message)
        try:
            self.session.commit()
        except OperationalError:
            self.session.rollback()

    def _get(self, queue):
        obj = self._get_or_create(queue)
        msg = self.session.query(Message) \
                    .filter(Message.queue_id == obj.id) \
                    .filter(Message.visible != False) \
                    .order_by(Message.sent_at) \
                    .order_by(Message.id) \
                    .limit(1) \
                    .first()
        if msg:
            msg.visible = False
            self.session.commit()
            return deserialize(msg.payload)
        raise Empty()

    def _query_all(self, queue):
        obj = self._get_or_create(queue)
        return self.session.query(Message) \
                .filter(Message.queue_id == obj.id)

    def _purge(self, queue):
        count = self._query_all(queue).delete(synchronize_session=False)
        try:
            self.session.commit()
        except OperationalError:
            self.session.rollback()
        return count

    def _size(self, queue):
        return self._query_all(queue).count()


class Transport(virtual.Transport):
    Channel = Channel

    default_port = 0
    connection_errors = ()
    channel_errors = ()
