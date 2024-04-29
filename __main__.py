import os
import sys
import time
# from PIL import Image
import pytz
import exifread
import subprocess
import datetime
import argparse
from win32com.propsys import propsys, pscon



## folder path##
folder = r""

## the counterFile.txt file thet contain the last number of the file##
counterFile = os.path.dirname(__file__) + '/counterFile.txt'

## if True it will start from 0 and rename all files, if False it will not rename the files that allready renamed ##
startfrom0 = True

## the file that you dont want to rename it, add -not to the end of the file name or folder name##
blackList = " -not"

## user os ##
useros = sys.platform


class File:
    def __init__(self, path):
        self.WINpath = path
        self.LINpath = path.replace('\\', '/').replace('C:', '/mnt/c').replace(
            'D:', '/mnt/d').replace('E:', '/mnt/e').replace('F:', '/mnt/f')
        self.root = os.path.dirname(path)
        self.name = os.path.basename(path)
        self.nameWOext = os.path.splitext(self.name)[0]
        self.newName = None
        self.ext = (os.path.splitext(path)[1]).lower()
        self.type = self.type()
        self.atime = os.path.getatime(path)  # Date of last access
        self.mtime = os.path.getmtime(path)  # Date Modified
        self.ctime = os.path.getctime(path)  # Date Created
        self.Dates = [None, None, None, None]
        self.Date = None
        self.renamed = self.Renamed()

    def convDate(self, date):
        try:
            self.datetime = datetime.datetime.fromtimestamp(date)
            self.datetime = self.datetime.replace(tzinfo=pytz.utc)
            self.datetime = self.datetime.astimezone(
                pytz.timezone('Asia/Riyadh'))
            self.datetime = self.datetime.strftime('%Y-%m-%d %I%p')
            return self.datetime
        except:
            print("Error in convDate")
            return None

    def type(self):
        if self.ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.heic', '.dng', '.tif']:
            return 'image'
        elif self.ext in ['.mp4', '.mkv', '.avi', '.mpg', '.mpeg', '.flv', '.wmv', '.mov', '.m4v', ".webm"]:
            return 'video'
        elif self.ext in ['.mp3', '.wav']:
            return 'audio'
        else:
            return 'unknown'

    def Renamed(self):
        try:
            date = time.mktime(datetime.datetime.strptime(
                self.name[0:15], "%Y-%m-%d %I%p").timetuple())

            if self.nameWOext[-7:].isdigit():
                return True
            else:
                return False
        except:
            return False


# ________________________main________________________
def main(folder, counterFile, startfrom0, blackList):

    log = {'renamed': {"image": 0, "video": 0, "audio": 0, "unknown": []},
           'errors': {"image": 0, "video": 0, "audio": 0, "unknown": []}, "currentFolder": None, "errorsFile": None, "startfrom": None, "endat": None, "unknownfile": None}

    # walk through the folder
    for root, dirs, files in os.walk(folder):
        # counter before the folder
        baseCounter = counter = counterFunc(counterFile, 'r', None)
        log["endat"] = counter

        if log["currentFolder"] != None:
            log = logsWrite(log)

        log["startfrom"] = counter
        log["currentFolder"] = root

        if (blackList in root):
            continue

        for file in files:
            counter += 1
            # log number of file
            print(f'file number: {counter - baseCounter}/{len(files)}')

            # get the full path of the file
            path = os.path.join(root, file)
            file = File(path)

            # if true dont rename the file
            if (blackList in file.nameWOext or file.renamed) and (not startfrom0):
                print(f'file: {file.name} is already renamed')
                counter -= 1
                baseCounter -= 1
                continue
            else:
                try:
                    if file.type == 'image':
                        file.Date = file.mtime     

                    elif file.type == 'video':
                        # video
                        file.Date = ExifVideo(file)

                    elif file.type == 'audio':
                        # todo: audio
                        pass
                    else:
                        print(f'file: {file.name} is unknown')
                        log["renamed"]["unknown"] += [
                            os.path.join(file.root, file.name)]
                        log["unknownfile"] = os.path.join(
                            file.root, 'unknown.txt')
                        continue

                    file.newName = newName(file, counter, file.Date)


                    log["renamed"][file.type] += 1
                    print("old name: ", os.path.join(file.root, file.name))
                    print("new name: ", os.path.join(
                        file.root, file.newName))

                    os.rename(os.path.join(file.root, file.name),
                              os.path.join(file.root, file.newName))

                    # check if there is file with the same old name put end with .AAE
                    if os.path.exists(os.path.join(file.root, file.nameWOext + '.AAE')):
                        os.rename(os.path.join(file.root, file.nameWOext + '.AAE'),
                                  os.path.join(file.root, os.path.splitext(file.newName)[0] + '.AAE'))

                    print("Done")
                    print("_______________________________________")

                except Exception as e:
                    print(e)
                    counter -= 1
                    baseCounter -= 1
                    error(file)
                    log["errors"][file.type] += 1
                    log["errorsFile"] = os.path.join(file.root, 'errors.txt')

                # check point
                if counter == 100:
                    counterFunc(counterFile, 'w', counter)
                    print("counter file updated")
                    print("_______________________________________")

        counterFunc(counterFile, 'w', counter)

        print(f"Finished this folder {root}")
        print("_______________________________________")
    log["endat"] = counter
    logsWrite(log)


def logsWrite(log):

    with open("log.txt", 'a', encoding='utf-8') as f:
        f.write(
            f'folder: {log["currentFolder"]}\n-------\n')
        if log["startfrom"] != None:
            f.write(
                f'start from ({log["startfrom"]}) to ({log["endat"]})\n')
        f.write(
            f"there is ({log['renamed']['image']}) images and ({log['renamed']['video']}) videos and ({log['renamed']['audio']}) audio has been renamed")
        if log['unknownfile'] != None:
            f.write(
                f"\nand ({len(log['renamed']['unknown'])}) unknown files we can't rename it\nto see the files check ({log['unknownfile']})\n\n")
            with open(log['unknownfile'], 'w', encoding='utf-8') as f2:
                for file in log['renamed']['unknown']:
                    f2.write(file + "\n")
        else:
            f.write("\n\n")
        if log["errorsFile"] != None:
            f.write(
                f'there is ({log["errors"]["image"]}) images and ({log["errors"]["video"]}) videos and ({log["errors"]["audio"]}) audio and ({log["errors"]["unknown"]}) unknown has error\n to see the errors check ({log["errorsFile"]})\n\n')
        f.write(
            "_"*50+"\n\n")
    return {'renamed': {"image": 0, "video": 0, "audio": 0, "unknown": []},
            'errors': {"image": 0, "video": 0, "audio": 0, "unknown": []}, "currentFolder": None, "errorsFile": None, "startfrom": None, "endat": None, "unknownfile": None}


def checkName(file):
    if file[:2] == '20':
        try:
            if "am" in file.lower() or "pm" in file.lower():
                try:
                    if "am" in file.lower():
                        date = time.mktime(datetime.datetime.strptime(
                            file.split("am")[0].strip(), "%Y-%m-%d %I").timetuple())
                    elif "pm" in file.lower():
                        date = time.mktime(datetime.datetime.strptime(
                            file.split("pm")[0].strip(), "%Y-%m-%d %I").timetuple())
                        date += 43200
                except:
                    if "am" in file.lower():
                        date = time.mktime(datetime.datetime.strptime(
                            file.split("am")[0].strip(), "%Y:%m:%d %I").timetuple())
                    elif "pm" in file.lower():
                        date = time.mktime(datetime.datetime.strptime(
                            file.split("pm")[0].strip(), "%Y:%m:%d %I").timetuple())
                        date += 43200
            else:
                try:
                    date = time.mktime(datetime.datetime.strptime(
                        file[file.index("20"):file.index("20")+10], "%Y-%m-%d").timetuple())
                except:
                    date = time.mktime(datetime.datetime.strptime(
                        file[file.index("20"):file.index("20")+10], "%Y:%m:%d").timetuple())
        except:
            pass
        else:
            return date
    else:
        return None


def newName(file, counter, date):
    date = file.convDate(date)
    newName = f'{date} {counter:07d}{file.ext}'
    return newName


def error(file):
    # write the new name to errors.txt
    with open(os.path.join(file.root, 'errors.txt'), 'a', encoding='utf-8') as f:
        f.write(
            f'{os.path.join(file.root, file.name)}\n{os.path.join(file.root, str(file.newName))}\n\n')
    print(
        "\033[91m" + "_________________________error_________________________" + "\033[0m")
    print(f"oldName: {os.path.join(file.root, file.name)}")
    print(
        "\033[91m" + "_________________________error_________________________" + "\033[0m")


def counterFunc(counterFile, mode, counter):
    if 'r' in mode:
        with open(counterFile, mode) as f:
            counter = int(f.read())
        return counter
    elif 'w' in mode:
        with open(counterFile, mode) as f:
            f.write(str(counter))


def ExifVideo(file: File):
    """

    Get the date taken from the exif data


    """

    # get the date from the video
    try:
        if useros == 'win32':
            date = propsys.SHGetPropertyStoreFromParsingName(file.WINpath)
            date = date.GetValue(pscon.PKEY_Media_DateEncoded).GetValue()
            date = time.mktime(date.timetuple())
        elif useros == 'linux':
            date = os.path.getmtime(file)
    except:
        if file.mtime:
            date = file.mtime
        else:
            date = checkName(file.name)
    return date


def ExifImage(file):
    """
    Get the date taken from the exif data

    Only in linux
    """
    try:
        with open(file.WINpath, 'rb') as f:
            tags = exifread.process_file(f, stop_tag='EXIF DateTimeOriginal')
        if 'EXIF DateTimeOriginal' in tags:
            date = tags['EXIF DateTimeOriginal']
            date = date.values
            date = time.mktime(datetime.datetime.strptime(
                date, "%Y:%m:%d %H:%M:%S").timetuple())
        else:
            date = file.mtime
    except:
        # if there is no exif data
        date = checkName(file.name)
        if not date:
            date = file.mtime
    return date


def ExifHeic(file):
    """
    Get the date taken from the exif data
    you may use it or use os.path.getmtime(file)

    you need to install imagemagick and wsl
    """
    # run it on wsl

    try:
        # todo: fix it fo linux
        output = subprocess.Popen(
            ['wsl', 'identify', '-format', '%[EXIF:*]', file.LINpath], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        output, err = output.communicate()
        output = output.decode('utf-8')
        if output:
            output = output.split()
            for line in output:
                if "DateTimeOriginal" in line:
                    date = f'{line.split("=")[1].strip()} {output[output.index(line)+1]}'
                    file.Dates[0] = time.mktime(datetime.datetime.strptime(
                        date, "%Y:%m:%d %H:%M:%S").timetuple())
                    break
                elif "DateTime" in line:
                    date = f'{line.split("=")[1].strip()} {output[output.index(line)+1]}'
                    file.Dates[2] = time.mktime(datetime.datetime.strptime(
                        date, "%Y:%m:%d %H:%M:%S").timetuple())
                elif "DateTimeDigitized" in line:
                    date = f'{line.split("=")[1].strip()} {output[output.index(line)+1]}'
                    file.Dates[3] = time.mktime(datetime.datetime.strptime(
                        date, "%Y:%m:%d %H:%M:%S").timetuple())

    except:
        pass

    file.Dates[1] = checkName(file.name)

    # for i in range(len(file.Dates)) if not none return the date
    for i in range(len(file.Dates)):
        if file.Dates[i]:
            return file.Dates[i]


# for args
def isdir(path):
    if os.path.isdir(path):
        return path
    else:
        raise argparse.ArgumentTypeError(
            f"readable_dir:{path} is not a valid path")


def isfile(path):
    if os.path.isfile(path):
        return path
    else:
        raise argparse.ArgumentTypeError(
            f"readable_dir:{path} is not a valid path")


def checks():
    if useros == 'win32':
        # check if wsl is installed
        pass
    elif useros == 'linux':
        # check if imagemagick is installed
        try:
            subprocess.check_output(['identify'])
        except:
            print("imagemagick is not installed")
            print("in ubuntu run: sudo apt install imagemagick")
            exit()
        try:
            subprocess.check_output(['exiftool'])
        except:
            print("exiftool is not installed")
            print("in ubuntu run: sudo apt install exiftool")
            exit()
    else:
        print("your os is not supported")
        exit()

    global folder, counterFile

    # check if the folder is exist
    if not os.path.exists(folder):
        # reformat the path
        folder = folder.replace('\\', '/').replace('C:', '/mnt/c').replace(
            'D:', '/mnt/d').replace('E:', '/mnt/e').replace('F:', '/mnt/f')
        if not os.path.exists(folder):
            print("folder is not exist")
            exit()

    # check if the counterFile is exist
    if not os.path.exists(counterFile):
        # reformat the path
        counterFile = counterFile.replace('\\', '/').replace('C:', '/mnt/c').replace(
            'D:', '/mnt/d').replace('E:', '/mnt/e').replace('F:', '/mnt/f')
        if not os.path.exists(counterFile):

            print("counterFile is not exist\nso we will create it and will restart the numbering from 0")
            with open(counterFile, 'w') as f:
                f.write('0')
            exit()


if __name__ == '__main__':
    checks()

    # get args from command line
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--folder', help='folder path', type=isdir)
    parser.add_argument('-c', '--counterFile',
                        help='counterFile path', type=isfile)
    parser.add_argument('-s', '--startfrom0',
                        help='start from 0 and rename all files', type=bool)
    parser.add_argument(
        '-b', '--blackList', help='the file that you dont want to rename it, add -not to the end of the file name or folder name')
    args = parser.parse_args()

    if args.folder:
        folder = args.folder
        print(f'folder: {folder}')
    if args.counterFile:
        counterFile = args.counterFile
    if args.startfrom0:
        startfrom0 = args.startfrom0
    if args.blackList:
        blackList = args.blackList

    with open("log.txt", 'w', encoding='utf-8') as f:
        f.write(
            f'folder: {folder}\ncounterFile: {counterFile}\nstartfrom0: {startfrom0}\nblackList: {blackList}\n\n')
        f.write(
            "_"*20+"\n\n")

    main(folder, counterFile, startfrom0, blackList)

    print("Done\n\n")

    print("You can check the errors.txt file for errors\nYou will find it in the each folder has error\n\n")
    print("You can check the log.txt file for the args\nYou will find it in this path: ",
          os.path.abspath("log.txt"))

    with open("log.txt", 'a') as f:
        f.write("Done")
