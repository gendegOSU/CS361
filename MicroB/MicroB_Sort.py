from datetime import datetime
import zmq


def get_date(item):
    date = item[1]["added"]
    if len(date) == 10:
        date = "0" + date
    return datetime.strptime(date, "%d %b %Y")

if __name__ == "__main__":

    # Setup ZMQ server
    context = zmq.Context()
    server = context.socket(zmq.REP)
    server.bind("tcp://*:5362")

    while True:
        #  Wait for request
        print("\nListening for SORT requests...")
        request = server.recv_json()
        print("Request Received")

        sort_column = request[0]
        sort_order = request[1]
        data = request[2]

        if sort_order == "asc":
            sort_rev = False
        elif sort_order == "dsc":
            sort_rev = True
        else:
            print("Error: Invalid sort order")
            server.send_json([False, f"Invalid sort order, must be 'asc' or 'dsc': {sort_order}"])
            continue

        if sort_column == "name":
            sorted_data = sorted(data.items(), reverse=sort_rev)
            sorted_data = dict(sorted_data)
        elif sort_column == "date":
            sorted_data = sorted(data.items(), reverse=sort_rev, key=get_date)
            sorted_data = dict(sorted_data)
        else:
            print("Error: Invalid sort column")
            server.send_json([False, f"Invalid sort column, must be 'name' or 'date': {sort_column}"])
            continue

        print(f"Sending back list, sorted by {request[0]} in {request[1]} order")
        server.send_json([True, sorted_data])

# Citation:
# Sorting process adapted from https://realpython.com/sort-python-dictionary/
