
from .driver import Driver, DEFAULT_USER_AGENT
from selenium import webdriver
import os
import time

class Chrome (Driver):
    def config_proxy (self, host, port):
        return {
            'httpProxy' : "%s:%d" %(host, port),
            'sslProxy' : "%s:%d" %(host, port),
            'noProxy' : None,
            'proxyType' : "MANUAL",
            'class' : "org.openqa.selenium.Proxy",
            'autodetect' : False
        }

    def setopt (self, headless, user_agent, window_size, **opts):
        options = webdriver.ChromeOptions ()
        options.add_argument("--disable-gpu")
        headless and options.add_argument('--headless')
        headless and options.add_argument('--no-sandbox')
        headless and options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--window-size={}x{}'.format (*window_size))

        capabilities = options.to_capabilities ()
        if opts.get ("proxy"):
            host, port = self._parse_host (opts ["proxy"])
            capabilities ['proxy'] = self.config_proxy (host, port)
            capabilities['user-agent'] = user_agent
        return capabilities

    def create (self):
        self.driver = webdriver.Chrome(self.driver_path, desired_capabilities = self.capabilities)


class Firefox (Driver):
    def setopt (self, headless, user_agent, window_size, **opts):
        profile = webdriver.FirefoxProfile()
        if opts.get ("proxy"):
            host, port = self.parse_host (opts ["proxy"])
            profile.set_preference("network.proxy.type", 1)
            profile.set_preference("network.proxy.http", host)
            profile.set_preference("network.proxy.http_port", port)
            profile.set_preference("network.proxy.https", host)
            profile.set_preference("network.proxy.https_port", port)
            profile.set_preference("http.response.timeout", self.TIMEOUT)
            profile.set_preference("dom.max_script_run_time", self.TIMEOUT)
            profile.set_preference("general.useragent.override", user_agent)
            profile.update_preferences()
        return profile

    def create (self):
        self.driver = webdriver.Firefox (self.capabilities, executable_path = self.driver_path)


class IE (Chrome):
    def __init__ (self, headless = False, user_agent = DEFAULT_USER_AGENT, window_size = (1600, 900), **kargs):
        Chrome.__init__ (self, None, headless, user_agent, window_size, **kargs)

    def setopt (self, headless, user_agent, window_size, **opts):
        capabilities = webdriver.DesiredCapabilities.INTERNETEXPLORER.copy()
        if opts.get ("proxy"):
            host, port = self.parse_host (opts ["proxy"])
            capabilities['proxy'] = self.config_proxy (host, port)
        return capabilities

    def create (self):
        self.driver = webdriver.Ie (self.capabilities)

