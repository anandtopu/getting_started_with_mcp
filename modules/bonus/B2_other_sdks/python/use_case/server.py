"""Bonus host entry point. Protocol-only stdout."""

from common.notes import notes_server

server = notes_server()
if __name__ == "__main__":
    server.run()
