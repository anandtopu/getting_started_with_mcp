"""Bonus host entry point. Protocol-only stdout."""

from common.skills_extension import skills_server

server = skills_server()
if __name__ == "__main__":
    server.run()
