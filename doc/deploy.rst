Getting an ABCE simulation on-line
==================================

Prepare your simulation to be displayed on the web
--------------------------------------------------

In order for your simulation to be able to be run on the web it must be running
in the webbrowser. For this the start.py file should be like it was in the
template, and :code:`from abce.abcegui import app`  must be added after the other import statements::

    from __future__ import division
    ...
    from abce.abcegui import app

    title = "Computational Complete Economy Model on Climate Gas Reduction"
    text = """ This simulation simulates climate change
    """

    simulation_parameters = OrderedDict({'wage_stickiness': (0, 0.5, 1.0),
                                         'price_stickiness': (0, 0.5, 1.0),
                                         'network_weight_stickiness': (0, 0.5, 1.0),
                                         'carbon_tax': (0, 50.0, 80.0),
                                         'tax_change_time': 100,
                                         'rounds': 200})

    @gui(simulation_parameters, text=text, title=title, self_hosted=False)
    def main(simulation_parameters):
        ...

        simulation = Simulation(rounds=simulation_parameters['rounds'], trade_logging='group', processes=1...
        simulation.run()

        #simulation.graphs() This must be commented out or deleted


    if __name__ == '__main__':
        main()

It is important to note that the :code:`main()` function is not called, when start.py
is imported! :code:`if __name__ == '__main__':`, means that it is not called
when start.py is imported. you can also simply delete the call of :code:`main()`.

:code:`@gui` is the part that generates the web application in the imported app container.
:code:`self_hosted` must be set to False in :code:`@gui(simulation_parameters, text=text, title=title, self_hosted=False)`. If :code:`self_hosted` is not False, the simulation will generate results,
but not change to the result view.

The easiest way to get your code to the server is via github. For this follow the
following instructions.
Push the simulation to github. If you are unsure what git and github is, refere to
this `gitimmersion.com<http://gitimmersion.com/>`_. If your code is not yet a git
repository change in your directory::

    git init
    git add --all
    git commit -m"initial commit"


Go to github sign up and create a new repository. It will than display you instruction
how to push an existing repository from the command line your, they will look like this::

   git remote add origin https://github.com/your_name/myproject.git
   git push -u origin master


Deploy you ABCE simulation on amazon ec2 or your own ubuntu server
------------------------------------------------------------------

For a detailed explanation refere `here<https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-uwsgi-and-nginx-on-ubuntu-14-04>`_

create an amazon ec2 instance following `Amazon's tutorial here<http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-launch-instance_linux.html>`_

make sure that in step 7b, configure the security groups, such that you have a HTTP access. This setting allows access to port 80 (HTTP) from anywhere, and ssh access only from your IP address.

.. image:: aws_security_group.jpeg
   :scale: 100 %
   :align: right

then from the console ssh into your account

::

    ssh -i amazoninstanceweb2py.pem ubuntu@ec2-54-174-70-207.compute-1.amazonaws.com

Install the server software and ABCE requirements::

    sudo apt-get update
    sudo apt-get install python-pip python-dev nginx

    sudo apt-get install python-pandas
    sudo pip install --upgrade numpy
    sudo apt-get install git

    sudo pip install virtualenv

    https://github.com/DavoudTaghawiNejad/abce.git

copy or clone your ABCE simulation into the ~/myproject directory the easiest way is to use a git repository, but you can also use scp::

    git clone https://github.com/your_name/myproject.git


change into your project and create and activate a python virtual environment::

    cd ~/myproject

    virtualenv myprojectenv
    source myprojectenv/bin/activate


Your prompt will change to indicate that you are now operating within the virtual environment. It will look something like this :code:`(myprojectenv)user@host:~/myproject$.`

Install Flask into your environment::

   pip install uwsgi flask

Install abce::

    cd ~/abce
    python setup.py install
    cd ~/myproject

Create and wsgi entry point:

    nano ~/myproject/wsgi.py

In the editor type this:

    from start import app as application

    if __name__ == "__main__":
        application.run()

-> ctrl-x -> y -> enter, to save


deactivate the virtual environment::

    deactivate

Creating a uWSGI Configuration File

    nano ~/myproject/myproject.ini

Copy this in::

    [uwsgi]
    module = wsgi

    master = true
    processes = 5

    socket = myproject.sock
    chmod-socket = 660
    vacuum = true

    die-on-term = true


Create an Upstart Script::

    sudo nano /etc/init/myproject.conf


Copy this in and change the paths, myproject and possibly the user name::

    description "uWSGI server instance configured to serve myproject"

    start on runlevel [2345]
    stop on runlevel [!2345]

    setuid ubuntu
    setgid www-data

    env PATH=/home/ubuntu/myproject/myprojectenv/bin
    chdir /home/ubuntu/myproject
    exec uwsgi --ini myproject.ini

Try to start with::

    sudo start myproject

If it doesn't start your myproject.conf is probably somehow wrong.

Configuring Nginx to Proxy Requests

    sudo nano /etc/nginx/sites-available/myproject

type in, replace the IP and directory::

    server {
        listen 80;
        server_name 54.174.70.207;

        location / {
            include uwsgi_params;
            uwsgi_pass unix:/home/ubuntu/myproject/myproject.sock;
            uwsgi_read_timeout 3000;
        }
    }

Note the uwsgi_read_timeout 3000; is important and not part of the explenation
tutorial I linked earlier. Simulations often take a long time. Setting the
timeout, the server is more patient with your simulation. You can set the value
even higher.

Link the project as active::

    sudo ln -s /etc/nginx/sites-available/myproject /etc/nginx/sites-enabled

Check the configuration::

    sudo nginx -t


Restart with new configuration::

    sudo service nginx restart

Check in the browser wether it works, put :code:`54.174.70.207` or what ever
your ip is into the address bar.

If it says internal server error check the logs::

   sudo more /var/log/upstart/myproject.log

If its a python error restart with::

    sudo restart myproject

If that doesn't work you can also reboot::

   sudo reboot now


