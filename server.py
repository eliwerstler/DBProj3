
"""
Columbia's COMS W4111.001 Introduction to Databases
Example Webserver
To run locally:
    python server.py
Go to http://localhost:8111 in your browser.
A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""
import os
# accessible as a variable in index.html:
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, abort
from urllib.parse import quote_plus

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)


#
# The following is a dummy URI that does not connect to a valid database. You will need to modify it to connect to your Part 2 database in order to use the data.
#
# XXX: The URI should be in the format of: 
#
#     postgresql://USER:PASSWORD@34.139.8.30/proj1part2
#
# For example, if you had username ab1234 and password 123123, then the following line would be:
#
#     DATABASEURI = "postgresql://ab1234:123123@34.139.8.30/proj1part2"
#
# Modify these with your own credentials you received from TA!
DATABASE_USERNAME = "pjm2188"
DATABASE_PASSWRD = quote_plus("Peterpeter01!")
DATABASE_HOST = "34.139.8.30"
DATABASEURI = f"postgresql://{DATABASE_USERNAME}:{DATABASE_PASSWRD}@{DATABASE_HOST}/proj1part2"


#
# This line creates a database engine that knows how to connect to the URI above.
#
engine = create_engine(DATABASEURI)

#
# Example of running queries in your database
# Note that this will probably not work if you already have a table named 'test' in your database, containing meaningful data. This is only an example showing you how to run queries in your database using SQLAlchemy.
#
with engine.connect() as conn:
	# create_table_command = """
	# CREATE TABLE IF NOT EXISTS test (
	# 	id serial,
	# 	name text
	# )
	# """
	# res = conn.execute(text(create_table_command))
	# insert_table_command = """INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace')"""
	# res = conn.execute(text(insert_table_command))
	# # you need to commit for create, insert, update queries to reflect
	# conn.commit()
	result = conn.execute(text("SELECT 1"))
	print("Database connection OK:", result.fetchone())


@app.before_request
def before_request():
	"""
	This function is run at the beginning of every web request 
	(every time you enter an address in the web browser).
	We use it to setup a database connection that can be used throughout the request.

	The variable g is globally accessible.
	"""
	try:
		g.conn = engine.connect()
	except:
		print("uh oh, problem connecting to database")
		import traceback; traceback.print_exc()
		g.conn = None

@app.teardown_request
def teardown_request(exception):
	"""
	At the end of the web request, this makes sure to close the database connection.
	If you don't, the database could run out of memory!
	"""
	try:
		g.conn.close()
	except Exception as e:
		pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to, for example, localhost:8111/foobar/ with POST or GET then you could use:
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
# 
# see for routing: https://flask.palletsprojects.com/en/1.1.x/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/')
def index():
	"""
	request is a special object that Flask provides to access web request information:

	request.method:   "GET" or "POST"
	request.form:     if the browser submitted a form, this contains the data in the form
	request.args:     dictionary of URL arguments, e.g., {a:1, b:2} for http://localhost?a=1&b=2

	See its API: https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data
	"""

	# DEBUG: this is debugging code to see what request looks like
	print(request.args)


	#
	# example of a database query
	#
	select_query = "SELECT name from test"
	cursor = g.conn.execute(text(select_query))
	names = []
	for result in cursor:
		names.append(result[0])
	cursor.close()

	#
	# Flask uses Jinja templates, which is an extension to HTML where you can
	# pass data to a template and dynamically generate HTML based on the data
	# (you can think of it as simple PHP)
	# documentation: https://realpython.com/primer-on-jinja-templating/
	#
	# You can see an example template in templates/index.html
	#
	# context are the variables that are passed to the template.
	# for example, "data" key in the context variable defined below will be 
	# accessible as a variable in index.html:
	#
	#     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
	#     <div>{{data}}</div>
	#     
	#     # creates a <div> tag for each element in data
	#     # will print: 
	#     #
	#     #   <div>grace hopper</div>
	#     #   <div>alan turing</div>
	#     #   <div>ada lovelace</div>
	#     #
	#     {% for n in data %}
	#     <div>{{n}}</div>
	#     {% endfor %}
	#
	context = dict(data = names)


	#
	# render_template looks in the templates/ folder for files.
	# for example, the below file reads template/index.html
	#
	return render_template("index.html", **context)

#
# This is an example of a different path.  You can see it at:
# 
#     localhost:8111/another
#
# Notice that the function name is another() rather than index()
# The functions for each app.route need to have different names
#
@app.route('/another')
def another():
	return render_template("another.html")


# Example of adding new data to the database
@app.route('/add', methods=['POST'])
def add():
	# accessing form inputs from user
	name = request.form['name']
	
	# passing params in for each variable into query
	params = {}
	params["new_name"] = name
	g.conn.execute(text('INSERT INTO test(name) VALUES (:new_name)'), params)
	g.conn.commit()
	return redirect('/')


@app.route('/login')
def login():
	abort(401)
	# Your IDE may highlight this as a problem - because no such function exists (intentionally).
	# This code is never executed because of abort().
	this_is_never_executed()

@app.route('/recipes')
def recipes():
    try:
        cursor = g.conn.execute(text("""
            SELECT recipe_id, recipe_name, portion_size, source
            FROM recipe
            ORDER BY recipe_name
        """))
        rows = cursor.fetchall()
        cursor.close()
    except Exception as e:
        return f"<h3>Error querying recipes:</h3><pre>{e}</pre>"
    return render_template("recipes.html", rows=rows)



@app.route('/households')
def households():
    try:
        cursor = g.conn.execute(text("SELECT household_id, household_name FROM household ORDER BY household_name"))
        data = cursor.fetchall()
        cursor.close()
    except Exception as e:
        return f"<h3>Error querying households:</h3><pre>{e}</pre>"
    return render_template("households.html", households=data)



@app.route('/inventory', methods=['GET', 'POST'])
def inventory():
    try:
        # Fetch households and ingredients (with their units)
        households = g.conn.execute(text(
            "SELECT household_id, household_name FROM household ORDER BY household_name"
        )).fetchall()
        ingredients = g.conn.execute(text(
            "SELECT ingredient_id, ingredient_name, unit FROM ingredient ORDER BY ingredient_name"
        )).fetchall()

        sel_hid = request.args.get('hid') or (str(households[0].household_id) if households else None)

        # Handle form submission
        if request.method == 'POST':
            hid = request.form.get('hid')
            iid = request.form.get('iid')
            qty = request.form.get('quantity')

            if hid and iid and qty:
                # Automatically apply unit from ingredient table
                g.conn.execute(text("""
                    INSERT INTO household_in_inventory_ingredient (household_id, ingredient_id, quantity, unit)
                    VALUES (:hid, :iid, :qty, (SELECT unit FROM ingredient WHERE ingredient_id = :iid))
                    ON CONFLICT (household_id, ingredient_id)
                    DO UPDATE SET quantity = household_in_inventory_ingredient.quantity + EXCLUDED.quantity,
                                  unit = EXCLUDED.unit
                """), {'hid': hid, 'iid': iid, 'qty': qty})
                g.conn.commit()
                return redirect(f"/inventory?hid={hid}")

        # If household is selected, show its inventory
        items = None
        if sel_hid:
            items = g.conn.execute(text("""
                SELECT i.ingredient_name, hi.quantity, hi.unit
                FROM household_in_inventory_ingredient hi
                JOIN ingredient i ON i.ingredient_id = hi.ingredient_id
                WHERE hi.household_id = :hid
                ORDER BY i.ingredient_name
            """), {'hid': sel_hid}).fetchall()

        return render_template("inventory.html",
                               households=households,
                               ingredients=ingredients,
                               items=items,
                               sel_hid=str(sel_hid) if sel_hid else None)

    except Exception as e:
        return f"<h3>Error querying inventory:</h3><pre>{e}</pre>"

    

@app.route('/cookable')
def cookable():
    try:
        households = g.conn.execute(text("SELECT household_id, household_name FROM household ORDER BY household_name")).fetchall()
        sel_hid = request.args.get("hid", str(households[0].household_id) if households else None)
        rows = []
        if sel_hid:
            rows = g.conn.execute(text("""
                SELECT DISTINCT r.recipe_id, r.recipe_name, r.portion_size
                FROM recipe r
                WHERE NOT EXISTS (
                    SELECT 1
                    FROM recipe_made_with_ingredient ri
                    WHERE ri.recipe_id = r.recipe_id
                      AND ri.ingredient_id NOT IN (
                          SELECT hi.ingredient_id
                          FROM household_in_inventory_ingredient hi
                          WHERE hi.household_id = :hid
                      )
                )
                ORDER BY r.recipe_name
            """), {'hid': sel_hid}).fetchall()
    except Exception as e:
        return f"<h3>Error querying cookable recipes:</h3><pre>{e}</pre>"
    return render_template("cookable.html", households=households, rows=rows, sel_hid=str(sel_hid) if sel_hid else None)



@app.route('/mealplans')
def mealplans():
    try:
        plans = g.conn.execute(text("""
            SELECT mp.plan_id, h.household_name, mp.label
            FROM meal_plans mp
            JOIN household h ON h.household_id = mp.household_id
            ORDER BY h.household_name, mp.label
        """)).fetchall()
        sel_pid = request.args.get("pid")
        groceries = recipes = []
        if sel_pid:
            groceries = g.conn.execute(text("""
                SELECT i.ingredient_name, gci.quantity, gci.unit
                FROM grocery_list gl
                JOIN grocery_list_contains_ingredients gci ON gci.grocery_id = gl.grocery_id
                JOIN ingredient i ON i.ingredient_id = gci.ingredient_id
                WHERE gl.plan_id = :pid
                ORDER BY i.ingredient_name
            """), {'pid': sel_pid}).fetchall()
            recipes = g.conn.execute(text("""
                SELECT r.recipe_name
                FROM meal_plan_selects_recipe mpsr
                JOIN recipe r ON r.recipe_id = mpsr.recipe_id
                WHERE mpsr.plan_id = :pid
                ORDER BY r.recipe_name
            """), {'pid': sel_pid}).fetchall()
    except Exception as e:
        return f"<h3>Error querying meal plans:</h3><pre>{e}</pre>"
    return render_template("mealplans.html", plans=plans, groceries=groceries, recipes=recipes, sel_pid=str(sel_pid) if sel_pid else None)



if __name__ == "__main__":
	import click

	@click.command()
	@click.option('--debug', is_flag=True)
	@click.option('--threaded', is_flag=True)
	@click.argument('HOST', default='0.0.0.0')
	@click.argument('PORT', default=8111, type=int)
	def run(debug, threaded, host, port):
		"""
		This function handles command line parameters.
		Run the server using:

			python server.py

		Show the help text using:

			python server.py --help

		"""

		HOST, PORT = host, port
		print("running on %s:%d" % (HOST, PORT))
		app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)

run()
