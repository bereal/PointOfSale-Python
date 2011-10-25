from mock import Mock
from flexmock import *

class Price:
  def euro(value):
    return Price(value)

  def __init__(self, value):
    self.__value = value

  def __eq__(self, other):
    return True

  def __str__(self):
    return "€%d" % self.__value

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

