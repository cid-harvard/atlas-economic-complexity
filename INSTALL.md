
Adding the Atlas to computer via virtualenv

### Getting The Atlas Running Locally via Virtualenv 

1. Clone from github (this will create an atlas_economic_complexity folder in the current directory)

        git clone https://github.com/cid-harvard/atlas-economic-complexity.git
        
2. Create the virtual environment

        mkvirtualenv env
        
3. Activate this newly created environment

        workon env

4. Install the required Python libraries

        cd atlas-economic-complexity
        pip install -r requirements.txt
        
5. Create a MySQL database on your local machine

6. Import the latest dump of the database from [https://github.com/cid-harvard/atlas-data](https://github.com/cid-harvard/atlas-data)

        mysql -u username -p -h localhost DB_NAME < atlas_xxxx-xx-xx.sql
        
7. Create local settings file based on missing info from settings.py

        touch django_files/atlas/settings_local.py
        
8. Edit this file and add the following setting CONSTANTS to it based on comments in django_files/atlas/settings.py

        DATABASES
        LOCALE_PATHS
        STATICFILES_DIRS
        SECRET_KEY
        TEMPLATE_DIRS
        REDIS
        CACHE
				
9. Run the site locally!

        django_files/manage.py runserver

### Getting The Atlas Running With Redis Caching enabled (Optional)
    
10. If you would like to run the Atlas with a cache (if, for instance, you wished to deploy it on a live server)
    All you will need to do is install the proper libraries and resources --

11. Install redis using Homebrew

        $ brew install redis

And you are done. Or download, extract and compile Redis itself with:
		
        $ wget http://redis.googlecode.com/files/redis-2.6.7.tar.gz
        $ tar xzf redis-2.6.7.tar.gz
        $ cd redis-2.6.7
        $ make  

12.	Install the redis-py client with (from https://github.com/andymccurdy/redis-py)

        $ sudo easy_install redis
        $ sudo python setup.py install
					
13. Install the django-redis backend (from https://github.com/niwibe/django-redis)
          
        easy_install django_redis
					
14. You will also need the following serialization library: (from http://msgpack.org)									
          
        easy_install msgpack-python
					
15. The constants defined in settings.py have REDIS turned on by default. The example constants in the comments can be used to turn it off. 		 
