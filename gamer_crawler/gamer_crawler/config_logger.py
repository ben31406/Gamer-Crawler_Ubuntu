import logging 


def config_logger(l):
    # create logger
    l.setLevel(logging.INFO)

    # create file formatter
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # file handler
    # create file handler and set level
    file_handler = logging.FileHandler('gamer_log_file.log')
    file_handler.setLevel(logging.DEBUG)
    
    # add formatter to file_handler
    file_handler.setFormatter(file_formatter)
    l.addHandler(file_handler)
    return l 