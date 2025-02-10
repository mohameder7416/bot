

from tools.get_dealers_info import get_dealers_info
from tools.get_products_info import get_products_info
from toolbox import ToolBox



toolbox = ToolBox()
toolbox.store([get_products_info, get_dealers_info])
print(toolbox.tools())