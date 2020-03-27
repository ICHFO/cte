# The Harvest

## Implementing a site specific scraper

1. Create a class subclassing from \_Harvester
2. Implement a function returning a list of links

Template:
```python
class XxxHarvester(_Harvester):
    def extract_urls(self):
        for i in range(xx,xx):
            url = f"{self.base_url}{i}"
            self.driver.get(url)
            for  w in self.driver.window_handles:
                self.driver.switch_to_window(w)
                ### scraping code goes here,
                ### be sure to place folowing funtction accordingly
                self.links.append(link)
```
