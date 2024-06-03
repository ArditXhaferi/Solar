from enerest import main_enerest
from fusion import main_fusion
from fronius import main_fronius
from kaco import main_kaco
from spreadsheet import create_spreadsheet
from datetime import datetime
import json

def main():
    enerest = main_enerest()
    fusion = main_fusion()
    fron = main_fronius()
    kaco = main_kaco()
    data = enerest + fusion + fron + kaco
    current_time = datetime.now().strftime('Report for: %Y-%m-%d-%H-%M')
    create_spreadsheet(data, file_name=f'{current_time}.xlsx', sheet_name='Current')

    
if __name__ == "__main__":
    main()