# recipes2groceries
Generate grocery lists from a selection of your custom recipes

I've been using HelloFresh for a while now to have prepackaged meal ingredients and recipe cards delivered to my door, because I've always struggled to plan my weekly grocery shopping in advance of cooking different meals throughout the week. Now that I've built up a set of recipes with all the ingredients clearly specified, I wanted to come up with a way to easily calculate a simple grocery list based on the list of recipes I want to cook during the week. This python GUI is the result.

## Getting started
* Install and open [Miniconda](https://docs.conda.io/projects/miniconda/en/latest/)
* Create an environment with python 3.11 e.g:
```
conda create -n recipes2groceries python=3.11
```
* Activate (enter) the environment:
```
conda activate recipes2groceries
```
* Install the packages the script is dependent on:
```
pip install pandas pint tk openpyxl
```
* Navigate to the folder containing the recipe excel file and the recipes2groceries.py file:
```
cd \path\to\working\directory
```
* Then you're ready to begin! Once you've populated the excel file with your recipes, just run the script:
```
python recipes2groceries.py
```
This will open the graphic user interface.

# The recipes2groceries interface
<img width="1001" alt="Screenshot 2024-07-28 at 19 42 27" src="https://github.com/user-attachments/assets/70391869-c54e-4a0b-abfc-b1956472b2a1">
The interface contains 3 columns: the recipes, the ingredients, and the output. Recipes with an asterisk in front of their name represent "favourites", and the numbers to the left of the ingredients in the centre column represent the number of recipes each ingredient is used in.
Select a recipe or multiple recipes by clicking on the names in the left column, and then click the "Calculate Ingredients" button to output all the required ingredients to make these meals in the rightmost column:
<img width="998" alt="Screenshot 2024-07-28 at 19 45 44" src="https://github.com/user-attachments/assets/6e9f14e1-fba5-4a7d-9b7b-a8a4070faa01">


Alternatively, select a series of ingredients (e.g. what you already have in the house), type in a number of meals to suggest, and then click the "Suggest Recipes" button to get a list of meals that collectively require the fewest additional ingredients:
<img width="1000" alt="Screenshot 2024-07-28 at 19 51 20" src="https://github.com/user-attachments/assets/da603298-168b-4939-82d3-a97a7e4d906b">
If the "Require Meat" checkbox is ticked, then the suggested recipes will be forced to use some of the meat ingredients selected in the middle column (to avoid the need to go out and buy a different meat item). In the example below, I selected bacon and chicken breast so my recommended recipes were based on chicken breast and bacon instead of the previously suggested pork and beef recipes that required a lower number of total new ingredients:
<img width="1002" alt="Screenshot 2024-07-28 at 19 53 59" src="https://github.com/user-attachments/assets/e9249a6f-f68c-4cf5-a12e-5bae1ff45161">


Finally, you can click "Get Combined Ingredient List" to get the final combined grocery list to make those meals (remove the items you already have):
<img width="1000" alt="Screenshot 2024-07-28 at 19 55 16" src="https://github.com/user-attachments/assets/dd598bfb-dd9b-4e0e-b40a-e4ddc1ec0729">

# Making the recipe excel file
The recipe excel file has 3 columns: Favourite, Meal, and Ingredients. The favourite column is used to highlight recipes you might want to make more often than the others. Add the number 1 to this cell in the same row as your favourite recipes, and leave the rest blank. In the Meal column write your recipe name, and the ingredients in the Ingredients column. The format of the ingredients list needs to be very specific. Each ingredient must be written in this format:
```
category:ingredient name:amount and optional unit
```
For example:
```
meat:ground beef:10oz
```
The categories can be anything you choose, but I recommend you keep them consistent. Each ingredient in the list must be separated by a comma, and the entire list must be contained in curly brackets {}.
