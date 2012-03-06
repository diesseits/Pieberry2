import cookielib
import locale

cj = cookielib.CookieJar()
prefenc = locale.getpreferredencoding()
user_agent = 'Mozilla/Linux'
headers = { 'User-Agent' : user_agent }
