import os, stat

def change_file_write_acces(filename):
    # Try to change chmod to allow group write access
    if os.path.isfile(filename):
        file_stat = os.stat(filename)
        file_mode = file_stat.st_mode
        # Check if the file already has group write permission
        if not stat.S_IWGRP & file_mode:
            try:
                # Change chmod to "-rw-rw-r--"
                os.chmod(filename, stat.S_IRUSR|stat.S_IWUSR|stat.S_IRGRP|stat.S_IWGRP|stat.S_IROTH)
            except:
                print(f">>>>> ERROR! Can't change the read/write access of the file '{filename}'!")
