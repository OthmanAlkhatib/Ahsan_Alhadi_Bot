import logging

logging.basicConfig(filename='output.log', filemode='w', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(filename)s - line:%(lineno)d - %(message)s')
logger = logging.getLogger()