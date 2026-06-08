from netbox.search import SearchIndex
 
from .models import Application, Group
 
 
class ApplicationIndex(SearchIndex):
    model = Application
    fields = (
        # Lower weight = ranked higher in results
        ('name', 100),
        ('slug', 110),
        ('description', 500),
    )
    display_attrs = ('slug', 'description', 'owner')
 
 
class GroupIndex(SearchIndex):
    model = Group
    fields = (
        ('name', 100),
        ('description', 500),
    )
    display_attrs = ('description', 'application', 'owner')

