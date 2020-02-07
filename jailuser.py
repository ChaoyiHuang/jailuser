import crypt
import getopt
import os
import sys


def jail_user(name, password):
    if exist_user(name):
        print("user ", name, " exist,", "please use other user name")
        return
    add_user(name, password)
    jail_init(name)
    jail_dev(name)
    jail_bash(name)
    sync_user(name)
    append_user_sshd(name)
    restart_sshd(name)


def jail_init(name):
    os.system("sudo jk_init -v -j /home/"+name+" basicshell editors netutils ssh scp ping")


def jail_dev(name):
    os.system("sudo mkdir -p /home/"+name+"/dev/")
    os.system("sudo mknod -m 666 /home/"+name+"/dev/null c 1 3")
    os.system("sudo mknod -m 666 /home/"+name+"/dev/tty c 5 0")
    os.system("sudo mknod -m 666 /home/"+name+"/dev/zero c 1 5")
    os.system("sudo mknod -m 666 /home/"+name+"/dev/random c 1 8")


def jail_bash(name):
    os.system("sudo mkdir -p /home/"+name+"/bin/")
    os.system("sudo mkdir -p /home/"+name+"/lib/")
    os.system("sudo mkdir -p /home/"+name+"/lib64/")
    os.system("sudo mkdir -p /home/"+name+"/lib/x86_64-linux-gnu/")
    os.system("sudo cp -v /bin/bash /home/"+name+"/bin/")
    os.system("sudo cp -v /lib/x86_64-linux-gnu/libncurses.so.5"
              " /home/"+name+"/lib/")
    os.system("sudo cp -v /lib/x86_64-linux-gnu/libtinfo.so.5"
              " /home/"+name+"/lib/")
    os.system("sudo cp -v /lib/x86_64-linux-gnu/libdl.so.2"
              " /home/"+name+"/lib/")
    os.system("sudo cp -v /lib/x86_64-linux-gnu/libc.so.6"
              " /home/"+name+"/lib/")
    os.system("sudo cp -v /lib64/ld-linux-x86-64.so.2"
              " /home/"+name+"/lib64/")
    os.system("sudo cp -va /lib/x86_64-linux-gnu/libnss_files*"
              " /home/"+name+"/lib/x86_64-linux-gnu/")
    enable_bash_color(name)


def enable_bash_color(name):
    # os.system("sudo cp -v ~/.bashrc /home"+name+"/home/"+name+"/")
    # os.system("sudo chown "+name+":"+name+" /home/"+name+"/home/"+name+"/.bashrc")
    os.system("sudo cp -v /usr/bin/dircolors /home/"+name+"/usr/bin/")
    file_name = "/home/"+name+"/home/"+name+"/.bashrc"
    with open(file_name, "w") as bashrc_file:
        bashrc_file.write("alias ls='ls --color=auto'\n")
        bashrc_file.write("alias grep='grep --color=auto'\n")
        bashrc_file.write("alias fgrep='fgrep --color=auto'\n")
        bashrc_file.write("alias egrep='egrep --color=auto'\n")
    os.system("sudo chown "+name+":"+name+" "+file_name)


def add_user(name, password):
    encPass = crypt.crypt(password, "22")
    os.system("sudo useradd -p"+encPass+" "+name)
    os.system("sudo chsh -s /bin/bash "+name)

    # /home/{name} is the jailed folder for the user
    os.system("sudo mkdir -p /home/"+name+"/")
    os.system("sudo chown root:root /home/"+name+"/")
    os.system("sudo chmod 0755 /home/"+name+"/")

    # /home/{name}/{name} is writable folder for the user
    os.system("sudo mkdir -p /home/"+name+"/home/"+name+"/")
    os.system("sudo chown "+name+":"+name+" /home/"+name+"/home/"+name+"/")


def exist_user(name):
    users = []
    with open("/etc/passwd", "r") as f:
        lines = f.readlines()
        for line in lines:
            user = line.split(":")
            if len(user) > 1:
                users.append(user[0])
    for user in users:
        if user == name:
            return True
    return False


def sync_user(name):
    passwd = get_passwd(name)
    if passwd != "":
        with open("/home/"+name+"/etc/passwd", "w") as f:
            f.write(passwd)

    group = get_group(name)
    if group != "":
        with open("/home/"+name+"/etc/group", "w") as f:
            f.write(group)


def get_passwd(name):
    with open("/etc/passwd", "r") as f:
        lines = f.readlines()
        for line in lines:
            user = line.split(":")
            if len(user) > 1:
                if user[0] == name:
                    return line
    return ""


def get_group(name):
    with open("/etc/group", "r") as f:
        lines = f.readlines()
        for line in lines:
            group = line.split(":")
            if len(group) > 1:
                if group[0] == name:
                    return line
    return ""


def append_user_sshd(name):

    #backup the old workable /etc/ssh/sshd_config
    os.system("sudo cp /etc/ssh/sshd_config /etc/ssh/bak_sshd_config")

    #append new user to jailed folder
    with open("/etc/ssh/sshd_config", "a") as myfile:
        myfile.write("\nMatch User "+name+"\n")
        myfile.write("        X11Forwarding yes\n")
        myfile.write("        AllowTcpForwarding yes\n")
        myfile.write("        PermitTTY yes\n")
        myfile.write("        ChrootDirectory /home/"+name+"/\n")


def restart_sshd(name):
    result = os.system("sudo systemctl restart sshd")
    print("*******************************************************************************************")
    print("*******************************************************************************************")
    print("*******************************************************************************************")
    if result != 0:
        print("restart sshd failed for jailed user "+name)
    else:
        print('congraturation, "'+name+'" is now jailed to folder "/home/'+name+'/"')
        print('login the server with "'+name+'" account, "/home/'+name+'" is the only writable folder')
    print("*******************************************************************************************")
    print("*******************************************************************************************")
    print("*******************************************************************************************")


def main(argv):
    try:
        options, args = getopt.getopt(argv, "hn:p:", ["help", "name=", "password="])
    except getopt.GetoptError:
        sys.exit()

    name = ""
    password = ""
    for option, value in options:
        if option in ("-h", "--help"):
            print("usage: python jailuser.py --name=[NAME], --password=[PASSWORD]")
        if option in ("-n", "--name"):
            name = value.strip()
        if option in ("-p", "--password"):
            password = value.strip()
    if name == "" or password == "":
        print("wrong parameter")
        print("usage: python jailuser.py --name=[NAME], --password=[PASSWORD]")
        return
    print("Start jailing user name "+name+", password "+password)
    jail_user(name, password)


if __name__ == '__main__':
    main(sys.argv[1:])

