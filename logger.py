import logging
import datetime as dt


class LoggingEnv:
    def __init__(self, application):
        logging.basicConfig(filename=f'/home/jack/log/{application}_{dt.datetime.now().strftime("%Y-%m-%d_%H_%m_%S")}.log',
                            filemode='w',
                            format='(%(asctime)s) (%(funcName)-8s) [%(levelname)-8s] [%(processName)-8s]: %(message)s',
                            level=logging.INFO)
        logging.info('%%%%%%%%%%%%%%%%%%%%%%%%%')
        logging.info(f'{application}')
        logging.info(f'%%%%%%%%%%%%%%%%%%%%%%%%%')
        logging.info(f'Started at: {dt.datetime.now()}')


def main():
    LoggingEnv('TestApplication')

    logging.info('test this shit out')
    logging.warning('How about this')
    logging.error('Jere we go again')


if __name__ == '__main__':
    main()
