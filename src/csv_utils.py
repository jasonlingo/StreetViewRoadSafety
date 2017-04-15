import csv


def outputCSV(dataset, filename):
    """
    Output dataSet to a csv file

    Args:
      dataSet: (list) the data set to be written to a csv file
      filename: (str) the output csv file name
    """
    with open(filename, 'a') as output:  # Open a csv file
        writer = csv.writer(output, lineterminator='\n')

        # Write data to a csv file one record a line
        for val in dataset:
            writer.writerow(val)
    output.close()