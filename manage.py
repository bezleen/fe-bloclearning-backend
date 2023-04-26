# -*- coding: utf-8 -*-
from gevent import monkey
monkey.patch_all()

# from requests.packages.urllib3.util.ssl_ import create_urllib3_context
# create_urllib3_context()

# import grpc.experimental.gevent as grpc_gevent
# grpc_gevent.init_gevent()

# import grpc._cython.cygrpc
# grpc._cython.cygrpc.init_grpc_gevent()

from src import create_app


app = create_app()


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5002)
