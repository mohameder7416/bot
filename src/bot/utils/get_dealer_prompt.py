from bot.variables import variables

from load_variables import load_variables
from db import DataBase
db = DataBase()
conn=db.connexion()
def get_dealer_prompt():
 return 