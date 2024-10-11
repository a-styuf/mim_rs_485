# ext imports
import sys
from PyQt6 import QtWidgets, QtCore
import time
from  visual.data_vis import Widget
import pandas as pd
from loguru import logger
from datetime import datetime, timedelta

if __name__ == '__main__':  # Если мы запускаем файл напрямую, а не импортируем
    logger.add("logs/{time}_visual.log")
    
    file_name = 'Exp_csv_result\\2024-10-12 02_27_41\\2024-10-12 02_27_41_Experiment_data_Ch_64.csv'
    
    app = QtWidgets.QApplication(sys.argv)
    ex = Widget()
    #
    df: pd.DataFrame = pd.read_csv(file_name)
    logger.info(df)
    df = df.sort_values(by="FR_TIME")
    #
    
    #
    data_list = []
    for index, name in enumerate(df.columns.to_list()):
        logger.info(f"{name}")
        data_list.append([name])
        raw_data = []
        for value in df[name].to_list():
            if name == "FR_TIME":
                base_time:  datetime = datetime.strptime("2000-01-01 00:00:00",'%Y-%m-%d %H:%M:%S')
                frame_time: datetime = datetime.strptime(value,'%Y-%m-%d %H:%M:%S')
                raw_data.append((frame_time - base_time).total_seconds())
            else:
                try:
                    raw_data.append(float(value))
                except:
                    raw_data.append(int(value, 16))
            pass
        data_list[-1].append(raw_data)
    data_list.pop(0)
    #

    ex.set_graph_data(data_list)
    ex.show()
    sys.exit(app.exec()) # type: ignore
    