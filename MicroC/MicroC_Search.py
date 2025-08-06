import zmq


if __name__ == "__main__":

    # Setup ZMQ server
    context = zmq.Context()
    server = context.socket(zmq.REP)
    server.bind("tcp://*:5363")

    while True:
        #  Wait for request
        print("\nListening for SEARCH requests...")
        request = server.recv_json()
        print("Request Received")

        term = request[0].lower()
        data = request[1]
        found_items = dict()
        found_item = False

        for name, properties in data.items():
            search_space = name + " " + properties["type"] + " " + properties["comment"]
            if term in search_space.lower():
                found_items.update({name: properties})
                found_item = True

        if found_item:
            print(f"Sending back list of items that matched the search term {term}")
        else:
            print(f"No items matched {term}, sending response")
        server.send_json(found_items)