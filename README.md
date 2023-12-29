# bakerysystem

#### Video demo of the project: 
https://www.youtube.com/watch?v=4HB-C_Y-s3o&feature=youtu.be

#### Description: 
This project was developt to help bakery employees to track down orders and its informations, such as clients, products and quantities, if it is for delivery or not, the hour to do it and notes that specify something about the order. To make this work, the user can sign in and register products, clients and the proper order. Hope this can help someone besides me, as bakery employee that need to track down orders everyday early in the morning. 

#### Instalation:
After installing all the requirements to the project listed in the requirements.txt, the user can run a local server with:

    export FLASK_APP=app.py
    flask run

This is going to oper a web based page of the system which does the things mentioned. 

#### Specification of the project:
There are some files in this project.
The app.py is the file that performs the connection between the web base page and the datafile to register and show the clients, projects and orders. 
In this way there are some html files that uses jinja sintax to perform the items to manage how the user interacts with the website. 
A couple of javascript files were probably the hardest part of this project, mainly the addorder.js, which is the file that execute a fetch to post the data inserted by the user to the backend part realized in the python file. This way it can add that information to the system database to keep track of the orders. Still make a fetch working by a submit button that can get the information in the html part, manage it to lists and dicts to pass to the python was really a hard and grateful thing to do.
Also, some pages has some interactive javascript commands that makes it easir for the user to properly use the website. 
Even though I did not spent to much time to make the pages a more pleasant thing to the user to spend some time in it, justifing the poorly design used here. 
The names used in the project are ficticius.