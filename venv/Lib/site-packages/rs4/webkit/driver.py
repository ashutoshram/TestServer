import time
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException
from .nops import nops
import os

DEFAULT_USER_AGENT = "Mozilla/5.0 (compatible; rfphound/1.0; +http://rfphound.com/bot; AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36)"


OPS = {
        "*": "contains",
        "^": "starts-with",
        "$": "ends-with"
}
def _transport (what, by):
    if what.startswith ("link-text:"):
        what = "a:data*|" + what [10:]
    elif what.startswith ("button-text:"):
        what = "button:data*|" + what [12:]

    s = what.find (':data')
    if s == -1:
        return what, By.CSS_SELECTOR

    tag, text = what [:s], what [s + 5:]
    by = By.XPATH

    op = "="
    include_descendant = False
    if text [1] not in "=|":
        assert text [0] == "=", "Unkown Operator {}".format (text [0])
        text = text [1:]
    else:
        if text [1] == "|":
            include_descendant = True
        op = text [0]
        assert op in OPS, "Unkown Operator {}".format (text [:2])
        text = text [2:]

    if op == "=":
        if include_descendant:
            what = "//{}[.//*[text() = '{}']]".format (tag, text.replace ("'", "\\'"))
        else:
            what = "//{}[text() = '{}']".format (tag, text.replace ("'", "\\'"))

    else:
        if include_descendant:
            what = "//{}[.//*[{}(text(), '{}')]]".format (tag, OPS [op], text.replace ("'", "\\'"))
        else:
            what = "//{}[{}(text(), '{}')]".format (tag, OPS [op], text.replace ("'", "\\'"))
    return what, by


class KeysProxy:
    def __getattr__ (self, key):
        # BACKSPACE DELETE RETURN HOME END etc
        return getattr (Keys, key)


class Driver:
    def __init__ (self, driver_path, headless = False, user_agent = DEFAULT_USER_AGENT, window_size = (1600, 900), **kargs):
        self.driver_path = driver_path
        self.capabilities = self.setopt (headless, user_agent, window_size, **kargs)
        self.driver = None
        self.keys = KeysProxy ()
        self.main_window = None

    # -----------------------------------------------------------------
    def _parse_host (self, host):
        try:
            server, port = host.split (":", 1)
        except ValueError:
            raise ValueError ("proxy port is required")
        port = int (port)
        return server, port

    def __getattr__ (self, attr):
        if self.driver:
            return getattr (self.driver, attr)
        raise AttributeError ("driver does not be stared or driver has not '{}' attribute".format (attr))

    def __enter__ (self):
        if self.driver is None:
            self.create ()
        return self

    def __exit__ (self, type, value, tb):
        self.driver.quit ()
        self.driver = None

    @property
    def cookies(self):
        return self.driver.get_cookies ()

    # callables ---------------------------------------------------------
    def set_timeout (self, timeout):
        self.driver.set_page_load_timeout (timeout)

    def implicitly_wait (self, timeout):
        self.driver.implicitly_wait (timeout)

    def get (self, url):
        self.main_window = self.driver.current_window_handle
        self.driver.get (url)
    navigate = get

    def new_tab (self, url, window_name):
        self.driver.execute_script (
            "(function () {"
            'window.open ("%s", "%s")'
            "}) ()" % (url, window_name)
        )

    def html (self, timeout = 5):
        self.wait (timeout)
        return "<html>%s</html>" % self.driver.execute_script ("return document.getElementsByTagName('html')[0].innerHTML;").replace ("&nbsp;", " ")
    get_html = html

    def lxml (self):
        return nops.from_string (self.html ())

    def sleep (self, timeout):
        time.sleep (timeout)

    def _wait (self, timeout = 5, until = 'loaded', by = By.CSS_SELECTOR, what = None):
        def document_loaded (driver):
            return driver.execute_script ("return document.readyState;") == "complete"

        if until == "loaded":
            return WebDriverWait (self.driver, timeout).until (document_loaded)

        cond = {
            'title': EC.title_is,
            'title-like': EC.title_contains,
            'title__contains': EC.title_contains,
            'url': EC.url_to_be,
            'url-like': EC.url_contains,
            'url__contains': EC.url_contains,
            '~url': EC.url_matches,
            'url__regex': EC.url_matches,
        }.get (until)
        if cond:
            return WebDriverWait (self.driver, timeout).until (cond (what))

        cond = {
            'presence': EC.presence_of_element_located,
            'clickable': EC.element_to_be_clickable,
            'visible': EC.visibility_of_element_located,
            'invisible': EC.invisibility_of_element_located,
        }.get (until)
        if cond:
            return WebDriverWait (self.driver, timeout).until (cond ((by, what)))

        raise ValueError ("Unknown Condition")

    # htmlops compatible---------------------------------------
    def wait (self, timeout = 5, **kargs):
        if not kargs:
            return self._wait (timeout, 'loaded')
        assert len (kargs) == 1, "wait condition must be single"
        k, v = kargs.popitem ()
        return self.wait_until (k, v, timeout)

    def query (self, by, what, timeout = 5, until = 'presence'):
        what, by = _transport (what, by)
        if timeout:
            self._wait (timeout, until, by, what)
        return self.driver.find_elements (by, what)

    # for e2e test ---------------------------------------
    def capture (self, path = './screenshot.jpg'):
        self.save_screenshot (path)

    def wait_until (self, until = 'presence', what = None, timeout = 5, by = By.CSS_SELECTOR):
        return self._wait (timeout, until, by, what)

    def fetch (self, what, until = 'presence', timeout = 5, by = By.CSS_SELECTOR):
        try:
            return self.query (by, what, timeout, until)
        except TimeoutException:
            return

    def one (self, what, until = 'presence', timeout = 5, by = By.CSS_SELECTOR):
        elements = self.fetch (what, until, timeout, by)
        if len (elements) == 1:
            return elements [0]
        raise ValueError ('zero or more than one')

    def first (self, what, until = 'presence', timeout = 5, by = By.CSS_SELECTOR):
        try:
            return self.fetch (what, until, timeout, by) [0]
        except (TypeError, IndexError):
            return None

    def last (self, what, until = 'presence', timeout = 5, by = By.CSS_SELECTOR):
        try:
            return self.fetch (what, until, timeout, by) [-1]
        except (TypeError, IndexError):
            return None

    def as_select (self, what, until = 'presence', timeout = 5, by = By.CSS_SELECTOR):
        item = self.one (what, until, timeout, by)
        if item:
            return Select (item)

    def run (self, script):
        return self.driver.execute_script (script)

    # inputs handling --------------------------------------------------
    # SELECT
    def select (self, s, index):
        s = Select (s)
        if type (index) is int:
            s.select_by_index(index)
        else:
            s.select_by_value(index)

    def unselect (self, s, index):
        s = Select (s)
        if type (index) is int:
            s.deselect_by_index(int (index))
        else:
            s.deselect_by_value(index)

    def deselect_all (self, s):
        s = Select (s)
        s.deselect_all ()

    def select_all (self, s, text):
        s = Select (s)
        s.select_all ()

    def select_by_text (self, s, text):
        s = Select (s)
        s.select_by_visible_text(text)

    def unselect_by_text (self, s, text):
        s = Select (s)
        s.deselect_by_visible_text(text)

    # CHECKBOX, RADIO
    def check (self, group, thing):
        if type (thing) is int:
            if not group [thing].is_selected():
                group [thing].click ()
            return

        for cb in group:
            if cb.get_attribute ("value") == thing and not cb.is_selected():
                cb.click()

    def uncheck (self, group, thing):
        if type (thing) is int:
            if group [thing].is_selected():
                group [thing].click ()
            return

        for cb in group:
            if cb.get_attribute ("value") == thing and cb.is_selected():
                cb.click()

    def uncheck_all (self, group):
        for cb in group:
            if cb.is_selected():
                cb.click ()

    def check_all (self, group):
        for cb in group:
            if not cb.is_selected():
                cb.click ()

    # TEXT, PASSWORD, TEXTAREA
    def set_text (self, e, *text):
        e.send_keys (*text)
    send_keys = set_text

    def save_html (self, path):
        with open (path, "w") as f:
            f.write (self.html ())

    # shortcuts ---------------------------------------------------
    def get_frames (self, for_human = True, timeout = 10):
        self.wait (timeout)
        names = []
        index = 0
        for ftype in ("frame", "iframe"):
            frames = self.driver.find_elements_by_tag_name(ftype)
            for frame in frames:
                if for_human:
                    names.append (
                        "FRAME #%d. type: %s, name: %s, width: %s, height: %s, src: %s" % (
                        index, ftype,
                        frame.get_attribute ("name"),
                        frame.get_attribute ("width"), frame.get_attribute ("height"),
                        frame.get_attribute ("src")
                        )
                    )
                else:
                    names.append (frame)
                index += 1
        return names

    def get_windows (self, for_human = True):
        windows = []
        index = 0
        for w in self.driver.window_handles:
            if w == self.main_window:
                continue

            if for_human:
                self.driver.switch_to.window (w)
                windows.append ("WINDOW #%d. name: %s, url: %s, title: %s" % (
                        index,
                        self.driver.name,
                        self.driver.current_url,
                        self.driver.title
                    )
                )
            else:
                windows.append (w)
            index += 1
        #self.driver.switch_to.window (self.main_window)
        return windows

    def switch_to_window (self, index = None):
        if index is None:
            return self.driver.switch_to.window (self.main_window)
        if isinstance (index, str):
            return self.driver.switch_to.window (index)
        return self.driver.switch_to.window (self.get_windows (False)[index])

    def switch_to_frame (self, index = None):
        if index is None:
            return self.driver.switch_to.default_content()
        if isinstance (index, str):
            return self.driver.switch_to.frame (index)
        return self.driver.switch_to.frame (self.get_frames (False)[index])

    def switch_to_active (self):
        return self.driver.switch_to.active_element

    def switch_to_alert (self):
        return self.driver.switch_to.alert()

    def close_window (self, switch_to = None):
        self.driver.close ()
        return self.switch_to_window (switch_to)
    close = close_window

    # @abstractmethod ----------------------------------------------
    def setopt (self, headless, user_agent, window_size, **opts):
        pass

    def create (self):
        pass