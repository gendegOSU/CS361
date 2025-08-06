
import zmq
import json
import csv


def run_microservice_a_export_csv() -> None:
    """
    Listens on port 5361 for JSON data to save in a CSV file on the user's local machine. Sends a success/error
    response back to the calling entity.

    :return: None
    """

    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:5361")

    print("Microservice is listening on port 5361...")

    while True:
        message = socket.recv()

        # Try / Except block to handle invalid message formats
        try:
            data = json.loads(message)
            filename = data[0]
            records = data[1]

            # Check if CSV file is requested
            if not filename.endswith(".csv"):
                raise ValueError("Invalid data format - not a CSV file")

            # Check if overall 'records' formatted as a dictionary
            if not isinstance(records, dict):
                raise ValueError("Invalid data format - not a dictionary")

            # Check to ensure each nested 'value' is a dictionary
            for value in records.values():
                if not isinstance(value, dict):
                    raise ValueError("Invalid data format - not a nested dictionary")

                # Checking each nested dictionary for if each property is a string
                for prop_val in value.values():
                    if not isinstance(prop_val, str):
                        raise ValueError("Invalid data type - not a string")

            # Write data to file in CSV format on local machine, functionally exporting it to CSV - uses CSV import
            with open(filename, mode="w", newline='', encoding='utf-8') as exported_csv_file:
                headers = ["Name", "Type", "Date Added", "Comment"]
                row_writer = csv.writer(exported_csv_file)
                row_writer.writerow(headers)

                for name, details in records.items():
                    csv_row = [
                        name,
                        details.get("type", "N/A"),  # N/A to catch keys with typos
                        details.get("added", "N/A"),
                        details.get("comment", "N/A")
                    ]

                    row_writer.writerow(csv_row)

            # Send success response back to source of request
            print("Successfully exported data to CSV file. Letting calling service know...")
            socket.send_string(f"Success: File saved as {filename}")

        # Send error response back to source of request if one occurred
        except ValueError as error_msg:
            print(f"Error: {error_msg}")
            socket.send_string(f"Error: {error_msg}")


if __name__ == "__main__":
    run_microservice_a_export_csv()
