import ntplib
import csv
import time
import subprocess
from datetime import datetime


def check_chrony_time(server="pool.ntp.org", csv_file="time_comparison.csv"):
    """
    Checks system time on the chrony/NTP server and compares it with the local time.
    Results are written to a CSV file.

    Args:
        server (str): Address of the chrony/NTP server
        csv_file (str): Name of the CSV file to write results to
    """
    try:
        client = ntplib.NTPClient()
        response = client.request(server, version=3, timeout=5)
        server_time = datetime.fromtimestamp(response.tx_time)

        data = {
            "timestamp_local": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
            "server_time": server_time.strftime("%Y-%m-%d %H:%M:%S.%f"),
            "offset_ms": round(
                response.offset * 1000, 3
            ),  # response.offset is the difference between local and server time in seconds (float)
            "delay_ms": round(
                response.delay * 1000, 3
            ),  # response.delay is the round-trip delay to the server in seconds (float)
            "stratum": response.stratum,
        }

        write_to_csv(csv_file, data)
        print(
            f"{data['timestamp_local']} | Offset: {data['offset_ms']}ms | Delay: {data['delay_ms']}ms | Written to {csv_file}"
        )
        return data

    except ntplib.NTPException as e:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Error: NTP communication - {e}")
        return None
    except Exception as e:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Error: {e}")
        return None


def write_to_csv(filename, data):
    """
    Writes data to a CSV file.
    If the file does not exist, creates a new one with a header.

    Args:
        filename (str): Name of the CSV file
        data (dict): Dictionary with data to write
    """
    import os

    file_exists = os.path.isfile(filename)

    with open(filename, "a", newline="", encoding="utf-8") as csvfile:
        fieldnames = [
            "timestamp_local",
            "server_time",
            "offset_ms",
            "delay_ms",
            "stratum",
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        writer.writerow(data)


if __name__ == "__main__":
    SERVER = "pool.ntp.org"
    CSV_FILE = "time_comparison.csv"
    TIME_DELAY_SECONDS = 30

    print(f"Starting automatic time check every {TIME_DELAY_SECONDS} seconds...")
    print(f"Server: {SERVER}")
    print(f"CSV file: {CSV_FILE}")
    print(f"Press Ctrl+C to stop.\n")

    try:
        while True:
            check_chrony_time(SERVER, CSV_FILE)
            time.sleep(TIME_DELAY_SECONDS)
    except KeyboardInterrupt:
        print("\n\nStopped.")
