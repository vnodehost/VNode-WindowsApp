import sys, os
import subprocess
from tkinter import Tk, filedialog
from tkinter import *
import json
from cryptography.fernet import Fernet
from threading import Thread
from hurry.filesize import size
from functools import partial
import requests
import time
import extract
from tqdm import tqdm
import os
import sys
from pathlib import Path
import requests
import webbrowser

# This example script downloads python program for mac.
# Home directory of Mac, pathlib.Path module make this easy.
#home_path = Path.home()
# This is the sub directory under home directory.
#sub_path = "tmp"
# The download link of python.
#url = "https://www.python.org/ftp/python/3.8.5/python-3.8.5-macosx10.9.pkg"

# The header of the dl link has a Content-Length which is in bytes.
# The bytes is in string hence has to convert to integer.
#filesize = int(requests.head(url).headers["Content-Length"])

# os.path.basename returns python-3.8.5-macosx10.9.pkg,
# without this module I will have to manually split the url by "/"
# then get the last index with -1.
# Example:
# url.split("/")[-1]
#filename = os.path.basename(url)

# make the sub directory, exists_ok=True will not have exception if the sub dir does not exists.
# the dir will be created if not exists.
#os.makedirs(os.path.join(home_path, sub_path), exist_ok=True)

# The absolute path to download the python program to.
#dl_path = os.path.join(home_path, sub_path, filename)
#chunk_size = 1024

# Use the requests.get with stream enable, with iter_content by chunk size,
# the contents will be written to the dl_path.
# tqdm tracks the progress by progress.update(datasize)
#with requests.get(url, stream=True) as r, open(dl_path, "wb") as f, tqdm(
#        unit="B",  # unit string to be displayed.
#        unit_scale=True,  # let tqdm to determine the scale in kilo, mega..etc.
#        unit_divisor=1024,  # is used when unit_scale is true
#        total=filesize,  # the total iteration.
#        file=sys.stdout,  # default goes to stderr, this is the display on console.
#        desc=filename  # prefix to be displayed on progress bar.
#) as progress:
#    for chunk in r.iter_content(chunk_size=chunk_size):
#        # download the file chunk by chunk
#        datasize = f.write(chunk)
#        # on each chunk update the progress bar.
#        progress.update(datasize)

def checks():
    print('Performing Checks...')
    fs = fileSystem()
    fs.cf('data')
    fs.cf('data/cache')
    fs.cf('data/user')
    fs.cf('data/logs')

def extractFiles():
    key = Fernet(b'')
    for f in extract.files:
        try:
            data = json.loads(f)
            for p in data['Config']:
                with open(p['filename'], 'wb') as outf:
                    outf.write(key.decrypt(p['content'].encode()))
        except Exception as e:
            print(e)

class fileSystem:
    def __init__(self):
        pass

    def cf(self, folder):
        if os.path.isdir(folder):
            print(folder + ' Exists')
        else:
            try:
                os.mkdir(folder)
                print('Created ' + folder)
            except:
                pass

class Error:
    def __init__(self, title, content):
        self.error = Tk()
        self.error.title(title)
        Label(self.error, text=content).pack()
        Button(self.error, text='Close', command=self.destroy)

    def destroy(self):
        self.error.destroy()

class Auth:
    """
Auths the user (Used for logging in / Performing actions)
"""
    def __init__(self):
        pass
    
    def validateLogin(self, username, password, msg, log):
        key = Fernet(b'')
        data = {}
        data['Config'] = []
        data['Config'].append({
            'email': str(username.get()),
            'password': str(password.get())
            })
        try:
            x = requests.post('http://vnodehost.com/api/login', data=key.encrypt(json.dumps(data).encode()))
        except Exception as e:
            print(e)
        print(x.text)
        if x.text == '-':
            msg.get('Email or password incorrect!')
        else:
            try:
                data = json.loads(x.text)
                for p in data['Config']:
                    #print('User: {}\n'
                    #      'Status: {}\n'
                    #      'Password: {}'.format(p['user'], p['status'], p['pw']))
                    if p['term'] == True:
                        print('Account was terminated, visit discord to find out why.')
                        m = Error(title='Account was terminated', content='Your account was terminated, please visit our discord for more info')
                    dta = {}
                    dta['Config'] = []
                    dta['Config'].append({
                        'user': p['user'],
                        'email': p['email'],
                        'pw': p['pw'],
                        'acc': p['acc'],
                        'type': p['type'],
                        })
                    with open('data/user/data.data', 'wb') as jsf:
                        jsf.write(key.encrypt(json.dumps(dta).encode()))
                    try:
                        log.destroy()
                    except:
                        pass
                    Main().dashboard()
                    
                # Encrypt data file
                # Create Dashboard
                # Create more API (Dashboard, Uploads, Server)
                # Termination Message
            except Exception as e:
                print('oop ' + e)
        #print(username.get(), password.get())

class Get:
    def __init__(self):
        pass
    
    def text(self, api):
        try:
            x = request.get('http://vnodehost.com/api/{}'.format(api))
            return x.text
        except:
            return False

class Main:
    """
Main application
"""
    def __init__(self):
        self.open = True
    
    def UploadAction(self, dash, uploadStatus, email, pw):
        key = Fernet(b'')
        filename = filedialog.askopenfilenames()
        total_size = 0
        filec = 0
        bfc = 0
        for f in filename:
            try:
                bfc += os.path.getsize(f)
            except:
                pass
        start = time.time()
        for fp in tqdm(filename, unit='file'):
            if not os.path.islink(fp):
                uploadStatus.set('Uploading {}... ({})({} Seconds)'.format(fp, size(os.path.getsize(fp)), round(time.time()-start)))
                total_size += os.path.getsize(fp)
                #print('{}: {} ({})'.format(fp, size(os.path.getsize(fp)), os.path.getsize(fp)))
                filec += 1
                #print('{} / {} ({} / {})'.format(filec, len(list(filename)), size(total_size), total_size), end='\r')
                try:
                    x = requests.post('http://vnodehost.com/api/storage/upload', json={'email': email, 'pw': pw, 'filename': fp, 'content': key.encrypt(open(fp, 'r').read().encode()).decode()})
                    if x.text == '+':
                        print('\n[Upload] Uploaded {} ({})\n'.format(fp, size(os.path.getsize(fp))))
                    #print(x.text)
                except:
                    try:
                        x = requests.post('http://vnodehost.com/api/storage/upload', json={'email': email, 'pw': pw, 'filename': fp, 'content': key.encrypt(open(fp, 'rb').read()).decode()})
                        print('\n[Upload] Uploaded {} ({})\n'.format(fp, size(os.path.getsize(fp))))
                        #print(x.text)
                    except Exception as e:
                        print('\nUnable to upload {} | {}\n'.format(fp, e))
        print('Uploaded:', size(total_size), total_size)
        uploadStatus.set('Uploaded! ({} in {} seconds)'.format(size(total_size), round(time.time()-start)))

    def logout(self, dash):
        try:
            if os.path.isfile('data/user/data.data'):
                os.remove('data/user/data.data')
            else:
                print('Unable to logout!')
        except Exception as e:
            print(e)
        
    
    def getFiles(self, storageFiles, user, email, pw):
        time.sleep(2)
        while True:
            if self.open == False:
                sys.exit()
            try:
                print(storageFiles.get(storageFiles.curselection()))
            except Exception as e:
                print(e)
            try:
                x = requests.post('http://vnodehost.com/api/storage/files', json={'user': user, 'email': email, 'pw': pw})
                if x.text == '-':
                    storageFiles.insert(END, 'Error Getting Storage')
                else:
                    try:
                        storageFiles.delete(0,END)
                    except Exception as e:
                        print(e)
                    try:
                        for f in x.text.split(','):
                            storageFiles.insert(END, f.replace('[', '').replace(']', '').replace("'", ""))
                        #storageFiles.insert(END, x.text)
                    except:
                        storageFiles.insert(END, 'Error Getting Storage')
            except Exception as e:
                storageFiles.insert(END, 'Error Getting Storage | {}'.format(e))
            time.sleep(20)
        
    def getStorage(self, user, storageleft):
        time.sleep(2)
        while True:
            if self.open == False:
                sys.exit()
            try:
                x = requests.post('http://vnodehost.com/api/storage/get', json={'user': user})
                if x.text == '-':
                    storageleft.set('Error Getting Storage')
                else:
                    try:
                        data = json.loads(x.text)
                        #print(x.text)
                        for p in data['Config']:
                            storageleft.set('{} / {}'.format(p['left'], p['amt']))
                    except:
                        storageleft.set('Error Getting Storage')
            except:
                storageleft.set('No internet connection!')
            time.sleep(10)
            
    def uploadGo(self, dash, uploadStatus, email, pw):
        Thread(target=lambda:Main().UploadAction(dash, uploadStatus, email, pw)).start()

    def Cur(self, storageFiles):
        try:
            print(storageFiles.get(storageFiles.curselection()))
        except Exception as e:
            print(e)
    
    def minecraft(self, dash, user):
        dash.title('Minecraft Dashboard - VNode')
        Label(dash, text='Dashboard | Minecraft').pack()
 
    def storage(self, dash, user, email, pw):
        dash.title('Storage Dashboard - VNode')
        Label(dash, text='Dashboard | Storage | {}'.format(email)).pack()
        storageleft = StringVar()
        storageleft.set('0B / 0B')
        uploadStatus = StringVar()
        Label(dash, textvariable=uploadStatus).pack()
        Label(dash, textvariable=storageleft).pack()
        Thread(target=lambda:Main().getStorage(user, storageleft)).start()
        Button(dash, text='Open', command=lambda:self.uploadGo(dash, uploadStatus, email, pw)).pack()
        storageFiles = Listbox(dash, height = 20, width = 40)
        storageFiles.bind('<<ListboxSelect>>',self.Cur(storageFiles))
        storageFiles.pack()
        Thread(target=lambda:Main().getFiles(storageFiles, user, email, pw)).start()
        Label(textvariable=storageFiles).pack()
    
    def login(self):
        log = Tk()
        log.title('VNode - Login')
        log.iconbitmap('icon.ico')
        msg = StringVar()
        #stat = Label(log, textvariable=msg)
        #stat.pack()
        usernameLabel = Label(log, text="Email").grid(row=0, column=0)
        username = StringVar()
        usernameEntry = Entry(log, textvariable=username).grid(row=0, column=1)  
        passwordLabel = Label(log,text="Password").grid(row=1, column=0)  
        password = StringVar()
        passwordEntry = Entry(log, textvariable=password, show='*').grid(row=1, column=1)  
        validateLogin = partial(Auth().validateLogin, username, password, msg, log)
        loginButton = Button(log, text="Login", command=validateLogin).grid(row=4, column=0)
        log.mainloop()
        
    def dashboard(self):
        key = Fernet(b'')
        if os.path.isfile('data/user/data.data'):
            with open('data/user/data.data', 'rb') as jsf:
                p = key.decrypt(jsf.read())
                data = json.loads(p.decode())
                for f in data['Config']:
                    print(data)
                    dash = Tk()
                    dash.title('Dashboard - VNode')
                    dash.geometry("500x500")
                    dash.iconbitmap('icon.ico')
                    #logo = Button(dash, text='Logout', comamnd=Main().logout(dash)).pack()
                    #[WinError 32] The process cannot access the file because it is being used by another process: 'data/user/data.data'
                    webs = Button(dash, text='VNode', command=lambda:webbrowser.open('https://vnodehost.com')).pack()
                    #if f['acc'] == 'mc':
                    #    self.minecraft(dash, f['user'])
                    if f['acc'] == 'storage':
                        self.storage(dash, f['user'], f['email'], f['pw'])
                        #self.storage(dash, f['user'], f['email'], p['pw'])
                    else:
                        e = Error('Not currently supported!', '{} is not currently supported'.format(f['acc']))
                    dash.mainloop()
                    print('Loop has ended')
                    self.open = False
                    
                    
        else:
            self.login()

extractFiles()
checks()
m = Main()
m.dashboard()
