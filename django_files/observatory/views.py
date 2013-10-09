# -*- coding: utf-8 -*-
# Django
from django.shortcuts import render_to_response, redirect
from django.http import HttpResponse, Http404, HttpResponsePermanentRedirect, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.template import RequestContext
from django.core.urlresolvers import resolve
from django.conf import settings
from django.contrib.sessions.models import Session
from django.utils.translation import ungettext
# General
from django.db.models import F
from django.db.models import Q
import json
from django.core.urlresolvers import reverse
# Project specific
from django.utils.translation import gettext as _
# App specific
from observatory.models import *
from observatory.models import storychapter
from django.db.models import Max
from django.forms import ModelForm
import msgpack
import re
# Import for cache
if settings.REDIS:
  from django.core.cache import cache, get_cache
  import redis
  import redis_cache
  from redis_cache import get_redis_connection
  import msgpack
  


#####################################
#create story
#####################################
def createStory(request):
       iscreatemode=True
       request.session['create']=iscreatemode
       if request.method == 'POST':
        post = request.POST
        story_name = post['story_name']
        story_desc = post['story_desc']
       url = request.META['HTTP_REFERER']
       return redirect(url) 

######################################
#save story
######################################
def endSaveStory(request):
  if request.POST["storyDetail"]:
   storyDetailJSON=request.POST["storyDetail"]
   objectJSON=json.loads(storyDetailJSON,encoding='utf-8')
   counter=0
   for counter in range(0,len(objectJSON)):
    data = objectJSON[counter]
    storyName=data['storyName']
    storyDesc=data['storyDescription']
    saveToStoryTable=observastory(story_name=storyName,story_desc=storyDesc)
    saveToStoryTable.save()
    storyId=observastory.objects.values_list('story_id',flat=True).filter(story_name=storyName).order_by('-story_id')[0:1]
    for story_id in storyId:
     request.session['storyId']=story_id
  if request.POST["storyChapterJSON"]:
   storyChapterJSON=request.POST["storyChapterJSON"]
   objectJSON = json.loads(storyChapterJSON,encoding='utf-8')
   chapterCount=len(objectJSON)
   storyId=request.session['storyId']
   updateChaptercount=observastory.objects.filter(story_id=storyId).update(number_of_chapters=chapterCount)
   counter=0
   for counter in range(0,len(objectJSON)):
    data = objectJSON[counter]
    chapterUrl=data['URL']
    chapterName=data['chapterName']
    chapterDescription=data['chapterDescription']
    chapterJs=json.dumps(data['JS'])
    chapterSerialNo=counter+1
    productClassification=request.session['product_classification'] if 'product_classification' in request.session else "hs4"
    sesProductClassification='product_classification'+':'+productClassification
    lang=request.session['django_language'] if 'django_language' in request.session else "en"
    sesLang='django_language'+':'+lang
    classification=request.session['classification'] if 'classification' in request.session else "hs4"
    sesClassification='classification'+':'+classification
    swap=request.session['swap'] if 'swap' in request.session else "False"
    sesSwap='swap'+':'+str(swap)
    sessionVar=(sesProductClassification,sesLang,sesClassification,sesSwap)
    sessionVarToString=str(sessionVar)[1:-1]
    chapter_details=sessionVarToString.replace("u'","'")
    saveToChapterTable=storychapter(story_id=storyId,chapter_url=chapterUrl,chapter_title=chapterName,chapter_desc=chapterDescription,chapter_js_details=chapterJs,chapter_details=chapter_details,serial_number=chapterSerialNo)
    saveToChapterTable.save()
  if 'userid'  in request.session:
   storyId=request.session['storyId']
   userId=request.session['userid']
   updateUserId=observastory.objects.filter(story_id=storyId).update(user_id=userId)
  else:
   if request.POST["socialMediaIntegrationData"]:
    socialSitesDetails=request.POST["socialMediaIntegrationData"]
    jsonObjects=json.loads(socialSitesDetails,encoding='utf-8')
    index=0
    for index in range(0,len(jsonObjects)):
     data=jsonObjects[index]
     email=data['email']
     name=data['name']
     request.session['username']=name
     source=data['source']
     if source == 'google':
      checkEmail=observatoryuser.objects.filter(user_email=email).exists()
      if checkEmail == True:
       getUserId=observatoryuser.objects.values_list('user_id',flat=True).filter(user_email=email)
       for userId in getUserId:
        request.session['userid']=userId
        storyId=request.session['storyId']
        updateUserId=observastory.objects.filter(story_id=storyId).update(user_id=userId)
      else:
       observaUser=observatoryuser(user_name=name,user_email=email,user_auth_type=source)
       observaUser.save()
       getUserId=observatoryuser.objects.values_list('user_id',flat=True).filter(user_email=email)
       for userId in getUserId:
        storyId=request.session['storyId']
        request.session['userid']=userId
        updateUserId=observastory.objects.filter(story_id=storyId).update(user_id=userId) 
     if source == 'facebook':
      checkEmail=observatoryuser.objects.filter(user_email=email).exists()
      if checkEmail == True:
       getUserId=observatoryuser.objects.values_list('user_id',flat=True).filter(user_email=email)
       for userId in getUserId:
        request.session['userid']=userId
        storyId=request.session['storyId']
        updateUserId=observastory.objects.filter(story_id=storyId).update(user_id=userId)
      else:
       observaUser=observatoryuser(user_name=name,user_email=email,user_auth_type=source)
       observaUser.save()
       getUserId=observatoryuser.objects.values_list('user_id',flat=True).filter(user_email=email)
       for userId in getUserId:
        request.session['userid']=userId
        storyId=request.session['storyId']
        updateUserId=observastory.objects.filter(story_id=storyId).update(user_id=userId) 
   else:
    storyId=request.session['storyId'] 
    updatePublish=observastory.objects.filter(story_id=storyId).update(published=1)
  iscreatemode=False
  request.session['create']=iscreatemode
  isbrowsemode=False
  request.session['retrieve']=isbrowsemode
  return redirect('/stories/')

#######################################
#browse story form
#######################################
def browseStoryForm(request):
    if 'userid'  in request.session:
     userUniqueId=request.session['userid'] 
    elif "socialMediaIntegrationData" in request.POST:
      socialSitesDetails=request.POST["socialMediaIntegrationData"]
      if socialSitesDetails:
       jsonObjects=json.loads(socialSitesDetails,encoding='utf-8')
       index=0
       for index in range(0,len(jsonObjects)):
        data=jsonObjects[index]
        email=data['email']
        name=data['name']
        request.session['username']=name
        source=data['source']
        if source == 'google':
         if observatoryuser.objects.filter(user_email=email).exists() == True:
          getUserId=observatoryuser.objects.values_list('user_id',flat=True).filter(user_email=email)
          for userId in getUserId:
           request.session['userid']=userId
         else:
          observaUser=observatoryuser(user_name=name,user_email=email,user_auth_type=source)
          observaUser.save()
          getUserId=observatoryuser.objects.values_list('user_id',flat=True).filter(user_email=email)
          for userId in getUserId:
           request.session['userid']=userId
        if source == 'facebook':
         if observatoryuser.objects.filter(user_email=email).exists() == True:
          getUserId=observatoryuser.objects.values_list('user_id',flat=True).filter(user_email=email)
          for userId in getUserId:
           request.session['userid']=userId         
         else:
          observaUser=observatoryuser(user_name=name,user_email=email,user_auth_type=source)
          observaUser.save()
          getUserId=observatoryuser.objects.values_list('user_id',flat=True).filter(user_email=email)
          for userId in getUserId:
           request.session['userid']=userId 
       userUniqueId=request.session['userid'] 
      else:
        userUniqueId=1
    else:
      userUniqueId=1
    userName=request.session['username'] if 'username' in request.session else ""
    checkAdmin=observatoryuser.objects.values('isadmin').filter(user_id=userUniqueId)
    mineStory=observastory.objects.values('story_name','story_id','published','featured','number_of_chapters').filter(user_id=userUniqueId)
    featureStory=observastory.objects.values('story_name','story_id','published','featured','number_of_chapters').filter(Q(featured=1) & (Q(published=1))) 
    popularStory=observastory.objects.values('story_name','story_id','published','featured','number_of_chapters').filter(published=1).order_by('-likecount')[0:10]
    publishStory=observastory.objects.values('story_name','story_id','published','featured','number_of_chapters').filter(published=1)
    return render_to_response('story/RetrieveForm.html',{
        'publishStory':publishStory,
	'checkAdmin':checkAdmin,
        'userName':userName,
	'userId':request.session['userid'] if 'userid' in request.session else 0,
	'mineStory':mineStory,
	'featureStory':featureStory,
	'popularStory':popularStory},context_instance=RequestContext(request))

########################################
#end browse story
########################################
def endbrowsestory(request):
  likeBtnEnable=False
  request.session['likeBtnEnable']=likeBtnEnable
  isbrowsemode=False
  request.session['retrieve']=isbrowsemode
  return redirect('/stories/')

#######################################
# edit story form
#######################################
def editStoryForm(request):
  if "Stories" in request.POST:
   editStoryId=request.POST["Stories"]
   request.session['editStoryId']=editStoryId
  editStoryId=request.session['editStoryId']
  stories=observastory.objects.values('story_name','story_desc','number_of_chapters').filter(story_id=editStoryId)
  chapters = storychapter.objects.values('chapter_id','chapter_title','chapter_desc','serial_number').filter(story_id=editStoryId).order_by("serial_number")
  if storychapter.objects.filter(story_id=editStoryId).exists() == True:
   serialNumbers=storychapter.objects.filter(story_id=editStoryId).aggregate(Max('serial_number',flat=True))
   serialNumberTostring=(str(serialNumbers)[1:-1])
   serialNumberToArray = serialNumberTostring.split(':')[-1]
   serialNumber=serialNumberToArray.strip()
   updateNumberOfChapters=observastory.objects.filter(story_id=editStoryId).update(number_of_chapters=serialNumber)
  else:
   serialNumber=0
   updateNumberOfChapters=observastory.objects.filter(story_id=editStoryId).update(number_of_chapters=serialNumber)
  temp={'storychapter':chapters,'observastory':stories}
  return render_to_response('story/editStoryForm.html',temp,context_instance=RequestContext(request))

############################################
# update story form
############################################
counter=0
def updateEditForm(request):
  storyId=request.session['editStoryId']
  if "storyTitle" in request.POST:
   storyTitle=request.POST["storyTitle"]
  if "storyDesc" in request.POST:
   storyDesc=request.POST["storyDesc"]
  if request.POST["chapterJson"]:
   chapterJson=request.POST["chapterJson"]
   objs = json.loads(chapterJson,encoding='utf-8')
   global counter
   for counter in range(0,len(objs)):
    record = storychapter(chapter_title = objs[counter])
    data = objs[counter]
    orderNumbder=data['order']
    chapterName=data['chapterTitle']
    chapterDesc= data['chapterDesc']
    chapterRemove=data['isRemoved']
    chapterID=data['chapterId'] 
    if chapterRemove == 'Y':
     deletechapter=storychapter.objects.filter(chapter_id=chapterID).delete()
    else:
     chapters=storychapter.objects.filter(chapter_id=chapterID).update         (chapter_title=chapterName,chapter_desc=chapterDesc,serial_number=orderNumbder)
   counter += 1
  story=observastory.objects.filter(story_id=storyId).update(story_name=storyTitle,story_desc=storyDesc)
  return redirect('/stories/')

################################################
# publish
################################################
def published(request):
  if request.is_ajax():
   browseStoryId=request.POST.get('storyId')
   browseStroyIdPublish=observastory.objects.values_list('published').filter(story_id=browseStoryId)
   for publishValue in browseStroyIdPublish:
    for value in publishValue:
     if value == 1:
      updatePublishValue=observastory.objects.filter(story_id=browseStoryId).update(published=0)
     else:
      updatePublishValue=observastory.objects.filter(story_id=browseStoryId).update(published=1) 
   return redirect('/stories/')

################################################
# featured
################################################
def featured(request):
   if request.is_ajax():
    browseStoryId=request.POST.get('storyId')
    browseStroyIdFeature=observastory.objects.values_list('featured').filter(story_id=browseStoryId)
    for featureValue in browseStroyIdFeature:
     for value in featureValue:
      if value == 0:
       updateFeatureValue=observastory.objects.filter(story_id=browseStoryId).update(featured=1)
    return redirect('/stories/')

#################################################
# likecount
#################################################
def likeCount(request):
  browseStoryId=request.session['browseStoryId'] if 'browseStoryIds' in request.session else 0
  updateLikeCount=observastory.objects.filter(story_id=browseStoryId).update(likecount=F('likecount')+1) 
  likeBtnEnable=request.session['likeBtnEnable'] if 'likeBtnEnable' in request.session else False
  userId=request.session['userid'] if 'userid' in request.session else 0
  if userId > 0:
   saveToLikeTable=observatory_like(user_id=userId,story_id=browseStoryId)
   saveToLikeTable.save()
  request.session['likeBtnEnable']=False
  return HttpResponse(request.session['likeBtnEnable'])

####################################################
# logout
####################################################
def logOut(request):
  iscreatemode=False
  request.session['create']=iscreatemode
  isbrowsemode=False
  request.session['retrieve']=isbrowsemode
  del request.session['userid'] 
  del request.session['username'] 
  return redirect('/explore/tree_map/export/usa/all/show/2010/')

#####################################################
# delete story
#####################################################
def deleteStory(request): 
  if 'userid'  in request.session:
   if request.is_ajax():
    deleteStoryId=request.GET.get('storyId')
    deleteStory=observastory.objects.filter(story_id=deleteStoryId).delete()
    chapterIds=storychapter.objects.filter(story_id=deleteStoryId)
    if chapterIds is not None:
     deleteStory=storychapter.objects.filter(story_id=deleteStoryId).delete()
   return redirect('/stories/')

#####################################################
# end delete story
#####################################################
def cancelstory(request):
  iscreatemode=False
  request.session['create']=iscreatemode
  isbrowsemode=False
  request.session['retrieve']=isbrowsemode
  url = request.META['HTTP_REFERER']
  return redirect(url)

############################################################
# browse story part
############################################################
browseArrayStoryId=0
browseModeIndex=0
def browsestories(request,browseStoryId):
  request.session['browseStoryId']=browseStoryId
  request.session['index']=0
  isbrowsemode=True
  request.session['retrieve']=isbrowsemode
  global browseModeIndex
  global browseArrayStoryId
  browseArrayStoryId = browseStoryId
  request.session['browseStoryIds']=browseStoryId
  userId=request.session['userid'] if 'userid' in request.session else 0
  if observatory_like.objects.filter(user_id=userId,story_id=browseStoryId).exists() == True:
    likeBtnEnable=False
    request.session['likeBtnEnable']=likeBtnEnable
  else:
     likeBtnEnable=True
     request.session['likeBtnEnable']=likeBtnEnable
  browseStoryName=observastory.objects.values_list('story_name', flat=True).filter(story_id=browseStoryId)
  for browseStoryNames in browseStoryName:
    request.session['browseStoryName']=browseStoryNames
  browseStoryDescription=observastory.objects.values_list('story_desc', flat=True).filter(story_id=browseStoryId)
  for browseStoryDescriptions in browseStoryDescription:
    request.session['browseStoryDesc']=browseStoryDescriptions
  browseStoryChapIds=storychapter.objects.values_list('chapter_id', flat=True).filter(story_id=browseStoryId)
  browseStoryChapIdsToSring=str(browseStoryChapIds)[1:-1]
  browseStoryChapIdsRemoveL=browseStoryChapIdsToSring.replace('L','')
  browseStoryChapIdsToArray=browseStoryChapIdsRemoveL.split(",")
  BrowseStoryChapNos= len(browseStoryChapIdsToArray)
  request.session['BrowseStoryChapNos']=BrowseStoryChapNos
  request.session['sessionBrowseStoryChapIds']=browseStoryChapIdsToArray
  browseStoryChapterIds=request.session['sessionBrowseStoryChapIds']
  if browseModeIndex < len(browseStoryChapterIds):
   if browseModeIndex == len(browseStoryChapterIds):
    browseModeIndex=0
######   set sessions varibales   ######
  browseStorySesVar=[chapter_details.encode("utf8") for chapter_details in storychapter.objects.values_list('chapter_details', flat=True).filter(chapter_id=browseStoryChapterIds[browseModeIndex])]
  request.session['sesBrowseModeIndex']=browseModeIndex
  for browseStorySesData in browseStorySesVar:
   browseStorySesDataToArray=browseStorySesData.split(',')
   for indexvar in range(0, len(browseStorySesDataToArray)):
    browseStorySessionData=browseStorySesDataToArray[indexvar].split(':')
    browseStorySesArrayLeft= browseStorySessionData[0].replace('\'','')
    browseStorySesArrayRight= browseStorySessionData[1].replace('\'','')
    sessionall=browseStorySesArrayLeft.strip()
    browseStorySesValues=browseStorySesArrayRight.strip()
    request.session[sessionall]=browseStorySesValues
########### redirect url##################################
   browseStoryJS=storychapter.objects.values_list('chapter_js_details', flat=True).filter(chapter_id=browseStoryChapterIds[browseModeIndex])
   for browseStoryJScript in browseStoryJS:
    request.session['browseStoryJScript']=browseStoryJScript
   browseStoryChapterName=storychapter.objects.values_list('chapter_title', flat=True).filter(chapter_id=browseStoryChapterIds[browseModeIndex])
   for browseStoryChapName in browseStoryChapterName:
    request.session['browseStoryChapName']=browseStoryChapName
   browseStoryChapterDesc=storychapter.objects.values_list('chapter_desc', flat=True).filter(chapter_id=browseStoryChapterIds[browseModeIndex])
   for browseStoryChapDesc in browseStoryChapterDesc:
    request.session['browseStoryChapterDesc']=browseStoryChapDesc
   browseStoryChapUrl=storychapter.objects.values_list('chapter_url', flat=True).filter(chapter_id=browseStoryChapterIds[browseModeIndex]) 
   for browseStoryChapterUrl in browseStoryChapUrl:
    return redirect(browseStoryChapterUrl)
def viewStory(request,browseStoryId):
  return render_to_response('story/viewStory.html',{'browseStoryId':browseStoryId},context_instance=RequestContext(request))

####################################################################
# next browse story
####################################################################
def browseStoryNext(request):
  browseStoryId=request.session['browseStoryIds']
  browseStoryName=observastory.objects.values_list('story_name', flat=True).filter(story_id=browseStoryId)
  for browseStoryNames in browseStoryName:
   request.session['browseStoryName']=browseStoryNames
  browseStoryDesc=observastory.objects.values_list('story_desc', flat=True).filter(story_id=browseStoryId)
  for browseStoryDescription in browseStoryDesc:
   request.session['browseStoryDesc']=browseStoryDescription
  index=request.session['index']
  browseStoryChapIds=request.session['sessionBrowseStoryChapIds']
  browseStoryChapNos=len(browseStoryChapIds)
  request.session['BrowseStoryChapNos']=browseStoryChapNos
  if index < len(browseStoryChapIds):
   index=index+1
   if index == len(browseStoryChapIds):
    index=0 
######set sessions varibales######
  browseStorySesVar=[chapter_details.encode("utf8") for chapter_details in storychapter.objects.values_list('chapter_details', flat=True).filter(chapter_id=browseStoryChapIds[index])]
  request.session['index']=index
  for browseStorySesData in browseStorySesVar:
   browseStorySesDataToArray=browseStorySesData.split(',')
   for indexvar in range(0, len(browseStorySesDataToArray)):
    browseStorySessionData=browseStorySesDataToArray[indexvar].split(':')
    browseStorySesLeft= browseStorySessionData[0].replace('\'','')
    browseStorySesRight= browseStorySessionData[1].replace('\'','')
    sessionall=browseStorySesLeft.strip()
    browseStorySesValues=browseStorySesRight.strip()
    request.session[sessionall]=browseStorySesValues
########### displaying url##################################
   browseStoryJS=storychapter.objects.values_list('chapter_js_details', flat=True).filter(chapter_id=browseStoryChapIds[index])
   for browseStoryJScript in browseStoryJS:
    request.session['browseStoryJScript']=browseStoryJScript
   browseStoryChapterName=storychapter.objects.values_list('chapter_title', flat=True).filter(chapter_id=browseStoryChapIds[index])
   for browseStoryChapName in browseStoryChapterName:
    request.session['browseStoryChapName']=browseStoryChapName
   browseStoryChapterDesc=storychapter.objects.values_list('chapter_desc', flat=True).filter(chapter_id=browseStoryChapIds[index])
   for browseStoryChapDesc in browseStoryChapterDesc:
    request.session['browseStoryChapterDesc']=browseStoryChapDesc
   browseStoryChapterUrl=storychapter.objects.values_list('chapter_url', flat=True).filter(chapter_id=browseStoryChapIds[index]) 
   for browseStoryChapUrl in browseStoryChapterUrl:
    return redirect(browseStoryChapUrl) 

   browseStoryChapIds=[]
###########################################################
#prev browse story
###########################################################
def browseStoryPrev(request):
  browseStoryId=request.session['browseStoryIds']
  browseStoryName=observastory.objects.values_list('story_name', flat=True).filter(story_id=browseStoryId)
  for browseStoryNames in browseStoryName:
   request.session['browseStoryName']=browseStoryNames
  browsestoryDesc=observastory.objects.values_list('story_desc', flat=True).filter(story_id=browseStoryId)
  for browsestoryDescription in browsestoryDesc:
   request.session['browseStoryDesc']=browsestoryDescription
  index=request.session['index']
  browseStoryChapterIds=request.session['sessionBrowseStoryChapIds']
  browsestoryChapterNos=len(browseStoryChapterIds)
  request.session['BrowseStoryChapNos']=browsestoryChapterNos
  if index < len(browseStoryChapterIds):
   if index  <= 0:
    index=len(browseStoryChapterIds)
   index=index-1
   request.session['index']=index
######## set sessions varibales  ########
  browseStorySesVar=[chapter_details.encode("utf8") for chapter_details in storychapter.objects.values_list('chapter_details', flat=True).filter(chapter_id=browseStoryChapterIds[index])]
  for browseStorySesData in browseStorySesVar:
   browseStorySesDataToArray=browseStorySesData.split(',')
   for  indexvar in range(0, len(browseStorySesDataToArray)):
    browseStorySessionData=browseStorySesDataToArray[indexvar].split(':')
    browseStorySesDataLeft= browseStorySessionData[0].replace('\'','')
    browseStorySesDataRight= browseStorySessionData[1].replace('\'','')
    sessionall=browseStorySesDataLeft.strip()
    browseStorySesValues=browseStorySesDataRight.strip()
    request.session[sessionall]=browseStorySesValues
########### redirect url##################################
   browseStoryJS=storychapter.objects.values_list('chapter_js_details', flat=True).filter(chapter_id=browseStoryChapterIds[index])
   for browseStoryJScript in browseStoryJS:
    request.session['browseStoryJScript']=browseStoryJScript
   browseStoryChapterName=storychapter.objects.values_list('chapter_title', flat=True).filter(chapter_id=browseStoryChapterIds[index])
   for browseStoryChapName in browseStoryChapterName:
    request.session['browseStoryChapName']=browseStoryChapName
   browseStoryChapterDesc=storychapter.objects.values_list('chapter_desc', flat=True).filter(chapter_id=browseStoryChapterIds[index])
   for browseStoryChapDesc in browseStoryChapterDesc:
    request.session['browseStoryChapterDesc']=browseStoryChapDesc
  browseStoryChapterUrl=storychapter.objects.values_list('chapter_url', flat=True).filter(chapter_id=browseStoryChapterIds[index])
  for browseStoryChapUrl in browseStoryChapterUrl:
   return redirect(browseStoryChapUrl)

  
  
def fluid(request):
  return render_to_response("fluid.html", context_instance=RequestContext(request))
  
###################
## Abandoned function? Does nothing.
###################
def new_ps(request):  
  ps_nodes = Sitc4.objects.get_all("en")
  return render_to_response("new_ps.html", {"ps_nodes":json.dumps(ps_nodes, indent=2)},context_instance=RequestContext(request))

def home(request):
  iscreatemode=False
  request.session['create']=iscreatemode
  isbrowsemode=False
  request.session['retrieve']=isbrowsemode
  import urllib2
  try:
    ip = request.META["HTTP_X_FORWARDED_FOR"]
  except KeyError:
    ip = request.META["REMOTE_ADDR"]
  # fetch the url
  url = "http://api.hostip.info/get_json.php?ip="+ip
  json_response = json.loads(urllib2.urlopen(url).read())
  country_code = json_response["country_code"]
  try:
    c = Country.objects.get(name_2char=country_code)
  except Country.DoesNotExist:
    c = Country.objects.get(name_2char="us")
  
  return render_to_response("home.html", 
    {"default_country": c},
    context_instance=RequestContext(request))

def about(request):
  isbrowsemode=False
  request.session['retrieve']=isbrowsemode
  return render_to_response("about/index.html", context_instance=RequestContext(request))
def support(request):
  return render_to_response("about/support.html", context_instance=RequestContext(request))
def research(request):
  return render_to_response("about/research.html", context_instance=RequestContext(request))
def glossary(request):
  return render_to_response("about/glossary.html", context_instance=RequestContext(request))  
def team(request):
  return render_to_response("about/team.html", context_instance=RequestContext(request))
def data(request):
  return render_to_response("about/data.html", context_instance=RequestContext(request))  
def permissions(request):
  return render_to_response("about/permissions.html", context_instance=RequestContext(request))
def privacy(request):
  return render_to_response("about/privacy.html", context_instance=RequestContext(request))

def about_data(request, data_type):
  lang = request.session['django_language'] if 'django_language' in request.session else "en"
  lang = request.GET.get("lang", lang)
  if data_type == "sitc4":
    items = [[getattr(x, "name_%s"% (lang,)), x.code] for x in Sitc4.objects.filter(community__isnull=False)]
    headers = ["Name", "SITC4 Code"]
    title = "SITC4 product names and codes"
  elif data_type == "hs4":
    items = [[x.name, x.code] for x in Hs4.objects.filter(community__isnull=False)]
    headers = ["Name", "HS4 Code"]
    title = "HS4 (harmonized system) product names and codes"
  elif data_type == "country":
    items = [[getattr(x, "name_%s"% (lang,)), x.name_3char] for x in Country.objects.filter(name_3char__isnull=False, name_2char__isnull=False, region__isnull=False)]
    headers = ["Name", "Alpha 3 Abbreviation"]
    title = "Country names and abbreviations"
  items.sort()
  return render_to_response("about/data.html",
    {"items":items, "headers":headers, "title": title},
    context_instance=RequestContext(request))

def api(request):
  isbrowsemode=False
  request.session['retrieve']=isbrowsemode
  return render_to_response("api/index.html", context_instance=RequestContext(request))

def api_apps(request):
  return render_to_response("api/apps.html", context_instance=RequestContext(request))

def api_data(request):
  return render_to_response("api/data.html", context_instance=RequestContext(request))

def book(request):
  isbrowsemode=False
  request.session['retrieve']=isbrowsemode
  return render_to_response("book/index.html", context_instance=RequestContext(request))

def set_language(request, lang):
  next = request.REQUEST.get('next', None)
  if not next:
    next = request.META.get('HTTP_REFERER', None)
  if not next:
    next = '/'
  response = HttpResponseRedirect(next)
  # if request.method == 'GET':
  #   lang_code = request.GET.get('language', None)
  lang_code = lang
  if lang_code:
    if hasattr(request, 'session'):
      request.session['django_language'] = lang_code
    else:
      response.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang_code)
      translation.activate(lang_code)
  return response

def set_product_classification(request, prod_class):
  next = request.REQUEST.get('next', None)
  if not next:
    next = request.META.get('HTTP_REFERER', None)
  if not next:
    next = '/'
  response = HttpResponseRedirect(next)
  if prod_class:
    if hasattr(request, 'session'):
      request.session['product_classification'] = prod_class
      request.session['classification'] = prod_class
  return response

def download(request):
  try:
    import cairo, rsvg, xml.dom.minidom
  except:
    pass
  import csv
  raise Exception(request.POST)
  content = request.POST.get("content")
  
  title = request.POST.get("title")
  
  format = request.POST.get("format")
  
  if format == "svg" or format == "pdf" or format == "png":
    svg = rsvg.Handle(data=content.encode("utf-8"))
    x = width = svg.props.width
    y = height = svg.props.height
  
  if format == "svg":
    response = HttpResponse(content.encode("utf-8"), mimetype="application/octet-stream")
      
  elif format == "pdf":  
    response = HttpResponse(mimetype='application/pdf')
    surf = cairo.PDFSurface(response, x, y)
    cr = cairo.Context(surf)
    svg.render_cairo(cr)
    surf.finish()
  
  elif format == "png":  
    response = HttpResponse(mimetype='image/png')
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, x, y)
    cr = cairo.Context(surf)
    svg.render_cairo(cr)
    surf.write_to_png(response)
  
  else:
    response = HttpResponse(mimetype="text/csv;charset=UTF-8")
    csv_writer = csv.writer(response, delimiter=',', quotechar='"')#, quoting=csv.QUOTE_MINIMAL)
    item_list = json.loads(content,encoding='utf-8')
    # raise Exception(content)
    for item in item_list:
      csv_writer.writerow([i.encode("utf-8") for i in item])
  
  # Need to change with actual title
  response["Content-Disposition"]= "attachment; filename=%s.%s" % (title, format)
  
  return response

def app(request, app_name, trade_flow, filter, year):
  # Get URL query parameters
  format = request.GET.get("format", False)
  lang = request.GET.get("lang", False)
  crawler = request.GET.get("_escaped_fragment_", False)
  
  country1, country2, product = None, None, None
  country1_list, country2_list, product_list, year1_list, year2_list, year_interval_list, year_interval = None, None, None, None, None, None, None
  
  trade_flow_list = ["export", "import", "net_export", "net_import"]
  
  year1_list = range(1962, 2011, 1)
  if "." in year:
    y = [int(x) for x in year.split(".")]
    year = range(y[0], y[1]+1, y[2])
    year2_list = year1_list
    year_interval_list = range(1, 11)
    year_interval = year[1] - year[0]
  else:
    year = int(year)
  
  json_response = {
    "year": year,
    "app": app_name
  }

  # Bilateral
  if "." in filter:
    bilateral_filters = filter.split(".")
    
    # Country x Product
    if len(bilateral_filters[1]) > 3:
      country1 = Country.objects.get(name_3char=bilateral_filters[0])
      product = Sitc4.objects.get(code=bilateral_filters[1])
      
      # Lists used for control pane
      country1_list = Country.objects.get_all(lang)
      product_list = Sitc4.objects.get_all(lang)
      trade_flow_list = ["export", "import"]
      
      article = "to" if trade_flow == "export" else "from"
      title = "Where did %s %s %s %s?" % (country1.name, trade_flow, product.name_en, article)
      
      # cspy means country1 / countr2 / show / year
      if crawler == "" or format == "json":
        json_response["data"] = Sitc4_ccpy.objects.cspy(country1, product, trade_flow)
        json_response["attr_data"] = Country.objects.get_all(lang)
        json_response["title"] = title
      
    # Country x Country
    else:
      country1 = Country.objects.get(name_3char=bilateral_filters[0])
      country2 = Country.objects.get(name_3char=bilateral_filters[1])

      # Lists used for control pane
      country1_list = Country.objects.get_all(lang)
      country2_list = country1_list
      trade_flow_list = ["export", "import"]
      
      article = "to" if trade_flow == "export" else "from"
      title = "What did %s %s %s %s?" % (country1.name, trade_flow, article, country2.name)
      
      # ccsy means country1 / countr2 / show / year
      if crawler == "" or format == "json":
        json_response["data"] = Sitc4_ccpy.objects.ccsy(country1, country2, trade_flow)
        json_response["attr_data"] = Sitc4.objects.get_all(lang)
        json_response["title"] = title
  
  # Product
  elif len(filter) > 3:
    product = Sitc4.objects.get(code=filter)
    product_list = Sitc4.objects.get_all(lang)
        
    title = "Who %ss %s?" % (trade_flow.replace("_", " "), product.name_en)
    
    # sapy means show / all / product / year
    if crawler == "" or format == "json":
      json_response["data"] = Sitc4_cpy.objects.sapy(product, trade_flow)
      json_response["attr_data"] = Country.objects.get_all(lang)
      json_response["title"] = title
  
  # Country
  else:
    country1 = Country.objects.get(name_3char=filter)
    country1_list = Country.objects.get_all(lang)
    
    title = "What did %s %s?" % (country1.name, trade_flow.replace("_", " "))
    
    # casy means country1 / all / show / year
    if crawler == "" or format == "json":
      json_response["data"] = Sitc4_cpy.objects.casy(country1, trade_flow)
      json_response["attr_data"] = Sitc4.objects.get_all(lang)
      json_response["title"] = title
  
  # Send data as JSON to browser via AJAX
  if format == "json":
    return HttpResponse(json.dumps(json_response))
  
  # Return page without visualization data
  return render_to_response("app/index.html", {
    "title": title,
    "trade_flow": trade_flow,
    "country1": country1,
    "country2": country2,
    "product": product,
    "year": year,
    "trade_flow_list": trade_flow_list,
    "country1_list": country1_list,
    "country2_list": country2_list,
    "product_list": product_list,
    "year1_list": year1_list,
    "year2_list": year2_list,
    "year_interval": year_interval,
    "year_interval_list": year_interval_list}, context_instance=RequestContext(request))

def app_redirect(request, app_name, trade_flow, filter, year):
  # Corrent for old spelling of tree map as one word
  if app_name == "treemap":
    app_name = "tree_map"
  
  # Bilateral
  if "." in filter:
    bilateral_filters = filter.split(".")
    
    # Country x Product
    if len(bilateral_filters[1]) > 3:
      country1, country2, product = bilateral_filters[0], "show", bilateral_filters[1]
      
    # Country x Country
    else:
      country1, country2, product = bilateral_filters[0], bilateral_filters[1], "show"
  
  # Product
  elif len(filter) > 3:
    country1, country2, product = "show", "all", filter
  
  # Country
  else:
    country1, country2, product = filter, "all", "show"
  # raise Exception("/explore/%s/%s/%s/%s/%s/%s/" % (app_name, trade_flow, country1, country2, product, year))
  return HttpResponsePermanentRedirect("/explore/%s/%s/%s/%s/%s/%s/" % (app_name, trade_flow, country1, country2, product, year))

def explore(request, app_name, trade_flow, country1, country2, product, year="2011"):
  
  iscreatemode=False
  iscreatemode = request.session['create'] if 'create' in request.session else False
  isbrowsemode=False
  isbrowsemode = request.session['retrieve'] if 'retrieve' in request.session else False
  NoOfChapter=request.session['BrowseStoryChapNos'] if 'BrowseStoryChapNos' in request.session else ""
  browseStoryName=request.session['browseStoryName'] if 'browseStoryName' in request.session else ""
  browseStoryDesc=request.session['browseStoryDesc'] if 'browseStoryDesc' in request.session else ""
  browseChapterName=request.session['browseStoryChapName'] if 'browseStoryChapName' in request.session else ""
  browseChapterDesc=request.session['browseStoryChapterDesc'] if 'browseStoryChapterDesc'in request.session else ""
  browseModeJScript=request.session['browseStoryJScript'] if 'browseStoryJScript' in request.session else ""
  NoOfChpt=request.session['NoOfchap'] if 'NoOfchap' in request.session else ""
  userName=request.session['username'] if 'username' in request.session else ""
  userId=request.session['userid'] if 'userid' in request.session else 0
  likeBtnEnable=request.session['likeBtnEnable'] if 'likeBtnEnable' in request.session else False 
  # raise Exception(country1, country2, product, year)
  # Get URL query parameters
  was_redirected = request.GET.get("redirect", False)
  crawler = request.GET.get("_escaped_fragment_", False)
  options = request.GET.copy()
  # set language (if session data available use that as default)
  lang = request.session['django_language'] if 'django_language' in request.session else "en"
  lang = request.GET.get("lang", lang)
  options["lang"] = lang
  # set product classification (if session data available use that as default)
  prod_class = request.session['product_classification'] if 'product_classification' in request.session else "hs4"
  prod_class = request.GET.get("product_classification", prod_class)
  options["product_classification"] = prod_class
  options = options.urlencode()

  # get distince years from db, different for diff product classifications
  years_available = list(Sitc4_cpy.objects.values_list("year", flat=True).distinct()) if prod_class == "sitc4" else list(Hs4_cpy.objects.values_list("year", flat=True).distinct())
  years_available.sort()

  country1_list, country2_list, product_list, year1_list, year2_list, year_interval_list, year_interval = None, None, None, None, None, None, None
  warning, alert, title = None, None, None
  data_as_text = {}
  # What is actually being shown on the page
  item_type = "product"
  
  # To make sure it cannot be another product class
  if prod_class != "hs4" and prod_class != "sitc4":
    prod_class = "sitc4"

  # Test for country exceptions
  if prod_class == "hs4":
    # redirect if and exception country
    if country1 == "bel" or country1 == "lux":
      return redirect('/explore/%s/%s/blx/%s/%s/%s/?redirect=true' % (app_name, trade_flow, country2, product, year))
    if country1 == "bwa" or country1 == "lso" or country1 == "nam" or country1 == "swz":
      return redirect('/explore/%s/%s/zaf/%s/%s/%s/?redirect=true' % (app_name, trade_flow, country2, product, year))
  if was_redirected:
    # display warning is redirected from exception
    if country1 == "blx":
      warning = {"title": "Country Substitution",
        "text": "In the Harmonized System (HS) classification, trade for Belgium and Luxembourg is reported as 'Belgium-Luxembourg'."}
    if country1 == "zaf":
      warning = {"title": "Country Substitution",
        "text": "In the Harmonized System (HS) classification, trade for Namibia, Republic of South Africa, Botswana, Lesotho and Swaziland is reported under 'South African Customs Union'."}
  
  trade_flow_list = [("export", _("Export")), ("import", _("Import")), ("net_export", _("Net Export")), ("net_import", _("Net Import"))]
  if app_name == "product_space":
    trade_flow_list = [trade_flow_list[0]]
  
  year1_list = range(years_available[0], years_available[len(years_available)-1]+1, 1)

  if app_name == "stacked" and year == "2009":
    year = "1969.2011.10"
  if "." in year:
    y = [int(x) for x in year.split(".")]
    # year = range(y[0], y[1]+1, y[2])
    year_start = y[0]
    year_end = y[1]
    year_interval = y[2]
    year2_list = year1_list
    year_interval_list = range(1, 11)
    # year_interval = year[1] - year[0]
  else:
    year_start, year_end, year_interval = None, None, None
    year = int(year)
    if year > years_available[len(years_available)-1]:
      year = years_available[len(years_available)-1]
    elif year < years_available[0]:
      year = years_available[0]
  
  
  
  api_uri = "/api/%s/%s/%s/%s/%s/?%s" % (trade_flow, country1, country2, product, year, options)
  
  redesign_api_uri = "/redesign/api/%s/%s/%s/%s/%s/%s" % (prod_class, trade_flow, country1, country2, product, year)
  
  country_code = None
  if country1 != "show" and country1 != "all": country_code = country1
  
  
  if crawler == "":
    view, args, kwargs = resolve("/api/%s/%s/%s/%s/%s/" % (trade_flow, country1, country2, product, year))
    kwargs['request'] = request
    view_response = view(*args, **kwargs)
    raise Exception(view_response)
    data_as_text["data"] = view_response[0]
    data_as_text["total_value"] = view_response[1]
    data_as_text["columns"] = view_response[2]


  app_type = get_app_type(country1, country2, product, year)

  # first check for errors
  # check whether country can be found in database
  countries = [None, None]
  country_lists = [None, None]
  for i, country in enumerate([country1, country2]):
    if country != "show" and country != "all":
      try:
        countries[i] = Country.objects.get(name_3char=country)
        country_lists[i] = Country.objects.get_all(lang)
      except Country.DoesNotExist:
        alert = {"title": "Country could not be found",
          "text": "There was no country with the 3 letter abbreviateion <strong>%s</strong>. Please double check the <a href='/about/data/country/'>list of countries</a>."%(country)}
  if product != "show" and product != "all":
    p_code = product
    product = clean_product(p_code, prod_class)
    if product:
      if product.__class__ == Sitc4:
        product_list = Sitc4.objects.get_all(lang)
        request.session['product_classification'] = "sitc4"
      else:
        product_list = Hs4.objects.get_all(lang)
        request.session['product_classification'] = "hs4"
    else:
      alert = {"title": "Product could not be found", "text": "There was no product with the 4 digit code <strong>%s</strong>. Please double check the <a href='/about/data/hs4/'>list of HS4 products</a>."%(p_code)}
  
  if countries[0]:
    # get distinct years from db, different for diff product classifications
    # also we need to filter by country1, as not all SITC4 data goes back to '62
    years_available = list(Sitc4_cpy.objects.filter(country=countries[0].id).values_list("year", flat=True).distinct()) if prod_class == "sitc4" else list(Hs4_cpy.objects.filter(country=countries[0].id).values_list("year", flat=True).distinct())
  else:
    years_available = list(Sitc4_cpy.objects.values_list("year", flat=True).distinct()) if prod_class == "sitc4" else list(Hs4_cpy.objects.values_list("year", flat=True).distinct())
  
  years_available.sort()

  list_countries_the = ["Cayman Islands", "Central African Republic", "Channel Islands", "Congo, Dem. Rep.", "Czech Republic", "Dominican Republic", "Faeroe Islands", "Falkland Islands", "Fm Yemen Dm", "Lao PDR", "Marshall Islands", "Philippines", "Seychelles", "Slovak Republic", "Syrian Arab Republic", "Turks and Caicos Islands", "United Arab Emirates", "United Kingdom", "Virgin Islands, U.S.", "United States"]

  if countries[0] and countries[0].name in list_countries_the:
    countries[0].name = "the "+countries[0].name
  
  prod_or_partner = "partner" # quick fix should be merged with item_type
  
  if not alert:
    if app_type == "casy":
      # raise Exception(app_name)
      if app_name == "pie_scatter":
        title = "What products are feasible for %s?" % countries[0].name
      elif app_name == "product_space":
        title = "How related are %s products in %s?" % (countries[0].name, year)       # INSERTED NEW TITLE HERE
      elif app_name == "stacked":
        title = "What did %s %s between %s and %s?" % (countries[0].name, trade_flow.replace("_", " "), year_start, year_end) # NEW TITLE HERE
      else:
        title = "What did %s %s in %s?" % (countries[0].name, trade_flow.replace("_", " "), year)                             # NEW TITLE HERE
        prod_or_partner = "product"

    # Country but showing other country trade partners
    elif app_type == "csay":
      item_type = "countries"
      article = "to" if trade_flow == "export" else "from"
      title = "Where did %s %s %s in %s?" % (countries[0].name, trade_flow.replace("_", " "), article, year)
  
    # Product
    elif app_type == "sapy":
      item_type = "countries"
      title = "Who did %ss %s in %s?" % (trade_flow.replace("_", " "), product.name_en, year)
  
    # Bilateral Country x Country
    elif app_type == "ccsy":
      # trade_flow_list = ["export", "import"]
      if _("net_export") in trade_flow_list: del trade_flow_list[trade_flow_list.index(_("net_export"))]
      if _("net_import") in trade_flow_list: del trade_flow_list[trade_flow_list.index(_("net_import"))]
      article = "to" if trade_flow == "export" else "from"
      title = "What did %s %s %s %s in %s?" % (countries[0].name, trade_flow, article, countries[1].name, year)

    # Bilateral Country / Show / Product / Year
    elif app_type == "cspy":
      if "net_export" in trade_flow_list: del trade_flow_list[trade_flow_list.index("net_export")]
      if "net_import" in trade_flow_list: del trade_flow_list[trade_flow_list.index("net_import")]
      item_type = "countries"    
      article = "to" if trade_flow == "export" else "from"
      title = "Where did %s %s %s %s in %s?" % (countries[0].name, trade_flow, product.name_en, article, year)
      prod_or_partner = "product"

  # Return page without visualization data
  
  return render_to_response("explore/index.html", {
    "likeBtnEnable":likeBtnEnable,
    "browseModeJScript": browseModeJScript,
    "browseChapterDesc" : browseChapterDesc,
    "browseChapterName": browseChapterName,
    "NoOfChapter" : NoOfChapter,
    "browseStoryName": browseStoryName,
    "browseStoryDesc" : browseStoryDesc,
    "isbrowsemode": isbrowsemode,
    "iscreatemode": iscreatemode,
    "userName":userName,
    "userId":userId,
    "warning": warning,
    "alert": alert,
    "prod_class": prod_class,
    "years_available": years_available,
    "data_as_text": data_as_text,
    "app_name": app_name,
    "title": title,#get_question(app_type, trade_flow=trade_flow,origin=countries[0],destination=countries[1],product=product),
    "trade_flow": trade_flow,
    "country1": countries[0] or country1,
    "country2": countries[1] or country2,
    "product": product,
    "year": year,
    "year_start": year_start,
    "year_end": year_end,
    "year_interval": year_interval,
    "trade_flow_list": trade_flow_list,
    "country1_list": country_lists[0],
    "country2_list": country_lists[1],
    "product_list": product_list,
    "year1_list": year1_list,
    "year2_list": year2_list,
    "year_interval_list": year_interval_list,
    "api_uri": api_uri,
    "app_type": app_type,
    "redesign_api_uri": redesign_api_uri,
    "country_code": country_code,
    "prod_or_partner": prod_or_partner,
    "item_type": item_type}, context_instance=RequestContext(request))

'''<COUNTRY> / all / show / <YEAR>'''
def api_casy(request, trade_flow, country1, year):
  # import time
  # start = time.time()
  
  '''Init variables'''
  prod_class = request.session['product_classification'] if 'product_classification' in request.session else "hs4"
  prod_class = request.GET.get("prod_class", prod_class)
  lang = request.session['django_language'] if 'django_language' in request.session else "en"
  lang = request.GET.get("lang", lang)
  crawler = request.GET.get("_escaped_fragment_", False)
  country1 = Country.objects.get(name_3char=country1)
  
  '''Set query params with our changes'''
  query_params = request.GET.copy()
  query_params["lang"] = lang
  query_params["product_classification"] = prod_class
  
  '''Grab extraneous details'''
  ## Clasification & Django Data Call
  name = "name_%s" % lang

  # Get attribute information  
  if prod_class == "sitc4":
    world_trade = list(Sitc4_py.objects.all().values('year','product_id','world_trade'))
    attr_list = list(Sitc4.objects.all().values('code',name,'id','color'))
    attr = {}
    for i in attr_list: 
      attr[i['code']] = {'code':i['code'],'name':i[name],'color':i['color']}
     #.extra(where=['CHAR_LENGTH(code) = 2'])
    
  elif prod_class == "hs4":
    world_trade = list(Hs4_py.objects.all().values('year','product_id','world_trade'))
    attr_list = list(Hs4.objects.all().values('code',name,'id','community_id__color'))
    attr = {}
    for i in attr_list: 
      attr[i['code']] = {'code':i['code'],'name':i[name],'item_id':i['id'],'color':i['community_id__color']}
     #.extra(where=['CHAR_LENGTH(code) = 2'])
  
  # get distince years from db, different for diff product classifications
  years_available = list(Sitc4_cpy.objects.values_list("year", flat=True).distinct()) if prod_class == "sitc4" else list(Hs4_cpy.objects.values_list("year", flat=True).distinct())
  years_available.sort()
    
  magic = Cy.objects.filter(country=country1.id,
                            year__range=(years_available[0],
                                        years_available[-1])).values('year',
                                                                    'pc_constant',
                                                                    'pc_current',
                                                                    'notpc_constant')
  magic_numbers = {}
  for i in magic: 
    magic_numbers[i['year']] = {"pc_constant":i['pc_constant'], 
                                "pc_current":i['pc_current'],
                                "notpc_constant":i["notpc_constant"]}
                                                           
  
  '''Define parameters for query'''
  year_where = "AND year = %s" % (year,) if crawler == "" else " "
  rca_col = "null"
  if trade_flow == "net_export":
    val_col = "export_value - import_value as val"
    rca_col = "export_rca"
  elif trade_flow == "net_import":
    val_col = "import_value - export_value as val"
  elif trade_flow == "export":
    val_col = "export_value as val"
    rca_col = "export_rca"
  else:
    val_col = "import_value as val"
  
  """Create query [year, id, abbrv, name_lang, val, export_rca]"""
  q = """
    SELECT cpy.year, p.id, p.code, p.name_%s, p.community_id, c.color,c.name, %s, %s, distance, opp_gain, py.pci
    FROM observatory_%s_cpy as cpy, observatory_%s as p, observatory_%s_community as c, observatory_%s_py as py 
    WHERE country_id=%s and cpy.product_id = p.id %s and p.community_id = c.id and py.product_id=p.id and cpy.year=py.year
    HAVING val > 0
    ORDER BY val DESC
    """ % (lang, val_col, rca_col, prod_class, prod_class, prod_class, prod_class, country1.id, year_where)
  
  """Prepare JSON response"""
  json_response = {}
  
  """Check cache"""
  if settings.REDIS:
    raw = get_redis_connection('default')
    key = "%s:%s:%s:%s:%s" % (country1.name_3char, "all", "show", prod_class, trade_flow)  
    # See if this key is already in the cache
    cache_query = raw.hget(key, 'data')
    if (cache_query == None):
  
      rows = raw_q(query=q, params=None)
      total_val = sum([r[4] for r in rows])
      """Add percentage value to return vals"""
      rows = [{"year":r[0], "item_id":r[1], "abbrv":r[2], "name":r[3], "value":r[4], "rca":r[5], "share": (r[4] / total_val)*100} for r in rows]
  
      if crawler == "":
        return [rows, total_val, ["#", "Year", "Abbrv", "Name", "Value", "RCA", "%"]]  
      # SAVE key in cache.
      
      json_response["data"] = rows 
      
      raw.hset(key, 'data', msgpack.dumps(rows))
    
    else:
      # If already cached, now simply retrieve
      encoded = cache_query
      decoded = msgpack.loads(encoded)
      json_response["data"] = decoded  
  
  else:
    rows = raw_q(query=q, params=None)
    total_val = sum([r[7] for r in rows])
    # raise Exception(q,r,(r[7]/total_val)*100)
    """Add percentage value to return vals"""
    # rows = [list(r) + [(r[4] / total_val)*100] for r in rows]
    rows = [{"year":r[0], "item_id":r[1], "abbrv":r[2], "name":r[3], "value":r[7], "rca":r[8], 
             "distance":r[9],"opp_gain":r[10], "pci": r[11], "share": (r[7] / total_val)*100,
             "community_id": r[4], "color": r[5], "community_name":r[6], "code":r[2], "id": r[2]} for r in rows]
    
    
    if crawler == "":
      return [rows, total_val, ["#", "Year", "Abbrv", "Name", "Value", "RCA", "%"]]
    
    json_response["data"] = rows 
    
  json_response["attr"] = attr
  json_response["attr_data"] = Sitc4.objects.get_all(lang) if prod_class == "sitc4" else Hs4.objects.get_all(lang)
  json_response["country1"] = country1.to_json()
  json_response["title"] = "What does %s %s?" % (country1.name, trade_flow.replace("_", " "))
  json_response["year"] = year
  json_response["item_type"] = "product"
  json_response["app_type"] = "casy"
  json_response["magic_numbers"] = magic_numbers
  json_response["world_trade"] = world_trade
  json_response["prod_class"] =  prod_class
  json_response["other"] = query_params

  # raise Exception(time.time() - start)
  """Return to browser as JSON for AJAX request"""
  return HttpResponse(json.dumps(json_response))

def api_sapy(request, trade_flow, product, year):
  """Init variables"""
  prod_class = request.session['product_classification'] if 'product_classification' in request.session else "hs4"
  prod_class = request.GET.get("prod_class", prod_class)
  lang = request.session['django_language'] if 'django_language' in request.session else "en"
  lang = request.GET.get("lang", lang)
  crawler = request.GET.get("_escaped_fragment_", False)
  product = clean_product(product, prod_class)
  
  """Set query params with our changes"""
  query_params = request.GET.copy()
  query_params["lang"] = lang
  query_params["product_classification"] = prod_class
  
  '''Grab extraneous details'''
  ## Clasification & Django Data Call
  name = "name_%s" % lang
  
  '''Grab extraneous details'''
  if prod_class == "sitc4":
    # attr_list = list(Sitc4.objects.all().values('code','name','color'))
    attr_list = list(Sitc4.objects.all().values('code',name,'id','color'))
    attr = {}
    for i in attr_list: 
      attr[i['code']] = {'code':i['code'],'name':i[name],'color':i['color']}
     #.extra(where=['CHAR_LENGTH(code) = 2'])
  elif prod_class == "hs4":
    # attr_list = list(Hs4.objects.all().values('code','name')) #.extra(where=['CHAR_LENGTH(code) = 2'])
    attr_list = list(Hs4.objects.all().values('code',name,'id','community_id__color'))
    attr = {}
    for i in attr_list: 
      attr[i['code']] = {'code':i['code'],'name':i[name],'item_id':i['id'],'color':i['community_id__color']}
    
    
  # Create dictionary of region codes  
  region_list = list(Country_region.objects.all().values()) #.extra(where=['CHAR_LENGTH(code) = 2'])
  region = {}
  for i in region_list: 
    region[i['id']] = i  
  
  # Create dictinoary for continent groupings
  continent_list = list(Country.objects.all().distinct().values('continent'))
  continents = {}
  for i,k in enumerate(continent_list): 
     continents[k['continent']] = i*1000
  
  """Define parameters for query"""
  year_where = "AND year = %s" % (year,) if crawler == "" else " "
  rca_col = "null"
  if trade_flow == "net_export":
    val_col = "export_value - import_value as val"
    rca_col = "export_rca"
  elif trade_flow == "net_import":
    val_col = "import_value - export_value as val"
  elif trade_flow == "export":
    val_col = "export_value as val"
    rca_col = "export_rca"
  else:
    val_col = "import_value as val"

  """Create query [year, id, abbrv, name_lang, val, export_rca]"""
  q = """
    SELECT year, c.id, c.name_3char, c.name_%s, c.region_id, c.continent, %s, %s 
    FROM observatory_%s_cpy as cpy, observatory_country as c 
    WHERE product_id=%s and cpy.country_id = c.id %s
    HAVING val > 0
    ORDER BY val DESC
    """ % (lang, val_col, rca_col, prod_class, product.id, year_where)
  
  """Prepare JSON response"""
  json_response = {}
  
  """Check cache"""
  if settings.REDIS:
    raw = get_redis_connection('default')
    key = "%s:%s:%s:%s:%s" % ("show", "all", product.id, prod_class, trade_flow)
    # See if this key is already in the cache
    cache_query = raw.hget(key, 'data')
    if (cache_query == None):
      rows = raw_q(query=q, params=None)
      total_val = sum([r[4] for r in rows])
      """Add percentage value to return vals"""
      rows = [{"year":r[0], "item_id":r[1], "abbrv":r[2], "name":r[3], "value":r[4], "rca":r[5], "share": (r[4] / total_val)*100} for r in rows]
    
      if crawler == "":
        return [rows, total_val, ["#", "Year", "Abbrv", "Name", "Value", "RCA", "%"]]  
      
      json_response["data"] = rows
      
      # SAVE key in cache.
      raw.hset(key, 'data', msgpack.dumps(rows))   
    
    else:
      # If already cached, now simply retrieve
      encoded = cache_query
      decoded = msgpack.loads(encoded)
      json_response["data"] = decoded
    
  else:
    rows = raw_q(query=q, params=None)
    total_val = sum([r[6] for r in rows])
    # raise Exception(total_val)
    """Add percentage value to return vals"""
    # rows = [list(r) + [(r[4] / total_val)*100] for r in rows]
    rows = [{"year":r[0], "item_id":r[1], "abbrv":r[2], "name":r[3], "value":r[6], "rca":r[7], "share": (r[6] / total_val)*100,
             "id": r[1], "region_id":r[4],"continent":r[5]} for r in rows]
  
    if crawler == "":
      return [rows, total_val, ["#", "Year", "Abbrv", "Name", "Value", "RCA", "%"]]
    
    json_response["data"] = rows
    
  json_response["attr_data"] = Country.objects.get_all(lang)
  json_response["product"] = product.to_json()
  json_response["title"] = "Who %ss %s?" % (trade_flow.replace("_", " "), product.name_en)
  json_response["year"] = year
  json_response["item_type"] = "country"
  json_response["app_type"] = "sapy"
  json_response["attr"] = attr
  json_response["region"]= region
  json_response["continents"] = continents
  json_response["other"] = query_params  
  # raise Exception(time.time() - start)
  """Return to browser as JSON for AJAX request"""
  return HttpResponse(json.dumps(json_response))

def api_csay(request, trade_flow, country1, year):
  """Init variables"""
  prod_class = request.session['product_classification'] if 'product_classification' in request.session else "hs4"
  prod_class = request.GET.get("prod_class", prod_class)
  lang = request.session['django_language'] if 'django_language' in request.session else "en"
  lang = request.GET.get("lang", lang)
  crawler = request.GET.get("_escaped_fragment_", False)
  country1 = Country.objects.get(name_3char=country1)
  
  """Set query params with our changes"""
  query_params = request.GET.copy()
  query_params["lang"] = lang
  query_params["product_classification"] = prod_class
  
  '''Grab extraneous details'''
  region_list = list(Country_region.objects.all().values()) #.extra(where=['CHAR_LENGTH(code) = 2'])
  region = {}
  for i in region_list: 
    region[i['id']] = i
    
  continent_list = list(Country.objects.all().distinct().values('continent'))
  continents = {}
  for i,k in enumerate(continent_list): 
     continents[k['continent']] = i*1000
  
  """Define parameters for query"""
  year_where = "AND year = %s" % (year,) if crawler == "" else " "
  rca_col = "null"
  if trade_flow == "net_export":
    val_col = "SUM(export_value - import_value) as val"
  elif trade_flow == "net_import":
    val_col = "SUM(import_value - export_value) as val"
  elif trade_flow == "export":
    val_col = "SUM(export_value) as val"
  else:
    val_col = "SUM(import_value) as val"

  '''Create query [year, id, abbrv, name_lang, val, rca]'''
  q = """
    SELECT year, c.id, c.name_3char, c.name_%s, c.region_id, c.continent, %s, %s
    FROM observatory_%s_ccpy as ccpy, observatory_country as c 
    WHERE origin_id=%s and ccpy.destination_id = c.id %s
    GROUP BY year, destination_id
    HAVING val > 0
    ORDER BY val DESC
    """ % (lang, val_col, rca_col, prod_class, country1.id, year_where)

  """Prepare JSON response"""
  json_response = {}
  
  """Check cache"""
  if settings.REDIS:
    raw = get_redis_connection('default')
    key = "%s:%s:%s:%s:%s" % (country1.name_3char, "show", "all", prod_class, trade_flow)
    # See if this key is already in the cache
    cache_query = raw.hget(key, 'data')
    if (cache_query == None):
      rows = raw_q(query=q, params=None)
  
      #article = "to" if trade_flow == "export" else "from"
  
      total_val = sum([r[4] for r in rows])
      """Add percentage value to return vals"""
      rows = [{"year":r[0], "item_id":r[1], "abbrv":r[2], "name":r[3], "value":r[4], "rca":r[5], "share": (r[4] / total_val)*100} for r in rows]
  
      if crawler == "":
        return [rows, total_val, ["#", "Year", "Abbrv", "Name", "Value", "RCA", "%"]]  
        
      json_response["data"] = rows
        
      # SAVE key in cache.
      raw.hset(key, 'data', msgpack.dumps(rows))
  
    else:
      # If already cached, now simply retrieve
      encoded = cache_query
      decoded = msgpack.loads(encoded)
      json_response["data"] = decoded
  
  else:
    rows = raw_q(query=q, params=None)
    total_val = sum([r[6] for r in rows])
  
    """Add percentage value to return vals"""
    # rows = [list(r) + [(r[4] / total_val)*100] for r in rows]
    rows = [{"year":r[0], "item_id":r[1], "abbrv":r[2], "name":r[3], "value":r[6], "rca":r[7], "share": (r[6] / total_val)*100,
             "id":r[1], "region_id":r[4], "continent":r[5]} for r in rows]
  
    if crawler == "":
      return [rows, total_val, ["#", "Year", "Abbrv", "Name", "Value", "RCA", "%"]]
      
    json_response["data"] = rows
    
  
  """Set article variable for question """
  article = "to" if trade_flow == "export" else "from"
  
  json_response["attr_data"] = Country.objects.get_all(lang)
  json_response["country1"] = country1.to_json()
  json_response["title"] = "Where does %s %s %s?" % (country1.name, trade_flow, article)
  json_response["year"] = year
  json_response["item_type"] = "country"
  json_response["app_type"] = "csay"
  json_response["region"]= region
  json_response["continents"]= continents
  json_response["class"] =  prod_class
  json_response["other"] = query_params
    
  """Return to browser as JSON for AJAX request"""
  return HttpResponse(json.dumps(json_response))

def api_ccsy(request, trade_flow, country1, country2, year):
  # import time
  # start = time.time()
  '''Init variables'''
  prod_class = request.session['product_classification'] if 'product_classification' in request.session else "hs4"
  prod_class = request.GET.get("prod_class", prod_class)
  lang = request.session['django_language'] if 'django_language' in request.session else "en"
  lang = request.GET.get("lang", lang)
  crawler = request.GET.get("_escaped_fragment_", False)
  country1 = Country.objects.get(name_3char=country1)
  country2 = Country.objects.get(name_3char=country2)
  article = "to" if trade_flow == "export" else "from"
  
  '''Set query params with our changes'''
  query_params = request.GET.copy()
  query_params["lang"] = lang
  query_params["product_classification"] = prod_class
  # Get Name in proper lang
  name = "name_%s" % lang
  
  '''Grab extraneous details'''
  if prod_class == "sitc4":
    # attr_list = list(Sitc4.objects.all().values('code','name','color'))
    attr_list = list(Sitc4.objects.all().values('code',name,'id','color'))
    attr = {}
    for i in attr_list: 
      attr[i['code']] = {'code':i['code'],'name':i[name],'color':i['color']}
     #.extra(where=['CHAR_LENGTH(code) = 2'])
  elif prod_class == "hs4":
    # attr_list = list(Hs4.objects.all().values('code','name')) #.extra(where=['CHAR_LENGTH(code) = 2'])
    attr_list = list(Hs4.objects.all().values('code',name,'id','community_id__color'))
    attr = {}
    for i in attr_list: 
      attr[i['code']] = {'code':i['code'],'name':i[name],'item_id':i['id'],'color':i['community_id__color']}

  
  
  '''Define parameters for query'''
  year_where = "AND year = %s" % (year,) if crawler == "" else " "
  rca_col = "null"
  if trade_flow == "net_export":
    val_col = "(export_value - import_value) as val"
  elif trade_flow == "net_import":
    val_col = "(import_value - export_value) as val"
  elif trade_flow == "export":
    val_col = "export_value as val"
  else:
    val_col = "import_value as val"
    
  '''Create query'''
  q = """
    SELECT year, p.id, p.code, p.name_%s, p.community_id, c.name, c.color, %s, %s
    FROM observatory_%s_ccpy as ccpy, observatory_%s as p, observatory_%s_community as c 
    WHERE origin_id=%s and destination_id=%s and ccpy.product_id = p.id and p.community_id = c.id %s
    HAVING val > 0
    ORDER BY val DESC
    """ % (lang, val_col, rca_col, prod_class, prod_class, prod_class, country1.id, country2.id, year_where)
  
  """Prepare JSON response"""
  json_response = {}
  
  """Check cache"""
  if settings.REDIS:  
    raw = get_redis_connection('default')
    key = "%s:%s:%s:%s:%s" % (country1.name_3char, country2.name_3char, "show", prod_class, trade_flow)
    # See if this key is already in the cache
    cache_query = raw.hget(key, 'data')
    if(cache_query == None):    
      rows = raw_q(query=q, params=None)
      total_val = sum([r[4] for r in rows])
      """Add percentage value to return vals"""
      rows = [{"year":r[0], "item_id":r[1], "abbrv":r[2], "name":r[3], "value":r[4], "rca":r[5], "share": (r[4] / total_val)*100} for r in rows]
  
      if crawler == "":
        return [rows, total_val, ["#", "Year", "Abbrv", "Name", "Value", "RCA", "%"]]
        
      json_response["data"] = rows  
        
      # SAVE key in cache.
      raw.hset(key, 'data', msgpack.dumps(rows))
    
    else: 
      # If already cached, now simply retrieve
      encoded = cache_query
      decoded = msgpack.loads(encoded)
      json_response["data"] = decoded
    
  else:
    rows = raw_q(query=q, params=None)
    total_val = sum([r[7] for r in rows])
  
    """Add percentage value to return vals"""
    # rows = [list(r) + [(r[4] / total_val)*100] for r in rows]
    rows = [{"year":r[0], "item_id":r[1], "abbrv":r[2], "name":r[3], "value":r[7], "rca":r[5], 
             "share": (r[7] / total_val)*100,
             "community_id":r[4],"community_name":r[5],"color":r[6], "code":r[2], "id": r[2]} for r in rows]
  
    if crawler == "":
      return [rows, total_val, ["#", "Year", "Abbrv", "Name", "Value", "RCA", "%"]]
      
    json_response["data"] = rows
  
  json_response["attr_data"] = Sitc4.objects.get_all(lang) if prod_class == "sitc4" else Hs4.objects.get_all(lang)
  json_response["country1"] = country1.to_json()
  json_response["country2"] = country2.to_json()
  json_response["title"] = "What does %s %s %s %s?" % (country1.name, trade_flow, article, country2.name)
  json_response["year"] = year
  json_response["item_type"] = "product"
  json_response["app_type"] = "ccsy"
  json_response["prod_class"] =  prod_class
  json_response["attr"] = attr
  json_response["class"] =  prod_class
  json_response["other"] = query_params

  """Return to browser as JSON for AJAX request"""
  return HttpResponse(json.dumps(json_response))

def api_cspy(request, trade_flow, country1, product, year):
  '''Init variables'''
  prod_class = request.session['product_classification'] if 'product_classification' in request.session else "hs4"
  prod_class = request.GET.get("prod_class", prod_class)
  lang = request.session['django_language'] if 'django_language' in request.session else "en"
  lang = request.GET.get("lang", lang)
  crawler = request.GET.get("_escaped_fragment_", False)
  country1 = Country.objects.get(name_3char=country1)
  product = clean_product(product, prod_class)
  article = "to" if trade_flow == "export" else "from"
  
  '''Set query params with our changes'''
  query_params = request.GET.copy()
  query_params["lang"] = lang
  query_params["product_classification"] = prod_class
  
  '''Grab extraneous details'''
  region_list = list(Country_region.objects.all().values()) #.extra(where=['CHAR_LENGTH(code) = 2'])
  region = {}
  for i in region_list: 
    region[i['id']] = i
    
  continent_list = list(Country.objects.all().distinct().values('continent'))
  continents = {}
  for i,k in enumerate(continent_list): 
     continents[k['continent']] = i*1000
  
  '''Define parameters for query'''
  year_where = "AND year = %s" % (year,) if crawler == "" else " "
  rca_col = "null"
  if trade_flow == "net_export":
    val_col = "(export_value - import_value) as val"
  elif trade_flow == "net_import":
    val_col = "(import_value - export_value) as val"
  elif trade_flow == "export":
    val_col = "export_value as val"
  else:
    val_col = "import_value as val"
    
  '''Create query'''
  q = """
    SELECT year, c.id, c.name_3char, c.name_%s, c.region_id, c.continent, %s, %s 
    FROM observatory_%s_ccpy as ccpy, observatory_country as c 
    WHERE origin_id=%s and ccpy.product_id=%s and ccpy.destination_id = c.id %s
    GROUP BY year, destination_id
    HAVING val > 0
    ORDER BY val DESC
    """ % (lang, val_col, rca_col, prod_class, country1.id, product.id, year_where)
  
  """Prepare JSON response"""
  json_response = {}
  
  """Check cache"""
  if settings.REDIS:
    raw = get_redis_connection('default')
    key = "%s:%s:%s:%s:%s" % (country1.name_3char, "show", product.id,  prod_class, trade_flow)
    # See if this key is already in the cache
    cache_query = raw.hget(key, 'data')
    if (cache_query == None):
      rows = raw_q(query=q, params=None)
      total_val = sum([r[6] for r in rows])
      """Add percentage value to return vals"""
      #rows = [{"year":r[0], "item_id":r[1], "abbrv":r[2], "name":r[3], "value":r[6], "rca":r[7], "share": (r[6] / total_val)*100} for r in rows]
      rows = [{"year":r[0], "item_id":r[1], "abbrv":r[2], "name":r[3], "value":r[6], "rca":r[7], "share": (r[6] / total_val)*100,
               "region_id": r[4], "continent": r[5], "id":r[1]} for r in rows]
               
      if crawler == "":
        return [rows, total_val, ["#", "Year", "Abbrv", "Name", "Value", "RCA", "%"]] 
      
      json_response["data"] = rows
         
      # SAVE key in cache.
      raw.hset(key, 'data', msgpack.dumps(rows))
    
    else:
      # If already cached, now simply retrieve
      encoded = cache_query
      decoded = msgpack.loads(encoded)
      json_response["data"] = decoded
  
  else:
    rows = raw_q(query=q, params=None)
    total_val = sum([r[6] for r in rows])
  
    """Add percentage value to return vals"""
    # rows = [list(r) + [(r[4] / total_val)*100] for r in rows]
    rows = [{"year":r[0], "item_id":r[1], "abbrv":r[2], "name":r[3], "value":r[6], "rca":r[7], "share": (r[6] / total_val)*100,
             "region_id": r[4], "continent": r[5], "id":r[1]} for r in rows]
  
    if crawler == "":
      return [rows, total_val, ["#", "Year", "Abbrv", "Name", "Value", "RCA", "%"]]
      
    json_response["data"] = rows
  
  
  article = "to" if trade_flow == "export" else "from"
  
  json_response["attr_data"] = Country.objects.get_all(lang)
  json_response["title"] = "Where does %s %s %s %s?" % (country1.name, trade_flow, product.name_en, article)
  json_response["country1"] = country1.to_json()
  json_response["product"] = product.to_json()
  json_response["year"] = year
  json_response["item_type"] = "country"
  json_response["continents"]= continents
  json_response["region"]= region
  json_response["app_type"] = "cspy"
  json_response["class"] =  prod_class
  json_response["other"] = query_params
  
  '''Return to browser as JSON for AJAX request'''
  return HttpResponse(json.dumps(json_response))

# Embed for iframe
def embed(request, app_name, trade_flow, country1, country2, product, year):
  lang = request.GET.get("lang", "en")
  prod_class = request.session['product_classification'] if 'product_classification' in request.session else "hs4"
  prod_class = request.GET.get("product_classification", prod_class)
  query_string = request.GET.copy()
  query_string["product_classification"] = prod_class
  # get distince years from db, different for diff product classifications
  years_available = list(Sitc4_cpy.objects.values_list("year", flat=True).distinct()) if prod_class == "sitc4" else list(Hs4_cpy.objects.values_list("year", flat=True).distinct())
  years_available.sort()
  
  return render_to_response("explore/embed.html", {"app":app_name, "trade_flow": trade_flow, "country1":country1, "country2":country2, "product":product, "year":year, "other":json.dumps(query_string),"years_available":json.dumps(years_available), "lang":lang})






###################
## Abandoned function? Coresponding model/tables 'wdi' & 'wdi_cwy' 
###################
def get_similar_productive(country, year):
  # correlation = request.GET.get("c", "pearson")
  import math
  from scipy.stats.stats import pearsonr as cor_func
  # if correlation == "pearson":
  #   from scipy.stats.stats import pearsonr as cor_func
  # else:
  #   from scipy.stats.stats import spearmanr as cor_func
  y = year
  c = country
  country_lookup = get_country_lookup()
  prods = list(Sitc4.objects.filter(ps_size__isnull=False).values_list("id", flat=True))
  cpys = Sitc4_cpy.objects.filter(year=y, export_rca__isnull=False, export_rca__gt=0).values_list("country", "product", "export_rca")
  country_vectors = {}
  for cpy in cpys:
    if cpy[0] not in country_vectors:
      country_vectors[cpy[0]] = [0] * len(prods)
    try:
      prod_pos = prods.index(cpy[1])
      country_vectors[cpy[0]][prod_pos] = math.log(cpy[2]+0.1, 10)
    except:
      pass
  cors = []
  for this_c, rcas in country_vectors.items():
    # raise Exception(rcas, country_vectors[c.id])
    cors.append([country_lookup[this_c][0], country_lookup[this_c][1], cor_func(country_vectors[c.id], rcas)[0]])
    # raise Exception(cors)
  cors.sort(key=lambda x: x[2], reverse=True)
  return cors
  # raise Exception(cors)
  # raise Exception(cor_func(country_vectors[50], country_vectors[105]))
  return render_to_response("explore/similar.html", {"cors": cors})

###################
## Abandoned function? Coresponding model/tables 'wdi' & 'wdi_cwy' 
###################
def similar_wdi(request, country, indicator, year):
  y = int(year)
  c = clean_country(country)
  if indicator == "0":
    this_index = 0
    name = "Productive strucuture correlation"
    values = get_similar_productive(c, y)
  else:
    i = Wdi.objects.get(pk=indicator)
    this_wdi = wdis = Wdi_cwy.objects.get(year=y, wdi=i, country=c)
    wdis = Wdi_cwy.objects.filter(year=y, wdi=i, country__region__isnull=False).order_by("-value")
    this_index = list(wdis).index(this_wdi)
    values = list(wdis.values_list("country__name_en", "country__name_3char", "value"))
    name = i.name
  return HttpResponse(json.dumps({"index": this_index, "values":values, "wdi": name}))



###############################################################################
## Helpers
###############################################################################
def clean_country(country):
  # first try looking up based on 3 character code
  try:
    c = Country.objects.get(name_3char=country)
  except Country.DoesNotExist:
    # next try 2 character code
    try:
      c = Country.objects.get(name_2char=country)
    except Country.DoesNotExist:
      c = None
  return c

def clean_product(product, prod_class):
  # first try looking up based on 3 character code
  if prod_class == "hs4":
    try:
      p = Hs4.objects.get(code=product)
    except Hs4.DoesNotExist:
      # next try SITC4
      try:
        conv_code = Sitc4.objects.get(code=product).conversion_code
        p = Hs4.objects.get(code=conv_code)
      except Hs4.DoesNotExist:
        p = None
  else:
    try:
      p = Sitc4.objects.get(code=product)
    except Sitc4.DoesNotExist:
      # next try SITC4
      try:
        conv_code = Hs4.objects.get(code=product).conversion_code
        p = Sitc4.objects.get(code=conv_code)
      except Hs4.DoesNotExist:
        p = None
  return p

def get_country_lookup():
  lookup = {}
  for c in Country.objects.all():
    lookup[c.id] = [c.name_en, c.name_3char]
  return lookup

def get_app_type(country1, country2, product, year):
  # country / all / show / year
  if country2 == "all" and product == "show":
    return "casy"
  
  # country / show / all / year
  elif country2 == "show" and product == "all":
    return "csay"
  
  # show / all / product / year
  elif country1 == "show" and country2 == "all":
    return "sapy"
  
  # country / country / show / year
  elif product == "show":
    return "ccsy"
  
  #  country / show / product / year
  else:
    return "cspy"
