Ensure SSH user can only work in his own folder. 

Just for fun, no clean code here

# jailuser

 wget https://olivier.sessink.nl/jailkit/jailkit-2.21.tar.gz
 
 tar xzvf jailkit-2.21.tar.gz
 
 cd jailkit-2.21/
 
 ./configure
 
  make && make install

  python jailuser.py --name=[USER_NAME] --password=[USER_PASSWORD]
