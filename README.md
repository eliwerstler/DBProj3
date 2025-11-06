# Recipe Database Web Application

## PostgreSQL Account
Account: pjm2188

This is the same database used for Part 2. 

## Web Application URL
URL: http://34.75.63.22:8111/

## Implemented Features

All features described in the original proposal were implemented. This includes:

- Display all recipes with their name, portion size, and source
- Add and delete households from the system
- Track ingredients in each household's inventory with quantities and units
- Identify which recipes can be made based on a household's current inventory
- Create, view, and delete meal plans for households with automatic grocery list generation
- Add multiple recipes from the database to meal plans
- Automatically generate grocery lists from meal plan recipes with ingredient aggregation

## Interesting Database Operations

### 1. Cookable Recipes Page (`/cookable`)

This page helps households discover which recipes they can make with their current inventory.

- Uses a `NOT EXISTS` subquery to find recipes where all required ingredients are present in the household's inventory
- The query checks the `recipe_made_with_ingredient` table against the `household_in_inventory_ingredient` table
- Returns recipes where no ingredients are missing from the household's inventory

This operation demonstrates  SQL logic using double negation. The query tries to find recipes where there does not exist any required ingredient that is not in the household's inventory. This type of operation is one of the more complex relational operations to implement in SQL.

Users interact by: 

1. User selects their household from a dropdown
2. The page queries the database to find all matching recipes
3. Results are displayed showing which recipes they can cook immediately
4. If no recipes match, users are prompted to add more ingredients to their inventory

### 2. Meal Plan and Grocery List Generation (`/mealplans`)

This page allows households to plan meals and automatically generates shopping lists with ingredient quantities.

- A multi-table insert creates records across 4 related tables in a single transaction:
  1. `meal_plans` - The meal plan itself
  2. `meal_plan_selects_recipe` - Links recipes to the plan
  3. `grocery_list` - Creates the shopping list container
  4. `grocery_list_contains_ingredients` - Populates with recipe ingredients
- When adding additional recipes to existing plans, uses `ON CONFLICT DO UPDATE` to sum ingredient quantities instead of creating duplicates

This operation demonstrates transactional database work with foreign key relationships. The query copies ingredient data from `recipe_made_with_ingredient` directly into the grocery list, and ensures that if a recipe needs 2 cups of flour and another needs 1 cup, the grocery list shows 3 cups total. This demonstrates data integrity and practical business logic.

Users interact by: 

1. User selects their household
2. Creates a new meal plan by choosing a recipe and providing a label
3. Can add additional recipes to existing plans
4. Database automatically calculates total ingredient needs
5. Grocery list updates in real-time with aggregated quantities
6. Users can delete plans, which cascades to remove all related data

Running the applciation: 

1. Select the desired PostgreSQL database
2. Set up environment variables in `.env` file:
   - `DATABASE_USER`
   - `DATABASE_PASS`
   - `DATABASE_HOST`
   - `DATABASE_NAME`
3. Install dependencies: `pip install -r requirements.txt`
4. Run the server: `python server.py`
5. Access the application at `http://localhost:8111` or VM URL if deployed remotely
