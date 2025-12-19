import datetime 

class LogCat:
    RESET = '\033[0m'       
    BLUE = '\033[34m'       
    YELLOW = '\033[33m'     
    PURPLE = '\033[35m'   
    RED = '\033[31m'       
    GREEN = '\033[102m'      
    CYAN = '\033[36m'      
    BOLD = '\033[1m'       

    def _get_english_datetime(self):
        now = datetime.datetime.now()
        return now.strftime("%H:%M:%S")

    def info(self, data: str):
        datetime_str = self._get_english_datetime()
        print(f"{self.BLUE}[{datetime_str}] [INFO] {data}{self.RESET}")

    def warning(self, data: str):
        datetime_str = self._get_english_datetime()
        print(f"{self.YELLOW}[{datetime_str}] [WARNING] {data}{self.RESET}") 

    def system(self, data: str):
        datetime_str = self._get_english_datetime()
        print(f"{self.BOLD}{self.PURPLE}[{datetime_str}] [SYSTEM] {data}{self.RESET}")

    def error(self, data: str):
        datetime_str = self._get_english_datetime()
        print(f"{self.BOLD}{self.RED}[{datetime_str}] [ERROR] {data}{self.RESET}")

    def success(self, data: str):
        datetime_str = self._get_english_datetime()
        print(f"{self.GREEN}[{datetime_str}] [SUCCESS] {data}{self.RESET}")

    def debug(self, data: str):
        datetime_str = self._get_english_datetime()
        print(f"{self.CYAN}[{datetime_str}] [DEBUG] {data}{self.RESET}")
