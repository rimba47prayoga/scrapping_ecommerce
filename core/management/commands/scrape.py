from django.core.management.base import BaseCommand

from core.utils import Scrape


class Command(BaseCommand):

    def handle(self, *args, **options):
        product_name = input("Product Name: ")
        service = Scrape(product_name=product_name)
        service.execute()
