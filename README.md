# Team Paca

## Members:

Mairaj Khalid k20019274,
Adomas Zilickij k20059569,
Nathan Lutala k20027893,
Volodymyr Hromyk k20067584,
Mohammad Seifanvari k20047636,
Aksar Islam k20059568

## Sourced code (with references):

- Used gitignore.io to make .gitignore file
- Most code written is from the learning materials provided in the 5CCS2SEG course.
- Code from previous term projects were reused. The projects used were of Mairaj, and Adomas and Aksar.
- Code for testing/evaluating and building the recommender system is from the linked in learning course:
  "Building Recommender Systems with Machine Learning and AI".
  Files used were downloaded from the webpage link:
  https://sundog-education.com/RecSys/

## Deployed software:

The software is deployed on Heroku.
Link to deployed code (no longer available): https://fierce-depths-05542.herokuapp.com/
Link to admin page of deployed code (no longer available): https://fierce-depths-05542.herokuapp.com/admin/

Database is already seeded.
Only one admin is seeded.

Admin username: admin1
Admin password: Password123

All users seeded in this software have the password as "Password123".

Users seeded have usernames starting from "1aa" to "200".
For example, single digits have "aa" attatched to them, while double have single "a",
and none onwards, so "1aa", "10a", "100".

Note: users may be seeded starting from higher numbers if other users exist before them.

## Installation Instructions:

### Python version:

3.8 preferrably 3.8.10 (surprise library may not work on a higher version like python 3.10 or lower versions as well).

Note: For the all information below, ensure you are using the local command line in a python enviroment inside the current directory.

### Installation steps:

Install all packages listed in requirements.txt file using pip.

Note: The libraries installed are needed for below.

### Running the server:

Call "python manage.py runserver".

You can go to local host on browser to see if server is running once run command.

### Running the tests:

Call "python manage.py test".

### Accessing HTML report of coverage tool:

Do not need python environment, just need to be inside current directory using local command line.

Call "your_brower htmlcov/index.html".

### Running the recommender evaluator:

Execute "RecsBakeOff.py".

Note: In its current setting it may break, as it will try to load a very large dataset that was provided in project briefs.

### Seeding the database:

Call "python manage.py seed".

This will seed 200 users, 8 clubs, and all the books for the catalog.

Ensure database is unseeded before doing this, as information may collide for unique constraints.

### Unseeding the database:

Call "python manage.py unseed".

This will unseed the database with all users, clubs and books, except for superusers
