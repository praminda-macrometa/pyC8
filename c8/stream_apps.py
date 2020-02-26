from c8.api import APIWrapper
from c8.request import Request
from c8.response import Response
from c8.exceptions import (
    StreamAppChangeActiveStateError
)

class StreamApps(APIWrapper):
    """Base class for collection API wrappers.

    :param connection: HTTP connection.
    :type connection: c8.connection.Connection
    :param executor: API executor.
    :type executor: c8.executor.Executor
    :param name: Collection name.
    :type
    """

    def __init__(self, connection, executor, name):
        super(StreamApps, self).__init__(connection, executor)
        self._name = name
        self._id_prefix = name + '/'

    @property
    def name(self):
        """Return stream app name.

        :return: stream app name.
        :rtype: str | unicode
        """
        return self._name
  
    def update(self,data):
        """updates the stream app
        """
        req = Request(
            method = "put",
            endpoint='/_api/streamapps/{}'.format(self.name),
            data=data
        )
        
        def response_handler(resp):
            if resp.is_success is True:
                return resp.body["streamApps"]
            return resp.body
        
        return self._execute(req,response_handler)

    def change_state(self,active):
        """enable or disable stream app
        """
        params = {"active":active}
        
        req = Request(
            method = "patch",
            endpoint='/_api/streamapps/{}/active'.format(self.name),
            params=params
        )
        
        def response_handler(resp):
            if resp.is_success is not True:
                raise StreamAppChangeActiveStateError(resp,req)
            return resp.body["streamApps"]
        
        return self._execute(req,response_handler)

    def get(self):
        """gets the stream app by name
        """
        req = Request(
            method = "get",
            endpoint='/_api/streamapps/{}'.format(self.name),
        )
        
        def response_handler(resp):
            if resp.is_success is True:
                return resp.body["streamApps"]
            return False
        
        return self._execute(req,response_handler)

    def delete(self):
        """deletes the stream app by name
        """
        req = Request(
            method = "delete",
            endpoint='/_api/streamapps/{}'.format(self.name),
        )

        def response_handler(resp):
            if resp.is_success is True:
                return True
            return False

        return self._execute(req,response_handler)

    def query(self,data):
        """query the stream app by name
        """
        req = Request(
            method = "post",
            endpoint='/_api/streamapps/query/{}'.format(self.name),
            data=data
        )

        def response_handler(resp):
            if resp.is_success is True:
                return True
            return False
        
        return self._execute(req,response_handler)