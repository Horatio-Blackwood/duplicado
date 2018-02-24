import hashlib, os, pprint, sys, time

deleted = 0
duplicates = None

def print_separator():
    print("-" * 80 + "\n")

def print_iter_help():
    print("ITER COMMANDS")
    print_separator()
    print("     help           - prints these options ")
    print("     del <#,#,#...> - deletes the file associated with the number")
    print("                      you entered.  To delete file 2, enter 'del 2'")
    print("                      (without quotes).  To delete files 2 and 5,")
    print("                      enter 'del 2,5' (without quotes).")
    print("     skip           - skips the current duplicate.")
    print("     status         - prints the number of duplicates removed so far")
    print("     quit           - exits the program.")
    print_separator()

def get_time_string(start, end):
    """ Given two times (a start and an end time in seconds) this function
        returns a formatted string showing the difference in hours minutes and
        seconds like so:  HH:MM:SS
    """
    diff = int(end) - int(start)
    seconds = 0
    minutes = 0
    hours = 0
    if diff > 60:
        seconds = diff % 60
        minutes = diff // 60

        if minutes > 60:
            minutes = minutes % 60
            hours = minutes // 60

    else:
        seconds = diff

    return str(hours) + ":" + str(minutes) + ":" + str(seconds)

def handle_item(item):
    """ Prints out the tuple (key, val) pair from the results dict in an easy
        to read fashion.  Allows a user to delete one or more of the files.
    """
    global deleted
    
    # Break out the parts of the 'item'
    hashcode = item[0]    # the hashcode generated by hashing all of the files in the file tuples list.
    file_tuples = item[1] # list of two-tuples with file names and formatted sizes
    
    # Show Output
    for i in range(len(file_tuples)):
        file = file_tuples[i]
        fname = file[0]
        fsize = file[1]
        print("   ", str(i), "- Name: ", fname)
        print("    ", " " * len(str(i)), " Size: ", fsize, "\n")
        

    # Get Input
    not_finished = True
    while(not_finished):
        response = input("Option:")
        response = response.strip().lower()
        # // HELP
        if response == "help":
            print_iter_help()
            not_finished = True

        # // SKIP
        elif response == "skip":
            not_finished = False

        # // DEL
        elif response.startswith("del"):
            # Break up the input command into its valid parts.
            parts = response.split(" ")
            cmd = parts[0]
            indices = parts[1]
            indices = indices.split(",")

            if cmd == "del":
                for index in indices:
                    index = index.strip()
                    index = int(index)
                    if index <= len(file_tuples) - 1:
                        os.remove(file_tuples[index][0])
                        print("File", str(index), "deleted.\n\n")
                        deleted += 1
            not_finished = False

        # STATUS
        elif response == "status":
            print("You deleted", str(deleted), "duplicates out of", str(duplicates) + ".")
            not_finished = True

        # // QUIT
        elif response == "quit":
            not_finished = False
            return 0
                
        

def iterate(dictionary, first_time_here):
    """ Recursively pops an item from the supplied dict and prints out its data then
        prompts the user to confirm if we should pop another item from the dict.
    """

    # Print instructions if its our first call to iterate().
    if (first_time_here):
        print_iter_help()

    # Where the real work gets done
    response = handle_item(dictionary.popitem())
    if response == 0:
        return
    else:
        # Call this recursively...
        iterate(dictionary, False)


def main(directory, bytes_to_read, files_per_status, ignored_extensions):
    """ Given a directory, this function recursively walks the files of that dir
        and creates a checksum of the first 512 bytes of the file.  The checksum
        is used as a key into a dictionary.  Any files with matching checksums
        are added to the list used as the dictionary's value.

        When all files have been scanned, any key/value pairs with only one file
        are removed from the dict and any with duplicates are pretty printed to
        the screen.
    """
    global duplicates
    
    print("Data Dir:", directory)
    print("Bytes to Read", bytes_to_read)
    print("Report status every", files_per_status, "files.")
    print("Ignoring files with the following extensions:\n   - ", ignored_extensions)
    print("")
    
    results = {} # md5 signature -> list of file names
    files_read = 0
    start_time = time.time()

    # Roll over all of the files, hash them and dump them into a dict
    for path, dirs, files in os.walk(directory):
        for filename in files:
            fullname = os.path.join(path, filename)

            # Ignore files iwth ignore extensions
            file_parts = fullname.split('.')
            file_ext = file_parts[len(file_parts) - 1]
            
            if len(file_parts) > 1 and file_ext.lower() not in ignored_extensions:
                #print("Accepted file:  ", filename)
                with open(fullname, 'rb') as f:
                    d = f.read(bytes_to_read)
                    h = hashlib.md5(d).hexdigest()
                    filelist = results.setdefault(h, [])

                    # Get File size in bytes, divide it down to (roughly) megabytes
                    size_megabytes = os.path.getsize(fullname) / 1024 / 1024
                    formatted_megas = str("{0:.2f}".format(size_megabytes)) + " Mb"
                    filelist.append((fullname, formatted_megas))
                    files_read += 1

                    if (files_read % files_per_status == 0):
                        print("Files read:  ", files_read)
                        print("Time elapsed:", get_time_string(start_time, time.time()))
    print_separator()


    # Remove the Files that DON'T have duplicates.
    print("Removing non-duplicates from results.")
    to_remove = []
    for key, value in results.items():
        if len(value) < 2:
            to_remove.append(key)
            
    for key in to_remove:
        del results[key]
    print("Done removing non-duplicates.")
    print_separator()


    # Print out Overall Stats
    duplicates = len(results)
    print("Processing complete.")
    print("Checked ", files_read, "files in ", get_time_string(start_time, time.time()), ",")
    print("Found ", str(duplicates), "files which likely have duplicates.")
    print_separator()

    # BEGIN USER INPUT LOOP
    iterate(results, True)



if __name__ == "__main__":
    directory = "."
    ignored = ['png', 'jpg', 'jpeg', 'gif', 'mp3', 'css', 'js', 'txt']
    
    # Run script on current directory,
    # read in 2048 bytes fo each byte and do the hash on that.
    # print process time/stats every 1000 files.
    main(directory, 2048, 1000, ignored)

    print("You deleted " + str(deleted) + " duplicates.")
