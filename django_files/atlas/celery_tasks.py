from celery import Celery
from celery.utils.log import get_task_logger
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

import re


# ----------- INIT ------------

# Vars
MAX_WAIT = 20
SVG_REGEX = re.compile(r"<svg.*</svg>")

# Celery app
app = Celery('tasks')
app.config_from_object("atlas.celeryconfig")

logger = get_task_logger(__name__)
# ----------- Helpers ------------


class visualization_loaded(object):
    """Selenium condition that solves issue where the Atlas viz dom element
    loads but the text doesn't."""

    def __init__(self, locator):
        self.locator = locator

    def __call__(self, driver):
        elems = expected_conditions._find_elements(driver, self.locator)
        if elems is not None and len(elems) > 1:
            return True
        else:
            return False


def extract_svg(source):
    """Using regex instead of a proper CSS selector here because a lot of
    browsers don't support outerHTML or innerHTML for svg elements, since
    they're considered xml docs. As a result, this is easier and more
    compatible than having to do the standard cross-browser hackery with
    XMLSerializer or .xml."""

    svg_elems = SVG_REGEX.findall(source)
    if not len(svg_elems) == 1:
        return False
    svg_data = svg_elems[0]

    # Insert in xmlns and version to get the file properly detected as an SVG
    namespace_string = " version='1.1' xmlns='http://www.w3.org/2000/svg' "
    return svg_data[:4] + namespace_string + svg_data[5:]


# ----------- Main ------------

@app.task
def prerender(url):
    """ Pass in a URL to get the post-javascript-execution fully rendered html
    of the page. You might need to put in a snippet like this into the page to
    catch javascript errors because selenium is silly and provides no good
    native way that works with all drivers:

    // Hack to be able to get error messages out of selenium
    window.jsErrors = [];
    window.onerror = function(errorMessage) {
    window.jsErrors[window.jsErrors.length] = errorMessage;
    }

    """

    # Initialize webdriver
    driver = webdriver.PhantomJS(
        service_args=["--debug=false",
                      "--load-images=false",
                      "--disk-cache=true",
                      "--max-disk-cache-size=100000"
                      ])

    driver.set_page_load_timeout(MAX_WAIT)
    driver.set_script_timeout(MAX_WAIT)

    # Load URL in webdriver
    viz_loaded = True
    driver.get(url)

    # Check app type and decide on how to wait for the script to end
    app_type = driver.execute_script("return window.app_name;")
    if app_type == "tree_map":
        wait_condition = visualization_loaded((By.CSS_SELECTOR,
                                               "#viz svg tspan"))
    else:
        wait_condition = expected_conditions.\
            invisibility_of_element_located((By.CSS_SELECTOR, "#loader"))

    try:
        WebDriverWait(driver, timeout=5,
                      poll_frequency=1).until(wait_condition)
    except TimeoutException:
        viz_loaded = False

    # Collect JS errors
    errors = driver.execute_script("return window.jsErrors;")
    page_source = driver.page_source

    if not viz_loaded or (errors and len(errors) > 0):
        raise RuntimeError("""The url could not be prerendered. Visualization
                           loaded within timeout = %s, JS errors = %s""" %
                           (viz_loaded, errors))

    driver.quit()

    return page_source
