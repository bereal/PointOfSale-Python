from flexmock import *
from abc import abstractmethod
from io import StringIO
from nose.tools import *

class Price:
  def euro(value):
    return Price(value)

  def __init__(self, value):
    self.value = value

  def __eq__(self, other):
    if isinstance(other, Price):
      return self.value == other.value
    else:
      return False

  def __str__(self):
    return "€%d" % self.value

class SaleController:
  def __init__(self, catalog, display):
    self.display = display
    self.catalog = catalog

  def on_barcode(self, barcode):
    if not barcode:
      self.display.display_empty_barcode_message()
      return

    price = self.catalog.find_price(barcode)
    if price:
      self.display.display_price(price)
    else:
      self.display.display_product_not_found_message(barcode)

class TestSellOneItem:
  def test_known_product(self):
    price = Price.euro(12)
    catalog = flexmock(find_price = lambda _: price)
    display = flexmock()
    sale_controller = SaleController(catalog, display)

    display.should_receive("display_price").with_args(price).once

    sale_controller.on_barcode("12345")

  def test_unknown_product(self):
    catalog = flexmock(find_price = lambda _: None)
    display = flexmock()
    sale_controller = SaleController(catalog, display)

    display.should_receive("display_product_not_found_message").with_args("12345").once

    sale_controller.on_barcode("12345")

  def test_empty_barcode(self):
    catalog = flexmock()
    display = flexmock()
    sale_controller = SaleController(catalog, display)

    display.should_receive("display_empty_barcode_message").once

    sale_controller.on_barcode("")


class InMemoryCatalog:
  def __init__(self, prices_by_barcode):
    self.prices_by_barcode = prices_by_barcode

  def find_price(self, barcode):
    if barcode in self.prices_by_barcode:
      return self.prices_by_barcode[barcode]
    else:
      return None

class SubclassResponsibility(BaseException):
  pass

class CatalogContract:
  @abstractmethod
  def catalog_with(self, barcode, price):
    raise SubclassResponsibility()

  @abstractmethod
  def catalog_without(self, barcode):
    raise SubclassResponsibility()

  def test_known_product(self):
    catalog = self.catalog_with("29384", Price.euro(24))
    assert Price.euro(24) == catalog.find_price("29384")

  def test_unknown_product(self):
    catalog = self.catalog_without("23948")
    assert not catalog.find_price("23948")

class TestInMemoryCatalog(CatalogContract):
  def catalog_with(self, barcode, price):
    return InMemoryCatalog(prices_by_barcode = {barcode: price})

  def catalog_without(self, barcode):
    return InMemoryCatalog({})

class Display:
  def __init__(self, io):
    self.io = io

  def display_price(self, price):
    self.io.write("%d€" % price.value)

  def display_product_not_found_message(self, barcode):
    self.io.write("Product not found for %s" % barcode)

  def display_empty_barcode_message(self):
    self.io.write("Scanning error: empty barcode")

class TestConsoleDisplay:
  def setUp(self):
    self.io = StringIO()
    self.display = Display(self.io)

  def test_display_price(self):
    self.display.display_price(Price.euro(24))
    eq_("24€", self.io.getvalue())

  def test_display_product_not_found_message(self):
    self.display.display_product_not_found_message("1323242")
    eq_("Product not found for 1323242", self.io.getvalue())

  def test_display_empty_barcode_message(self):
    self.display.display_empty_barcode_message()
    eq_("Scanning error: empty barcode", self.io.getvalue())

class TestDictionary:
  def test_lookup(self):
    assert 1 == {"a": 1}["a"]

  def test_key_not_present(self):
    assert not "b" in {"a": 1}

class TestPriceEquals:
  def test_equal(self):
    assert Price.euro(24) == Price.euro(24)

  def test_not_equal(self):
    assert Price.euro(25) != Price.euro(24)

  def test_none(self):
    assert Price.euro(0) != None

  def test_not_a_price(self):
    assert Price.euro(1) != 1

