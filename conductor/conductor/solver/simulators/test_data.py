import sys

from conductor.common.music import messaging as music_messaging
from conductor import messaging
from conductor import service

# Used for testing. This file is in .gitignore and will NOT be checked in.
CONFIG_FILE = '/Users/shankar/Documents/ATT/conductor/PyCharmProject' \
              '/conductor/etc/conductor/conductor.conf.sample'


def test_data():
    """Test the Data Service"""

    # Prepare service-wide components (e.g., config)
    conf = service.prepare_service([], config_files=[CONFIG_FILE])

    # Set up the RPC Client
    topic = "data"
    transport = messaging.get_transport(conf=conf)
    target = music_messaging.Target(topic=topic)
    client = music_messaging.RPCClient(conf=conf,
                                       transport=transport,
                                       target=target)

    # Try calling a method (remember, "calls" are synchronous)
    ctxt = {}
    args = {"candidate": {"location_id": "mor01"}}
    response = client.call(ctxt=ctxt,
                           method="get_candidate_location",
                           args=args)
    print("get_candidate_location response: {}".format(response))

if __name__ == "__main__":
    if len(sys.argv) > 1:
        globals()[sys.argv[1]]()
    else:
        print("Specify test_data.")
