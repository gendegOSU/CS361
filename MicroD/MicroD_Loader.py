import hashlib
import json
import os
import zmq


def get_collection_list():
    file_list = []

    files = os.listdir("../collections")
    for filename in files:
        with open("../collections/" + filename, "r") as file:
            data = json.loads(file.read())
            file_list.append((data[0], filename))

    return file_list

def load_collection(name, file_list):
    filename = ""
    for file in file_list:
        if file[0] == name:
            filename = file[1]
            break

    if filename == "":
        return False

    with open("../collections/" + filename, "r") as file:
        data = json.loads(file.read())
    return data

def save_collection(data):
    filename = hashlib.sha256(data[0].encode("utf-8")).hexdigest()
    data = json.dumps(data)

    with open("../collections/" + filename, 'w') as file:
        file.write(data)

if __name__ == "__main__":

    # Setup ZMQ server
    context = zmq.Context()
    server = context.socket(zmq.REP)
    server.bind("tcp://*:5364")

    while True:
        #  Wait for request
        print("\nListening for COLLECTION requests...")
        request = server.recv_json()
        print("Request Received")
        req_type = request[0]

        if req_type == "list": # request = ["list"]
            file_list = get_collection_list()
            collection_list = sorted([name for name, file in file_list])

            print("Sending list of available collections")
            server.send_json([True, collection_list])

        elif req_type == "load": # request = ["load", name, cur_data]
            if request[2][0] is not None:
                save_collection([request[2][0], request[2][1]])
                print(f"Saved {request[2][0]} collection")
            else:
                print("No prior collection to save")

            file_list = get_collection_list()
            response = load_collection(request[1], file_list)

            if response:
                print(f"Sending data for {request[1]}")
                server.send_json([True, response])
            else:
                print(f"Error: Collection {request[1]} not found")
                server.send_json([False, f"Collection {request[1]} not found"])

        elif req_type == "save": # request = ["save", name, values]
            save_collection([request[1], request[2]])
            print(f"Saved record for {request[1]}")
            server.send_json([True, f"Saved record for {request[1]}"])

        else:
            print(f"Error: Request type {req_type} unknown")
            server.send_json([False, f"Request type {req_type} unknown"])
