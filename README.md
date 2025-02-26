Installation
Prerequisites
1. Install Python
Install python-3.9.12 and python-pip. Follow the steps from the below reference document based on your Operating System. Reference: https://docs.python-guide.org/starting/installation/

2. Install MySQL
Install mysql-8.0.15.<= Follow the steps form the below reference document based on your Operating System. Reference: https://dev.mysql.com/doc/refman/5.5/en/

3. Setup virtual environment
# Install virtual environment
sudo pip install virtualenv

# Make a directory
mkdir envs

# Create virtual environment
virtualenv ./envs/

# Activate virtual environment
source envs/bin/activate
4. Clone git repository
git clone "git@github.com:CresitaTech/staffing-backend.git"
5. Install requirements
pip install -r requirements.txt
6. Load sample data into MySQL
# open mysql bash
mysql -u <mysql-user> -p

# Give the absolute path of the file
mysql> source ~/simple-django-project/world.sql
mysql> exit;
7. Edit project settings
# open settings file
vim staffingapp/settings.py

# Edit Database configurations with your MySQL configurations.
# Search for DATABASES section.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'world',
        'USER': '<mysql-user>',
        'PASSWORD': '<mysql-password>',
        'HOST': '<mysql-host>',
        'PORT': '<mysql-port>',
    }
}


# save the file
8. Run the server
# Make migrations
python manage.py makemigrations
python manage.py migrate



# Run the server
python manage.py runserver 0:8001

# your server is up on port 8001
Try opening http://localhost:8001 in the browser. Now you are good to go.
