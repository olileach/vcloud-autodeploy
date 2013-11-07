import logging

requests_log = logging.getLogger("requests")
requests_log.setLevel(logging.WARNING)

class vCloud_Logger(object):

    filename = None

    def log(self,lvl,msg):

            logging.basicConfig(filename=self.filename, level=logging.DEBUG,
            format='%(asctime)-6s: %(name)s - %(levelname)s - %(message)s')

            logger = logging.getLogger('')

            if lvl == 'i' :logger.info(msg)
            if lvl == 'd' :logger.debug(msg)
            if lvl == 'w' :logger.warning(msg)
            if lvl == 'e' :logger.error(msg)
            if lvl == 'c' :logger.critical(msg)
