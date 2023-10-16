import os, stat

def change_file_write_acces(filename):
    # Change chmod to allow group write access
    if os.path.isfile(filename):
        try:
            os.chmod(filename, stat.S_IRUSR|stat.S_IWUSR|stat.S_IRGRP|stat.S_IWGRP|stat.S_IROTH)
        except:
            print(f">>>>> ERROR! Can't change the read/write access of the file '{filename}'!")
