
class FileOperations:
    def write_to_file(self, file_path, data):
        """Function to write data to a file

        Args:
            file_path (string): The path to the file
            data (list): The data to write to the file
        """
        with open(file_path, "w", encoding="utf-8") as file:
            if isinstance(data, str):
                file.write(data)
            elif isinstance(data, list):
                file.write('\n'.join(data))
            else:
                raise TypeError("Data must be a string or a list of strings")

