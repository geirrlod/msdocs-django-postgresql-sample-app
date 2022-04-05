import datetime

from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.forms import DateField 

# Create your models here.
class Restaurant(models.Model):
    name = models.CharField(max_length=50)
    street_address = models.CharField(max_length=50)
    description = models.CharField(max_length=250)
    def __str__(self):
        return self.name

class Review(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    user_name = models.CharField(max_length=20)
    rating=models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    review_text = models.CharField(max_length=500)
    review_date = models.DateTimeField('review date')    
    def __str__(self):
        return self.restaurant.name + " (" + self.review_date.strftime("%x") +")"

#Things to deal with:
# Countries --> I think the best is to have a country level above campaigns. So a total hierarchy is something like
# Country --> Campaign --> Marketing Actiivty -> Flight 
# But when a campaign is created, be able to do it in several countries at once
# in the GUI, and have a connection between the campaigns so it is possible to tab between them and the same with creatives. But open to suggestions...

# Locations
# Product promotions --> See notes, a couple of companies who has done this nicely




#we really havent looked at how to deal with product promotions, i.e. campaigns that should puch a single product or groups of products
class Campaign(models.Model):
    name = models.CharField(max_length=50)
    budget = models.DecimalField(max_digits=12, decimal_places=2)
    #Code for GoalTypes
    REVENUE = 'REVENUE'
    BRAND = 'BRAND'
    TRAFFIC = 'TRAFFIC'
    CAMPAIGN_GOAL_CHOICES = [
        (REVENUE, 'Revenue'),
        (BRAND, 'Brand'),
        (TRAFFIC, 'Traffic'),
    ]
    campaign_goal = models.CharField(
        max_length=8,
        choices=CAMPAIGN_GOAL_CHOICES,
        default=REVENUE,
    )
    campaign_goal_values = models.DecimalField(max_digits=12, decimal_places=0)
    description = models.CharField(max_length=250)
    from_date =models.DateField()
    to_date = models.DateField()
    #Should we have a landing page field here, i.e. define if the campagin needs a landing page? Or should that be a channel
    #UX wise it doesn't really matter where we put it.

class Format(models.Model):
    #Maybe a list to choose from. The whole purpose for having this as a seperate class would be to find formats that can be used across 
    #several channels.
    size = models.CharField(max_length=50)


#Newspaper, TV, Social media etc. Reporting level
class ChannelGroup(models.Model):
    name = models.CharField(max_length=50)

#This would be good were standard as much as possible across companies. Integrations with channels to get cost data
# and also suggested creative formats would be so much better then. Also which channel spesific format that is applicable (views, GPR etc for the channel)
class Channel(models.Model):
    name = models.CharField(max_length=50)
    channel_group = models.ForeignKey(ChannelGroup)

#This class need to store the formats availible somehow, and also a way to get the recommended format for a given budget... Probably
# need to use some kind of subclassing and a seperate function, but probably should be calculated each night or something and put in an table

class ChannelFormats(models.Model):
    channel = models.ForeignKey(Channel)
    format = models.ForeignKey(Format)
    recommendations = models.CharField(max_length=2500) #How to create creatives for this channel. I.e. Google guidelines
    # Could be stored at channel level?
    spend_level_minimum =models.DecimalField(max_digits=12, decimal_places=2) #how much spend before worthwhile creating this format. 
    #updated nightly, but obviously just a recommondation
    importance_level =models.IntegerField(max_digits=5) #Just to say that if you only want to create three formats, choose these three





#The marketing activity class is for the planned lifecycle. The actual flight data is a seperate class with a seperate
# row for each day (or maybe even more grannular for TV/Radio data???). Everything included formats could be different from the plan
# What about location, both for instore promotions but also for instance outdoor. Created when needed?
#Location is a good example, should it be planned in marketing activity, or just a part of flight data. Do everything need to be both in planned and in actual
# if we thing as a flight as a realization of a plan that might or might not go according to it.

class MarketingActivity(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE) #Not sure if should cascade
    description = models.CharField(max_length=250)
    from_date =models.DateField()
    to_date = models.DateField()
    channel = models.ForeignKey(Channel)
    budget = models.DecimalField(max_digits=12, decimal_places=2)
    formats = models.CharField(max_length=250) #Obviously not charfield, this should be a list of the formats choosen
    #Maybe they also should have #expectedViews etc to have something to compare to. 


class MarketingFlight(models.Model):
    marketing_activity  = models.ForeignKey(MarketingActivity)
    date =models.DateField()
    time = models.TimeField() #For some activities, like TV spots, it might actually be interesting to know when it were sent.
    spend = models.DecimalField(max_digits=12, decimal_places=2) #Seems easy to have a spend, but what is the data source. 
    #Some could be integrated with the plattforms, other could be typed in as we wait for invoices(But then not on a day to day level?)
    #And what about invoices, should that if we get them be a basis for spend or a check? Probably the last, with possibility to override.
    budget = models.DecimalField(max_digits=12, decimal_places=2) #Guess this need to beb on flight level as well? Needs to sum up to
    #marketing activity budget? How to keep track of changes on budget??? In general, not very change tracking data model so far, but easyish
    # fix when to production model. 
    format = models.ForeignKey(Format) #in some instances, we will get spend per format, but not all I am sure.
    #All channel spesific formats, will probably be a lot longer. GUI controls what is shown when.  Alternative have a seperate flight model for different channels
    #maybe for instance TV is so different from facebook that it makes sense. (A lot of TV-spot info that is important and do not fit into other)
    views = models.IntegerField()
    impressions = models.IntegerField()
    clicks = models.IntegerField()
    GPR = models.IntegerField()
    
    






#The deals made, for instance on TV they can be complex and not easily standarized. But they should be stored somewhere,
# and it might also influence the marketing plan. If you HAVE bought TV for 30 mill NOK, you better spend it. Complex issue
# but probably solvable. Hardest for multibrand shops that have deals across.
class MarketingDeals(models.Model):
    channel = models.ForeignKey(Channel)
    marketing_activity = models.ForeignKey(MarketingActivity)
    #might be a subclass of this to store the actuall deals documents

    


    def __str__(self):
        return self.name
