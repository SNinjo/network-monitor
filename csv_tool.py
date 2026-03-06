import csv

def create(filename, headers):
    with open(filename, mode='w', newline='') as file:
        csv.writer(file).writerow(headers)

def write(filename, data):
    with open(filename, mode='a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(data)
