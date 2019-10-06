# -*- coding: utf-8 -*-
import sys
from ktask import app
if __name__ == '__main__':
    port = 8000
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    host = '0.0.0.0'
  #  print app.url_map
    app.run(host=host, port=port, debug=True)
