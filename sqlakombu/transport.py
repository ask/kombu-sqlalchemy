from Queue import Empty

from anyjson import serialize, deserialize
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from kombu.transport import virtual

from sqlakombu.models import Queue, Message


class Channel(virtual.Channel):
    _session = None
    _engines = {}   # engine cache

    def _open(self):
        conninfo = self.connection.client
        if conninfo.host not in self._engines:
            engine = sqlalchemy.create_engine(conninfo.host)
            Session = sessionmaker(bind=engine)
            metadata.create_all(engine)
            self._engines[conninfo.host] = engine, Session
        return self._engines[conninfo.host]

    @property
    def session(self):
        if self._session is None:
            _, Session = self._open()
            self._session = Session()
        return self._session

    def _get_or_create_queue(self, queue):
        obj = self.session.query(Queue).filter(Queue.name == queue) \
                    .first()
        if not obj:
            obj = Queue(queue)
            self.session.add(obj)
            self.session.commit()
        return obj

    def _new_queue(self, queue, **kwargs):
        self._get_or_create(queue)

    def _put(self, queue, message, **kwargs):
        obj = self._get_or_create(queue)
        message = Message(serialize(payload), queue)
        self.session.add(message)
        self.session.commit()

    def _get(self, queue):
        obj = self._get_or_create(queue)
        msg = self.session.query(Message) \
                    .filter(Message.queue_id == obj.id) \
                    .filter(Message.visible != 0) \
                    .order_by(Message.sent_at) \
                    .order_by(Message.id) \
                    .limit(1) \
                    .first()
        if msg:
            msg.visible = False
            self.session.commit()
            return deserialize(msg.payload)

    def _query_all(self, queue):
        obj = self._get_or_create(queue)
        return self.session.query(Message) \
                .filter(queue_id == obj.id)

    def _purge(self, queue):
        count = self._query_all(queue).delete(synchronize_session=False)
        self.session.commit()
        return count

    def _size(self, queue):
        return self._query_all(queue).count()


class Transport(virtual.Transport):
    Channel = Channel

    default_port = 0
    connection_errors = ()
    channel_errors = ()
