
## RenameMe

This Python script automates the renaming of files (images, videos) within a specified folder and its subfolders. Files are renamed in the format "YYYY-MM-DD HH[AM/PM] #######.[ext]", where:

* **YYYY-MM-DD**: Date the file was created/modified.
* **HH**: Hour (12-hour format).
* **[AM/PM]**: AM or PM.
* **#######**: A 7-digit counter to ensure unique names.
* **[ext]**: Original file extension.

### Features:

* **Automatic Renaming**: Renames files based on creation/modification date and a unique counter.
* **File Type Support**: Handles images (JPG, PNG, etc.), videos (MP4, MKV, etc.).
* **EXIF Data Extraction**: Extracts date information from image and video metadata where available.
* **Counter File**: Uses a text file to store the current counter value, allowing resumption from the last renamed file.
* **Blacklist**: Allows excluding specific files or folders from renaming using a "-not" suffix in their names.
* **Error Handling**: Logs errors to a separate file for review and troubleshooting.
* **Logging**: Creates a log file ("log.txt") documenting the renaming process, including errors and file counts.
* **Cross-Platform**: Supports Windows and Linux (requires additional installations - see below).

### Requirements:

* **Python 3**: Ensure you have Python 3 installed on your system.
* **Additional Libraries**: Install the required Python libraries using `pip install -r requirements.txt`.
* **Windows Specific**:
    * No additional requirements.
* **Linux Specific**:
    * **imagemagick**: Install using your package manager (e.g., `sudo apt install imagemagick`).
    * **exiftool**: Install using your package manager (e.g., `sudo apt install exiftool`).

### Usage:
1. **Installation**:
    * Clone the repository using: \
     `git clone https://github.com/FS-17/RenameMe.git`.
    * Install the required libraries using: \
    `pip install -r requirements.txt`.


1. **Configuration**: 
     * **Command Line**: 
        * Run `python __main__.py -h` to view the available options.
    
        * Optional arguments:
            * `-f/--folder`: Specify the folder path.
            * `-c/--counterFile`: Specify the counter file path, default is "<project_folder>/counter.txt".

            * `-s/--startfrom0`: Set to `True` to start the counter from 0, default is `False`.

            * `-b/--blackList`: Specify the blacklist suffix, default is "-not", any file/folder with this suffix will be excluded from renaming.

        * Example:
            * `python __main__.py -f "C:\Users\user\Desktop\Photos"`.


### Notes:

* The script uses creation/modification date for renaming. For more accurate timestamps, ensure your system clock is synchronized.
* Review the "errors.txt" file in each folder for any files that could not be renamed. 
* The "log.txt" file provides a comprehensive record of the renaming process and script settings.

### Disclaimer:

Use this script at your own risk. While it has been tested, it is recommended to back up your files before running the script. 

