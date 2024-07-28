# Import packages
import pandas as pd # for data manipulation and analysis
import tkinter as tk # for creating graphical user interface (GUI) components
from tkinter import ttk
from pint import UnitRegistry # for handling and converting units of measurement
from itertools import combinations # to generate possible combinations of items
import re   # for regular expression operations, useful for pattern matching and text manipulation

### Path to recipes excel file
df = pd.read_excel('recipes.xlsx')

# Import UnitRegistry and Quantity from pint
ureg = UnitRegistry()
Q_ = ureg.Quantity

def format_ingredients(ingredients):
    # Clear the existing text in the ingredients_text widget
    ingredients_text.delete(1.0, tk.END)
    
    # Initialize a variable to keep track of the current category
    current_category = None
    
    # Iterate over each ingredient and its associated information
    for ingredient, info in ingredients.items():
        category = info['category']  # Get the category of the current ingredient
        
        # Check if the current ingredient's category is different from the previous one
        if category != current_category:
            # If it's not the first category, add a newline for separation
            if current_category is not None:
                ingredients_text.insert(tk.END, '\n')
            
            # Insert the category name and a line of dashes under it
            ingredients_text.insert(tk.END, f"{category}\n")
            ingredients_text.insert(tk.END, '-' * len(category) + '\n')
            
            # Update the current category to the new one
            current_category = category
        
        # Create the ingredient text with its amount, unit, and name
        text = f"{info['amount']} {info['unit']} {ingredient}\n"
        
        # Insert the formatted ingredient text into the ingredients_text widget
        ingredients_text.insert(tk.END, text)



def calculate_ingredients(selected_recipes):
    # Clear the existing text in the ingredients_text widget
    ingredients_text.delete(1.0, tk.END)
    
    # Initialize dictionaries and sets to store ingredient details and encountered categories
    total_ingredients = {}
    categories_encountered = set()

    # Iterate over each selected recipe
    for recipe in selected_recipes:
        # Remove leading star and spaces from the recipe name
        recipe_name = recipe.lstrip('* ')
        
        # Retrieve the row corresponding to the current recipe from the DataFrame
        row = df[df['Meal'] == recipe_name].iloc[0]
        
        # Insert the recipe name into the ingredients_text widget
        ingredients_text.insert(tk.END, f"{recipe_name}\n")
        
        # Split the ingredients string into individual ingredients with categories
        ingredients_with_categories = row['Ingredients'].strip("{}").split(', ')
        
        # Process each ingredient in the recipe
        for ingredient_with_category in ingredients_with_categories:
            parts = ingredient_with_category.split(':')
            
            # Parse the ingredient details based on the number of parts
            if len(parts) == 3:
                category, ingredient, amount_with_unit = parts
            elif len(parts) == 2:
                category, ingredient_amount = parts
                print(f"Error parsing ingredient amount in recipe '{recipe}': {ingredient_amount}")
                continue
            else:
                print(f"Error parsing ingredient amount in recipe '{recipe}': {ingredient_with_category}")
                continue

            # Add the category to the set of encountered categories
            categories_encountered.add(category)
            
            try:
                # Use regular expressions to extract the unit from the amount_with_unit string
                match = re.search(r'([a-zA-Z]+)', amount_with_unit)
                if match:
                    amount_unit = match.group(1)
                    amount_value = amount_with_unit.replace(amount_unit, '').strip()
                else:
                    # If no unit is found, set amount_unit to None
                    amount_value = amount_with_unit
                    amount_unit = None
                    # Uncomment the following line if you want to print a warning message
                    # print(f"Warning: No unit found for '{ingredient}' in recipe '{recipe}'.")

                # Convert the amount_value and amount_unit to a standard unit using Pint
                if amount_unit:
                    amount_in_standard_units = ureg(amount_value + ' ' + amount_unit)
                else:
                    amount_in_standard_units = ureg(amount_value)
                    
                # Handle cases where the unit cannot be parsed
                try:
                    # Update the total amount of the ingredient in the total_ingredients dictionary
                    if ingredient in total_ingredients:
                        total_ingredients[ingredient]['amount'] += amount_in_standard_units.magnitude
                    else:
                        total_ingredients[ingredient] = {'amount': amount_in_standard_units.magnitude, 'unit': str(amount_in_standard_units.units), 'category': category}
                except AttributeError:
                    # If an AttributeError occurs, handle it by treating the amount as raw value
                    if ingredient in total_ingredients:
                        total_ingredients[ingredient]['amount'] += amount_in_standard_units
                    else:
                        total_ingredients[ingredient] = {'amount': amount_in_standard_units, 'unit': str('x'), 'category': category}
            
            except ValueError as e:
                # Print and record any errors encountered while processing the amount
                print(f"Error processing amount '{amount_with_unit}' in recipe '{recipe}', ingredient '{ingredient}': {e}")
                format_issues.append(f"Error processing amount '{amount_with_unit}' in recipe '{recipe}', ingredient '{ingredient}': {e}")

    # Sort the categories alphabetically
    sorted_categories = sorted(categories_encountered)
    
    # Insert each category and its ingredients into the ingredients_text widget
    for category in sorted_categories:
        ingredients_text.insert(tk.END, f"{category}\n")
        ingredients_text.insert(tk.END, '-' * len(category) + '\n')
        for ingredient, info in total_ingredients.items():
            if info['category'] == category:
                # Format the ingredient text including its amount, unit, and name
                text = f"{info['amount']} {info['unit']} {ingredient}\n"
                ingredients_text.insert(tk.END, text)
        # Add a newline after listing all ingredients for a category
        ingredients_text.insert(tk.END, '\n')



def suggest_recipes():
    # Clear the existing text in the ingredients_text widget
    ingredients_text.delete(1.0, tk.END)
    
    try:
        # Get and validate the number of meals from the user input
        num_meals = int(num_meals_entry.get())
    except ValueError:
        ingredients_text.insert(tk.END, "Please enter a valid number of meals.\n")
        return

    # Gather all selected ingredients from the listboxes
    selected_ingredients = []
    for category, category_listbox in category_listboxes.items():
        selected_ingredients += [category_listbox.get(i).split('\t')[-1].strip() for i in category_listbox.curselection()]

    # Check if the user requires recipes with meat
    require_meat = require_meat_var.get()

    # Validate the number of meals
    if num_meals <= 0 or num_meals > len(df):
        ingredients_text.insert(tk.END, "Please enter a number between 1 and the total number of meals.\n")
        return

    # Initialize lists to store recipes based on whether they include meat
    recipe_scores = {}
    meat_recipes = []
    non_meat_recipes = []

    # Process each recipe in the DataFrame
    for index, row in df.iterrows():
        # Extract and parse ingredients from the recipe
        ingredients_with_categories = row['Ingredients'].strip("{}").split(', ')
        ingredients_in_recipe = []
        for ingredient_with_category in ingredients_with_categories:
            parts = ingredient_with_category.split(':')
            if len(parts) == 3:
                category, ingredient, amount_with_unit = parts
            elif len(parts) == 2:
                category, ingredient_amount = parts
                amount_with_unit = ingredient_amount
                continue
            else:
                continue

            # Format the amount and unit of the ingredient
            match = re.search(r'(\d*\.?\d+)\s*(\w+)?', amount_with_unit)
            if match:
                amount_value = match.group(1)
                amount_unit = match.group(2) if match.group(2) else ''
                if amount_unit:
                    formatted_amount_with_unit = f"{amount_value} {amount_unit} {ingredient}"
                else:
                    formatted_amount_with_unit = f"{amount_value} x {ingredient}"  # Use "x" for count only
            else:
                formatted_amount_with_unit = f"1 x {ingredient}"  # Default format if no match

            ingredients_in_recipe.append((category, ingredient, formatted_amount_with_unit))

        # Check if the recipe contains any selected meat ingredients
        has_meat_ingredient = any(category.lower() == 'meat' and ingredient in selected_ingredients for category, ingredient, _ in ingredients_in_recipe)

        # Identify missing ingredients in the current recipe
        missing_ingredients = [(category, ingredient, formatted_amount_with_unit) for category, ingredient, formatted_amount_with_unit in ingredients_in_recipe if ingredient not in selected_ingredients]

        # Categorize recipes based on meat requirement
        if require_meat:  # If the checkbox is checked
            if has_meat_ingredient:
                meat_recipes.append((row['Meal'], missing_ingredients))
            else:
                continue
        else:
            if not has_meat_ingredient:
                non_meat_recipes.append((row['Meal'], missing_ingredients))
            else:
                meat_recipes.append((row['Meal'], missing_ingredients))

    num_meat_recipes = len(meat_recipes)
    num_non_meat_recipes = len(non_meat_recipes)

    # Check if there are enough meat recipes to meet the requirement
    if require_meat and num_meat_recipes < num_meals:
        ingredients_text.insert(tk.END, "There aren't that many recipes with the required meats.\n")
        return

    # Determine possible combinations of recipes to suggest
    if require_meat:
        if num_meat_recipes >= num_meals:
            possible_combinations = [combo for combo in combinations(meat_recipes, num_meals)]
        else:
            required_non_meat = num_meals - num_meat_recipes
            required_non_meat = min(required_non_meat, num_non_meat_recipes)
            possible_combinations = [combo for combo in combinations(meat_recipes, num_meat_recipes) 
                                     for non_meat_combo in combinations(non_meat_recipes, required_non_meat)
                                     if len(combo) + len(non_meat_combo) == num_meals]
    else:
        possible_combinations = [combo for combo in combinations(meat_recipes + non_meat_recipes, num_meals)]

    # Find the combination with the fewest missing ingredients
    best_combination = None
    min_missing_ingredients = float('inf')

    for combo in possible_combinations:
        unique_ingredients_needed = set()
        missing_ingredient_count = 0

        for meal, missing_ingredients in combo:
            for category, ingredient, formatted_amount_with_unit in missing_ingredients:
                if (category, ingredient) not in unique_ingredients_needed:
                    unique_ingredients_needed.add((category, ingredient))
                    missing_ingredient_count += 1  # Count each missing ingredient

        if missing_ingredient_count < min_missing_ingredients:
            min_missing_ingredients = missing_ingredient_count
            best_combination = combo

    # Display the best combination of recipes and their ingredients
    if best_combination:
        suggested_recipes.clear()
        for meal, missing_ingredients in best_combination:
            suggested_recipes.append(meal)
            ingredients_text.insert(tk.END, f"{meal} (Missing {len(missing_ingredients)} ingredients)\n")
            ingredients_text.insert(tk.END, '-' * len(meal) + '\n')
            for category, ingredient, formatted_amount_with_unit in missing_ingredients:
                if ingredient not in selected_ingredients:
                    ingredients_text.insert(tk.END, f"{formatted_amount_with_unit}\n")
            ingredients_text.insert(tk.END, '\n')
        get_combined_button.pack(pady=10)



def get_combined_ingredients():
    # Call the function to calculate ingredients based on the suggested recipes
    calculate_ingredients(suggested_recipes)


# Clean the DataFrame by removing rows with missing or empty 'Ingredients' fields
df = df.dropna(subset=['Ingredients'])
df = df[df['Ingredients'].str.strip() != '']

# Initialize lists and dictionaries to track format issues and unique ingredients
format_issues = []
unique_ingredients = {}
ingredient_counts = {}

# Iterate over each row in the DataFrame to process ingredients
for index, row in df.iterrows():
    # Extract and parse the ingredients with their categories
    ingredients_with_categories = row['Ingredients'].strip("{}").split(', ')
    for ingredient_with_category in ingredients_with_categories:
        parts = ingredient_with_category.split(':')
        
        # Check if the ingredient format is valid
        if len(parts) == 3:
            category, ingredient, amount_with_unit = parts
        elif len(parts) == 2:
            category, ingredient_amount = parts
            # Log issues with ingredient amount format
            format_issues.append(f"Error parsing ingredient amount in row {index}: {ingredient_amount}")
            continue
        else:
            # Log issues with ingredient format
            format_issues.append(f"Error parsing ingredient amount in row {index}: {ingredient_with_category}")
            continue

        # Add the ingredient to the appropriate category set
        if category not in unique_ingredients:
            unique_ingredients[category] = set()
        unique_ingredients[category].add(ingredient)
        
        # Update the count of the ingredient
        ingredient_counts[ingredient] = ingredient_counts.get(ingredient, 0) + 1

# Print all format issues encountered during the parsing
for issue in format_issues:
    print(issue)

# Sort the unique ingredients in each category
for category in unique_ingredients:
    unique_ingredients[category] = sorted(unique_ingredients[category])


# Sort the DataFrame by 'Meal' column to ensure meals are listed in alphabetical order
df = df.sort_values(by='Meal')
# Create a list of sorted meal names
sorted_meals = df['Meal'].tolist()

# Initialize the main Tkinter window
root = tk.Tk()
root.title("Meal Ingredients Calculator")  # Set the title of the window
root.geometry("1000x700")  # Set the dimensions of the window

# Create a frame to hold the list of meals
meals_frame = tk.Frame(root)
meals_frame.pack(side='left', fill='both', expand=True)

# Create and place a label for the meals section
meals_title_label = tk.Label(meals_frame, text="Select Meals", font=("Helvetica", 14, "bold"))
meals_title_label.pack(side='top', padx=10, pady=5)

# Create and place a vertical scrollbar for the meal listbox
meal_scrollbar = tk.Scrollbar(meals_frame, orient='vertical')
meal_scrollbar.pack(side='right', fill='y')

# Create a listbox to display the meals, allowing multiple selections
meal_listbox = tk.Listbox(meals_frame, yscrollcommand=meal_scrollbar.set, selectmode='multiple', width=35)
# Populate the listbox with meals and mark favourites with a leading '*'
for meal, favourite in zip(df['Meal'], df['Favourite']):
    if favourite == 1:
        meal_listbox.insert(tk.END, f"* {meal}")
    else:
        meal_listbox.insert(tk.END, meal)
# Pack the listbox and configure scrolling
meal_listbox.pack(side='left', fill='both', expand=True)
meal_listbox.config(yscrollcommand=meal_scrollbar.set)
meal_scrollbar.config(command=meal_listbox.yview)

# Create a frame to hold the ingredients
ingredients_frame = tk.Frame(root)
ingredients_frame.pack(side='left', fill='both', expand=True)

# Create and place a label for the ingredients section
ingredients_title_label = tk.Label(ingredients_frame, text="Select Ingredients", font=("Helvetica", 14, "bold"))
ingredients_title_label.pack(side='top', padx=10, pady=5)

# Create a frame to hold the canvas and scrollbar together
scrollable_frame = tk.Frame(ingredients_frame)
scrollable_frame.pack(side='left', fill='both', expand=True)

# Create a canvas to hold the ingredient categories
canvas = tk.Canvas(scrollable_frame)
canvas.pack(side='left', fill='both', expand=True)

# Add a scrollbar linked to the canvas
overall_ingredient_scrollbar = tk.Scrollbar(scrollable_frame, orient='vertical', command=canvas.yview)
overall_ingredient_scrollbar.pack(side='right', fill='y')

# Configure canvas to use scrollbar
canvas.config(yscrollcommand=overall_ingredient_scrollbar.set)

# Create a frame inside the canvas to hold the ingredient category frames
ingredient_category_container = tk.Frame(canvas)
canvas.create_window((0, 0), window=ingredient_category_container, anchor='nw')

# Create dictionaries to store frames and listboxes for each ingredient category
ingredient_category_frames = {}
category_listboxes = {}

# Iterate over each unique ingredient category to create corresponding UI elements
for category in unique_ingredients:
    # Create a new frame for the current category inside the main container
    category_frame = tk.Frame(ingredient_category_container)
    category_frame.pack(fill='both', expand=True)

    # Create and place a label for the category
    category_label = tk.Label(category_frame, text=category, font=("Helvetica", 12, "bold"))
    category_label.pack(side='top', padx=5, pady=5)

    # Create and place a vertical scrollbar for the category listbox
    category_scrollbar = tk.Scrollbar(category_frame, orient='vertical')
    category_scrollbar.pack(side='right', fill='y')

    # Create a listbox to display the ingredients for the current category
    category_listbox = tk.Listbox(category_frame, yscrollcommand=category_scrollbar.set, selectmode='multiple', exportselection=False, width=30)
    # Populate the listbox with ingredients and their counts, formatted for display
    for ingredient in unique_ingredients[category]:
        display_text = f"{ingredient_counts[ingredient]}\t{ingredient}"
        category_listbox.insert(tk.END, display_text)
    category_listbox.pack(side='left', fill='both', expand=True)
    # Configure scrolling for the listbox
    category_listbox.config(yscrollcommand=category_scrollbar.set)
    category_scrollbar.config(command=category_listbox.yview)
    
    # Store the frame and listbox in the dictionaries for future reference
    ingredient_category_frames[category] = category_frame
    category_listboxes[category] = category_listbox

# Update scroll region when the size of the frame changes
def update_scrollregion(event):
    canvas.configure(scrollregion=canvas.bbox("all"))

# Bind the resize event to update scroll region
ingredient_category_container.bind("<Configure>", update_scrollregion)

# Frame for output and controls
output_frame = tk.Frame(root)
output_frame.pack(side='left', fill='both', expand=True)

# Label for the ingredients section
ingredients_title_label = tk.Label(output_frame, text="Ingredients required", font=("Helvetica", 14, "bold"))
ingredients_title_label.pack(side='top', padx=10, pady=2)  # Reduced vertical padding

# Text widget for displaying the required ingredients
ingredients_text = tk.Text(output_frame, wrap="word", font=("Helvetica", 15))
ingredients_text.pack(fill="both", expand=True)

# Button to calculate the ingredients for the selected meals
calculate_button = tk.Button(output_frame, text="Calculate Ingredients", command=lambda: calculate_ingredients([meal_listbox.get(i).rstrip(' *') for i in meal_listbox.curselection()]))
calculate_button.pack(pady=2)  # Reduced vertical padding

# Label and entry for specifying the number of meals to suggest
num_meals_label = tk.Label(output_frame, text="Number of meals to suggest:", font=("Helvetica", 12))
num_meals_label.pack(pady=2)  # Reduced vertical padding
num_meals_entry = tk.Entry(output_frame)
num_meals_entry.pack(pady=2)  # Reduced vertical padding

# Checkbox to require meat in the suggested recipes
require_meat_var = tk.BooleanVar()
require_meat_checkbox = tk.Checkbutton(output_frame, text="Require Meat", variable=require_meat_var)
require_meat_checkbox.pack(pady=2)  # Reduced vertical padding

# Button to suggest recipes based on selected criteria
suggest_button = tk.Button(output_frame, text="Suggest Recipes", command=suggest_recipes)
suggest_button.pack(pady=2)  # Reduced vertical padding

# Button to get the combined ingredient list from the suggested recipes
get_combined_button = tk.Button(output_frame, text="Get Combined Ingredient List", command=get_combined_ingredients)
get_combined_button.pack(pady=2)  # Reduced vertical padding

# Initialize an empty list to store suggested recipes
suggested_recipes = []

# Start the Tkinter event loop, which will keep the application running and responsive to user interactions
root.mainloop()